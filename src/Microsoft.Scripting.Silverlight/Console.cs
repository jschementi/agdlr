using System;
using System.Collections.Generic;
using System.Text;
using System.Windows.Browser;
using System.IO;
using Microsoft.Scripting.Hosting;

namespace Microsoft.Scripting.Silverlight {
    public class Console {
        
        #region Console Html Template
        private const string _sdlr        = "silverlightDlrConsole";
        private const string _sdlrCode    = "silverlightDlrConsoleCode";
        private const string _sdlrPrompt  = "silverlightDlrConsolePrompt";
        private const string _sdlrLine    = "silverlightDlrConsoleLine";
        private const string _sdlrOutput  = "silverlightDlrConsoleOutput";
        private const string _sdlrValue   = "silverlightDlrConsoleValue";
        private const string _sdlrResult  = "silverlightDlrConsoleResult";
        private const string _sdlrRunForm = "silverlightDlrConsoleRunForm";
        private const string _sdlrRun     = "silverlightDlrConsoleRun";

        private static string _ConsoleHtmlTemplate = string.Format(@"
<div id=""{0}""> 
  <div id=""{1}""></div> 
  <span id=""{2}"" class=""{2}""></span><form id=""{3}"" action=""javascript:void(0)""><input type=""text"" id=""{4}"" /><input type=""submit"" id=""{5}"" value=""Run"" /></form>
</div>", _sdlr, _sdlrResult, _sdlrPrompt, _sdlrRunForm, _sdlrCode, _sdlrRun);
        #endregion

        #region Private fields
        private string              _code;
        private bool                _multiLine;
        private bool                _multiLinePrompt;
        private bool                _multiLineComplete;
        private List<string>        _history;
        private int                 _currentCommand = -1;
        private static Console      _current;
        private ConsoleOutputBuffer _outputBuffer;
        private ConsoleInputBuffer  _inputBuffer;
        private HtmlElement         _silverlightDlrConsoleCode;
        private HtmlElement         _silverlightDlrConsoleResult;
        private HtmlElement         _silverlightDlrConsolePrompt;
        private ScriptEngine        _engine;
        #endregion

        #region Public properties
        public ConsoleInputBuffer InputBuffer {
            get { return _inputBuffer; }
        }

        public ConsoleOutputBuffer OutputBuffer {
            get { return _outputBuffer; }
        }

        public static Console Current {
            get { return _current; }
        }
        #endregion

        #region Console management
        /// <summary>
        /// Creates a console and inserts it into the page.
        /// </summary>
        public static void Show() {
            Show(DynamicApplication.Current.Engine);
        }

        public static void Show(ScriptEngine engine) {
            if (_current == null) {
                var div = HtmlPage.Document.CreateElement("div");
                div.SetProperty("innerHTML", _ConsoleHtmlTemplate);
                HtmlPage.Document.Body.AppendChild(div);
                _current = new Console(engine);
                _current.Start();
            }
        }

        private Console(ScriptEngine engine) {
            _silverlightDlrConsoleCode   = HtmlPage.Document.GetElementById(_sdlrCode);
            _silverlightDlrConsoleResult = HtmlPage.Document.GetElementById(_sdlrResult);
            _silverlightDlrConsolePrompt = HtmlPage.Document.GetElementById(_sdlrPrompt);
            _engine = engine;
        }

        private void Start() {
            _inputBuffer = new ConsoleInputBuffer(_current);
            _outputBuffer = new ConsoleOutputBuffer(_silverlightDlrConsoleResult, _sdlrOutput);
            ShowDefaults();
            ShowPrompt();
            _silverlightDlrConsoleCode.AttachEvent("onkeypress", new EventHandler<HtmlEventArgs>(OnKeyPress));
        }

        private void OnKeyPress(object sender, HtmlEventArgs args) {
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
            default:
                _currentCommand = _history.Count;
                break;
            };
        }

        private void Remember(string line) {
            if (_history == null) {
                _history = new List<string>();
            }
            _history.Add(line);
        }

        private void Reset() {
            _code = null;
            _multiLine = false;
            _multiLinePrompt = false;
            _multiLineComplete = false;
        }
        #endregion

