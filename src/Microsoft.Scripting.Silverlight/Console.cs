using System;
using System.Collections.Generic;
using System.Text;
using System.Windows.Browser;
using System.IO;
using Microsoft.Scripting.Hosting;

namespace Microsoft.Scripting.Silverlight {
    class Console {
        
        #region Console Html Template
        const string _sdlr =       "silverlightDlrConsole";
        const string _sdlrCode =   "silverlightDlrConsoleCode";
        const string _sdlrPrompt = "silverlightDlrConsolePrompt";
        const string _sdlrLine =   "silverlightDlrConsoleLine";
        const string _sdlrResult = "silverlightDlrConsoleResult";

        static string _ConsoleHtmlTemplate = string.Format(@"
<div id=""{0}""> 
  <div id=""{1}""></div> 
  <span id=""{2}"" class=""{2}""></span><form id=""{3}"" action=""javascript:void(0)""><input type=""text"" id=""{4}"" /><input type=""submit"" id=""{5}"" value=""Run"" /></form>
</div>", _sdlr, _sdlrResult, _sdlrPrompt, "SilverlightDlrConsoleRunForm", _sdlrCode, "silverlightDlrConsoleRun");
        
        #endregion

        #region Private instance variables
        private string           _code;
        private bool             _multiLine;
        private bool             _multiLinePrompt;
        private bool             _multiLineComplete;
        private List<string>     _history;
        private int              _currentCommand = -1;
        private static Console   _current;
        private HtmlElement      _silverlightDlrConsoleCode;
        private HtmlElement      _silverlightDlrConsoleResult;
        private HtmlElement      _silverlightDlrConsolePrompt;
        #endregion

        #region Console management
        /// <summary>
        /// Creates a console and inserts it into the page.
        /// </summary>
        public static void Show() {
            var div = HtmlPage.Document.CreateElement("div");
            div.SetProperty("innerHTML", _ConsoleHtmlTemplate);
            HtmlPage.Document.Body.AppendChild(div);
            if (_current == null) {
                _current = new Console();
            }
            _current.Start();
        }

        Console() {
            _silverlightDlrConsoleCode   = HtmlPage.Document.GetElementById(_sdlrCode);
            _silverlightDlrConsoleResult = HtmlPage.Document.GetElementById(_sdlrResult);
            _silverlightDlrConsolePrompt = HtmlPage.Document.GetElementById(_sdlrPrompt);
        }

        void Start() {
            ShowDefaults();
            ShowPrompt();
            _silverlightDlrConsoleCode.AttachEvent("onkeypress", new EventHandler<HtmlEventArgs>(OnKeyPress));
        }

        void OnKeyPress(object sender, HtmlEventArgs args) {
            switch(args.CharacterCode) {
            case 13:
                RunCode(args.CtrlKey);
                break;
            case 38:
                ShowPreviousCommand();
                break;
            case 40:
                if (!args.ShiftKey) {
                    ShowNextCommand();
                }
                break;
            };
        }

        void Remember(string line) {
            if (_history == null) {
                _history = new List<string>();
            }
            _history.Add(line);
        }

        void Reset() {
            _code = null;
            _multiLine = false;
            _multiLinePrompt = false;
            _multiLineComplete = false;
        }
        #endregion

        #region History
        int CurrentCommand {
            get {
                if (_history == null) {
                    _currentCommand = -1;
                } else if(_currentCommand == -1) {
                    _currentCommand = _history.Count != 0 ? _history.Count - 1 : 0;
                }
                return _currentCommand;
            }
            set {
                if (_history == null) {
                    _currentCommand = -1;
                } else if (value < 0) {
                    _currentCommand = 0;
                } else if (value > _history.Count - 1) {
                    _currentCommand = _history.Count - 1;
                } else {
                    _currentCommand = value;
                }
            }
        }

        string TryGetFromHistory(int index) {
            if (_history == null)
                return "";
            return _history[index];
        }

        string GetNextCommand() {
            CurrentCommand++;
            return TryGetFromHistory(CurrentCommand); 
        }

        string GetPreviousCommand() {
            --CurrentCommand;
            return TryGetFromHistory(CurrentCommand);
        }
        #endregion

        #region Running Code
        string TryExpression(string text) {
            var props = DynamicApplication.Current.Engine.CreateScriptSourceFromString(
                text, SourceCodeKind.Expression
            ).GetCodeProperties();
            string result;
            if (props == ScriptCodeParseResult.Complete || props == ScriptCodeParseResult.Empty) {
                result = text;
            } else {
                result = null;
            }
            return result;
        }
   
        void RunCode(bool forceExecute) {
            var line = _silverlightDlrConsoleCode.GetProperty("value").ToString();
            if (line != string.Empty) {
                _code = (_code == null || _code == string.Empty ? "" : _code + "\n") + line;
            }
            object result = (_code.Split('\n').Length > 1) ? DoMultiLine(forceExecute) : DoSingleLine(forceExecute);

            ShowLineAndResult(line, result);
        }

        object DoSingleLine(bool forceExecute) {
            var valid = TryExpression(_code);
            if (valid != null) {
                var source = DynamicApplication.Current.Engine.CreateScriptSourceFromString(_code, SourceCodeKind.Expression);
                return ExecuteCode(source);
            } else {
                DoMultiLine(forceExecute);
            }
            return null;
        }

        object DoMultiLine(bool forceExecute) {
            if (forceExecute || IsComplete(_code, false)) {
                _multiLineComplete = true;
                var source = DynamicApplication.Current.Engine.CreateScriptSourceFromString(_code, SourceCodeKind.InteractiveCode);
                return ExecuteCode(source);
            } else {
                _multiLine = true;
                _multiLineComplete = false;
            }
            return null;
        }

        object ExecuteCode(ScriptSource source) {
            object result;
            try {
                result = source.Compile(new ErrorFormatter.Sink()).Execute();
            } catch (Exception e) {
                result = HandleException(e);
            }
            return result;
        }

        string HandleException(Exception e) {
            return string.Format(@"<div>{0}</div>", e.Message);
        }

        bool IsComplete(string text, bool allowIncomplete) {
            var props = DynamicApplication.Current.Engine.CreateScriptSourceFromString(
                text, SourceCodeKind.InteractiveCode
            ).GetCodeProperties();
            var result = (props != ScriptCodeParseResult.Invalid) &&
                (props != ScriptCodeParseResult.IncompleteToken) &&
                (allowIncomplete || (props != ScriptCodeParseResult.IncompleteStatement));
            return result;
        }
        #endregion

        #region Rendering
        private void ShowLineAndResult(string line, object result) {
            Remember(line);
            ShowLineInResultDiv(line);

            if (!_multiLine || _multiLineComplete) {
                ShowValueInResultDiv(result);
                ShowPrompt();
                Reset();
            } else {
                ShowSubPrompt();
            }

            ShowDefaults();
        }

        void ShowSubPrompt() {
            _silverlightDlrConsolePrompt.SetProperty("innerHTML", SubPromptHtml());
        }

        void ShowPrompt() {
            _silverlightDlrConsolePrompt.SetProperty("innerHTML", PromptHtml());
        }

        void ShowLineInResultDiv(string line) {
            ShowPromptInResultDiv();
            var lineDiv = HtmlPage.Document.CreateElement("div");
            lineDiv.CssClass = _sdlrLine;
            lineDiv.SetProperty("innerHTML", line.Replace(" ", "&nbsp;"));
            _silverlightDlrConsoleResult.AppendChild(lineDiv);
        }

        void ShowValueInResultDiv(object result) {
            var resultDiv = HtmlPage.Document.CreateElement("div");
            resultDiv.SetProperty("innerHTML", result != null ? result.ToString() : "nil");
            _silverlightDlrConsoleResult.AppendChild(resultDiv);
        }
  
        void ShowPromptInResultDiv() {
            HtmlElement prompt = HtmlPage.Document.CreateElement("span");
            prompt.SetAttribute("class", _sdlrPrompt);
            prompt.SetProperty("innerHTML", _multiLinePrompt ? SubPromptHtml() : PromptHtml());
            _silverlightDlrConsoleResult.AppendChild(prompt);
            if (_multiLine)
                _multiLinePrompt = true;
        }

        string PromptHtml() {
            return String.Format(
                "{0}&gt;&nbsp;",
                Path.GetExtension(DynamicApplication.Current.EntryPoint).Substring(1)
            );
        }

        string SubPromptHtml() {
            return "&nbsp;&nbsp;|&nbsp;";
        }
    
        void ShowDefaults() {
            _silverlightDlrConsoleCode.SetProperty("value", "");
            _silverlightDlrConsolePrompt.Focus();
            _silverlightDlrConsoleCode.Focus();
        }

        void ShowNextCommand() {
            _silverlightDlrConsoleCode.SetProperty("value", GetNextCommand());
        }

        void ShowPreviousCommand() {
            _silverlightDlrConsoleCode.SetProperty("value", GetPreviousCommand());
        }
        #endregion
    }
}