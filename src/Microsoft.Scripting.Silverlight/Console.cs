using System;
using System.Collections.Generic;
using System.Text;
using System.Windows.Browser;
using System.IO;
using Microsoft.Scripting.Hosting;

namespace Microsoft.Scripting.Silverlight {
    class Console {
        
        #region Console Html Template
        static string _ConsoleHtmlTemplate = @"
<div id=""silverlightDlrConsole""> 
  <div id=""silverlightDlrConsoleResult""></div> 
  <span id=""silverlightDlrConsolePrompt"" class=""silverlightDlrConsolePrompt""></span><form id=""SilverlightDlrConsoleRunForm"" action=""javascript:void(0)""><textarea type=""text"" rows=""1"" id=""silverlightDlrConsoleCode""></textarea><input type=""submit"" id=""silverlightDlrConsoleRun"" value=""Run"" /></form> <!-- return submitenter(this, event) --> 
</div>";
        private const string _sdlrCode = "silverlightDlrConsoleCode";
        private const string _sdlrPrompt = "silverlightDlrConsolePrompt";
        private const string _sdlrLine = "silverlightDlrConsoleLine";
        private const string _sdlrResult = "silverlightDlrConsoleResult";
        private const string _sdlrExpression = "silverlightDlrConsoleExpression";
        #endregion

        #region Private instance variables
        private string _code;
        private bool _multiLine;
        private bool _multiLinePrompt;
        private List<string> _history;
        private HtmlDocument Doc = HtmlPage.Document;
        private static Console _current;
        private HtmlElement _silverlightDlrConsoleCode;
        private HtmlElement _silverlightDlrConsoleResult;
        private HtmlElement _silverlightDlrConsolePrompt;
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
            _silverlightDlrConsoleCode = HtmlPage.Document.GetElementById(_sdlrCode);
            _silverlightDlrConsoleResult = HtmlPage.Document.GetElementById(_sdlrResult);
            _silverlightDlrConsolePrompt = HtmlPage.Document.GetElementById(_sdlrPrompt);
        }

        void Start() {
            ShowDefaults();
            _silverlightDlrConsoleCode.AttachEvent("onkeypress", new EventHandler<HtmlEventArgs>(OnKeyPress));
            _silverlightDlrConsoleCode.AttachEvent("onfocus", new EventHandler<HtmlEventArgs>(OnFocus));
        }

        void OnKeyPress(object sender, HtmlEventArgs args) {
            switch(args.CharacterCode) {
            case 13:
                RunCode();
                break;
            case 38:
                break;
            case 40:
                break;
            };
        }

        void OnFocus(object sender, HtmlEventArgs args) {
            if (!_multiLine) {
                string value = Doc.GetElementById(_sdlrCode).GetProperty("value").ToString().Trim('\n');
                HtmlPage.Window.Eval(string.Format("document.getElementById('silverlightDlrConsoleCode').value = \"{0}\"", value));
            }
        }

        void Remember() {
            if (_history == null) {
                _history = new List<string>();
            }
            _history.Add(_code);
        }

        void Reset() {
            _code = null;
            _multiLine = false;
            _multiLinePrompt = false;
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
   
        void RunCode() {
            _code = _silverlightDlrConsoleCode.GetProperty("value").ToString().Trim('\n');
            if(_code.Split('\n').Length > 1) {
                DoMultiLine();
            } else {
                DoSingleLine();
            }
        }

        void DoSingleLine() {
            var valid = TryExpression(_code);
            if (valid != null) {
                var source = DynamicApplication.Current.Engine.CreateScriptSourceFromString(_code, SourceCodeKind.Expression);
                ExecuteCode(source);
            } else {
                DoMultiLine();
            }
        }

        void DoMultiLine() {
            if (IsComplete(_code, false)) {
                var source = DynamicApplication.Current.Engine.CreateScriptSourceFromString(_code, SourceCodeKind.InteractiveCode);
                ExecuteCode(source);
            } else {
                _multiLine = true;
                string height = _silverlightDlrConsoleCode.GetStyleAttribute("height");
                if(height == String.Empty)
                    height = _silverlightDlrConsoleCode.GetProperty("height").ToString();
                height = height.ToString().TrimEnd('p', 'x');
                _silverlightDlrConsoleCode.SetStyleAttribute("height", (Int32.Parse(height) + 20).ToString() + "px");
                ShowPrompt();
                _silverlightDlrConsolePrompt.SetProperty("innerHTML", SubPromptHtml());
            }
        }

        void ExecuteCode(ScriptSource source) {
            object result;
            try {
                result = source.Compile(new ErrorFormatter.Sink()).Execute();
            } catch (Exception e) {
                result = HandleException(e);
            }
            ShowPrompt();
            ShowResult(_code, result);
            ShowDefaults();
            Remember();
            Reset();
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
        void ShowResult(string code, object result) {
            var lines = code.Split('\n');
            var codeDivs = "";
            foreach (string line in lines) {
                codeDivs = codeDivs + string.Format(@"<div class=""{0}"">{1}</div>", _sdlrLine, line.Replace(" ", "&nbsp;"));
            }
            var output = "";
            if (code == null || code.Length == 0) {
                output = "<br />";
            } else {
                // TODO: Delegate to the language to format the result
                output = string.Format(
                    @"<div class=""{0}"">{1}</div><div>{2}</div>",
                    _sdlrExpression, codeDivs, result != null ? result.ToString() : "nil"
                );
            }
            Doc.GetElementById(_sdlrResult).SetProperty(
                "innerHTML", 
                Doc.GetElementById(_sdlrResult).GetProperty("innerHTML") + output
            );
        }
  
        void ShowPrompt() {
            HtmlElement prompt = HtmlPage.Document.CreateElement("div");
            prompt.SetAttribute("class", _sdlrPrompt);
            prompt.SetProperty("innerHTML", _multiLinePrompt ? SubPromptHtml() : PromptHtml());
            Doc.GetElementById(_sdlrResult).AppendChild(prompt);
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
            _silverlightDlrConsolePrompt.SetProperty("innerHTML", PromptHtml());
            _silverlightDlrConsoleCode.SetStyleAttribute("height", "20px");
            _silverlightDlrConsoleCode.SetProperty("rows", "1");
        }
        #endregion
    }
}