        #region History
        private int CurrentCommand {
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

        private string TryGetFromHistory(int index) {
            if (_history == null)
                return "";
            return _history[index];
        }

        public string GetNextCommand() {
            CurrentCommand++;
            return TryGetFromHistory(CurrentCommand); 
        }

        public string GetPreviousCommand() {
            --CurrentCommand;
            return TryGetFromHistory(CurrentCommand);
        }
        #endregion

        #region Running Code
        public string TryExpression(string text) {
            var props = _engine.CreateScriptSourceFromString(
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

        public void RunCode() {
            RunCode(false);
        }
        public void RunCode(bool forceExecute) {
            var line = _silverlightDlrConsoleCode.GetProperty("value").ToString();
            if (line != string.Empty) {
                _code = (_code == null || _code == string.Empty ? "" : _code + "\n") + line;
            }
            if (_code != null) {
                object result = (_code.Split('\n').Length > 1) ? DoMultiLine(forceExecute) : DoSingleLine(forceExecute);

                ShowLineAndResult(line, result);
            }
        }

        private object DoSingleLine(bool forceExecute) {
            var valid = TryExpression(_code);
            if (valid != null) {
                var source = _engine.CreateScriptSourceFromString(_code, SourceCodeKind.Expression);
                return ExecuteCode(source);
            } else {
                DoMultiLine(forceExecute);
            }
            return null;
        }

        private object DoMultiLine(bool forceExecute) {
            if (forceExecute || IsComplete(_code, false)) {
                _multiLineComplete = true;
                var source = _engine.CreateScriptSourceFromString(_code, SourceCodeKind.InteractiveCode);
                return ExecuteCode(source);
            } else {
                _multiLine = true;
                _multiLineComplete = false;
            }
            return null;
        }

        public object ExecuteCode(ScriptSource source) {
            object result;
            try {
                result = source.Compile(new ErrorFormatter.Sink()).Execute();
            } catch (Exception e) {
                HandleException(e);
                result = null;
            }
            return result;
        }

        private void HandleException(Exception e) {
            var de = new ErrorFormatter.DynamicExceptionInfo(e);
            
            _outputBuffer.WriteLine("");
            _outputBuffer.WriteLine(de.Message);

            foreach(var frame in de.DynamicStackFrames) {
                _outputBuffer.WriteLine("  at {0} in {1}, line {2}",
                    frame.GetMethodName(),
                    frame.GetFileName() != null ? frame.GetFileName() : null,
                    frame.GetFileLineNumber()
                );
            }

            _outputBuffer.WriteLine("CLR Stack Trace:");
            _outputBuffer.WriteLine(e.StackTrace != null ? e.StackTrace : e.ToString());
        }

        public bool IsComplete(string text, bool allowIncomplete) {
            var props = _engine.CreateScriptSourceFromString(
                text, SourceCodeKind.InteractiveCode
            ).GetCodeProperties();
            var result = (props != ScriptCodeParseResult.Invalid) &&
                (props != ScriptCodeParseResult.IncompleteToken) &&
                (allowIncomplete || (props != ScriptCodeParseResult.IncompleteStatement));
            return result;
        }
        #endregion

        #region Rendering
        internal void ShowLineAndResult(string line, object result) {
            Remember(line);
            ShowCodeLineInResultDiv(line);

            if (!_multiLine || _multiLineComplete) {
                FlushOutputInResultDiv();
                ShowValueInResultDiv(result);
                ShowPrompt();
                Reset();
            } else {
                ShowSubPrompt();
            }

            ShowDefaults();
        }

        internal void ShowDefaults() {
            _silverlightDlrConsoleCode.SetProperty("value", "");
            _silverlightDlrConsolePrompt.Focus();
            _silverlightDlrConsoleCode.Focus();
        }

        #region Code input
        public void AppendCode(string str) {
            string toPrepend = HtmlPage.Document.GetElementById(_sdlrCode).GetProperty("value").ToString();
            HtmlPage.Document.GetElementById(_sdlrCode).SetProperty("value", toPrepend + str);
        }
        #endregion

        #region Prompt
        internal void ShowSubPrompt() {
            _outputBuffer.PutTextInElement(SubPromptHtml(), _silverlightDlrConsolePrompt);
        }

        internal void ShowPrompt() {
            _outputBuffer.PutTextInElement(PromptHtml(), _silverlightDlrConsolePrompt);
        }

        internal string PromptHtml() {
            return String.Format("{0}&gt;&nbsp;", _engine.Setup.FileExtensions[0].Substring(1));
        }

        internal string SubPromptHtml() {
            return "&nbsp;&nbsp;|&nbsp;";
        }
        #endregion

        #region Pushing stuff into Result Div
        internal void ShowCodeLineInResultDiv(string codeLine) {
            ShowPromptInResultDiv();
            _outputBuffer.ElementClass = _sdlrLine;
            _outputBuffer.ElementName = "div";
            _outputBuffer.Write(codeLine);
            _outputBuffer.Reset();
        }

        internal void ShowPromptInResultDiv() {
            _outputBuffer.ElementClass = _sdlrPrompt;
            _outputBuffer.ElementName = "span";
            _outputBuffer.Write(_multiLinePrompt ? SubPromptHtml() : PromptHtml());
            _outputBuffer.Reset();
            if (_multiLine) {
                _multiLinePrompt = true;
            }
        }

        internal void ShowValueInResultDiv(object result) {
            ScriptScope scope = _engine.CreateScope();
            scope.SetVariable("sdlr_result", result);
            var resultStr = _engine.CreateScriptSourceFromString("sdlr_result.inspect").Execute(scope).ToString();
            _outputBuffer.ElementClass = _sdlrValue;
            _outputBuffer.ElementName = "div";
            _outputBuffer.Write("=> " + (result != null ? resultStr : "nil"));
            _outputBuffer.Reset();
        }

        internal void FlushOutputInResultDiv() {
            _outputBuffer.Flush();
        }
        #endregion

        #region History
        public void ShowNextCommand() {
            _silverlightDlrConsoleCode.SetProperty("value", GetNextCommand());
        }

        public void ShowPreviousCommand() {
            _silverlightDlrConsoleCode.SetProperty("value", GetPreviousCommand());
        }
        #endregion

        #endregion
    }

    #region Text Buffer
    public class ConsoleOutputBuffer : ConsoleWriter {
        public string ElementClass;
        public string ElementName;
        private HtmlElement _results;
        private string _outputClass;
        private string _queue;

        public ConsoleOutputBuffer(HtmlElement results, string outputClass) {
            _results = results;
            _outputClass = outputClass;
        }

        public string Queue { get { return _queue; } }

        public override void Write(string str) {
            if (ElementName == null) {
                _queue += str;
            } else {
                _results.AppendChild(PutTextInNewElement(TextToHtml(str), ElementName, ElementClass));
            }
        }

        public void Reset() {
            ElementClass = null;
            ElementName = null;
        }

        public override void Flush() {
            if (_queue != null) {
                _results.AppendChild(PutTextInNewElement(TextToHtml(_queue), "div", _outputClass));
                _queue = null;
            }
        }

        public static string TextToHtml(string text) {
            return text.Replace("\t", "  ").Replace(" ", "&nbsp;").Replace((new ConsoleWriter()).NewLine, "<br />");
        }

        #region HTML Helpers
        private HtmlElement PutTextInNewElement(string str, string tagName, string className) {
            var element = HtmlPage.Document.CreateElement(tagName == null ? "div" : tagName);
            if (className != null) {
                element.CssClass = className;
            }
            PutTextInElement(str, element);
            return element;
        }

        internal void PutTextInElement(string str, HtmlElement e) {
            e.SetProperty("innerHTML", str);
        }

        internal void AppendTextInElement(string str, HtmlElement e) {
            var toPrepend = e.GetProperty("innerHTML").ToString();
            e.SetProperty("innerHTML", toPrepend + str);
        }
        #endregion
    }

    public class ConsoleInputBuffer : ConsoleWriter {
        private Console _console;
        public ConsoleInputBuffer(Console console) {
            _console = console;
        }
        public override void Write(string str) {
            string[] lines = str.Split(CoreNewLine);
            if (lines.Length > 1) {
                foreach (var line in lines) {
                    _console.AppendCode(line);
                    _console.RunCode();
                }
            } else if (lines.Length != 0) {
                _console.AppendCode(lines[lines.Length - 1]);
            }
        }
    }

    public class ConsoleWriter : TextWriter {
        protected Encoding _encoding;
        public ConsoleWriter() {
            _encoding = new System.Text.UTF8Encoding();
            CoreNewLine = new char[] { '\n' };
        }
        public override Encoding Encoding { get { return _encoding; } }
        public override void WriteLine(string str) {
            Write(str + "\n");
        }
    }
    #endregion
}