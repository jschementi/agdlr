/* ****************************************************************************
 *
 * Copyright (c) Microsoft Corporation. 
 *
 * This source code is subject to terms and conditions of the Microsoft Public License. A 
 * copy of the license can be found in the License.html file at the root of this distribution. If 
 * you cannot locate the  Microsoft Public License, please send an email to 
 * dlr@microsoft.com. By using this source code in any fashion, you are agreeing to be bound 
 * by the terms of the Microsoft Public License.
 *
 * You must not remove this notice, or any other, from this software.
 *
 *
 * ***************************************************************************/

using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Threading;
using System.Windows;
using System.Windows.Resources;
using System.Xml;
using Microsoft.Scripting.Hosting;
using Microsoft.Scripting.Runtime;
using Microsoft.Scripting.Utils;
using System.Net;

namespace Microsoft.Scripting.Silverlight {

    /// <summary>
    /// The entry point for dynamic language applications
    /// It is a static class that exists to bootstrap the DLR, and start running the application
    /// Also contains helper APIs. These can be accessed by using:
    /// 
    ///   System.Windows.Application.Current
    ///   
    /// ... which returns the global instance of DynamicApplication
    /// </summary>
    public class DynamicApplication : Application {

        #region public properties

        /// <summary>
        /// Returns the entry point file
        /// </summary>
        public string EntryPoint {
            get { return _entryPoint; }
            set { _entryPoint = value; }
        }

        /// <summary>
        /// Determines if we emit optimized code, and whether turn on debugging features
        /// </summary>
        public bool Debug {
            get { return _debug; }
            set { _debug = value; }
        }

        /// <summary>
        /// Returns the "initParams" argument passed to the Silverlight control
        /// (otherwise would be inaccessible because the DLR host consumes them)
        /// </summary>
        public IDictionary<string, string> InitParams {
            get { return _initParams; }
        }

        /// <summary>
        /// Returns the instance of the DynamicApplication.
        /// Importantly, this method works if not on the UI thread, unlike
        /// Application.Current
        /// </summary>
        public static new DynamicApplication Current {
            get { return _Current; }
        }
        
        /// <summary>
        /// Indicates whether we report unhandled errors to the HTML page
        /// </summary>
        public bool ReportUnhandledErrors {
            get { return _reportErrors; }
            set {
                if (value != _reportErrors) {
                    _reportErrors = value;
                    if (_reportErrors) {
                        Application.Current.UnhandledException += OnUnhandledException;
                    } else {
                        Application.Current.UnhandledException -= OnUnhandledException;
                    }
                }
            }
        }

        /// <summary>
        /// Indicates what HTML element errors should be reported into.
        /// </summary>
        public string ErrorTargetID {
            get { return _errorTargetID; }
            set { _errorTargetID = value; }
        }

        /// <summary>
        /// Indicates whether or not CLR stack traces are shown in the error report
        /// </summary>
        public bool ExceptionDetail {
            get { return _exceptionDetail; }
        }

        /// <summary>
        /// The ScriptRuntime that application code runs in
        /// </summary>
        public ScriptRuntime Runtime {
            get { return _runtime; }
        }

        internal ScriptEngine Engine {
            get { return _engine; }
        }

        internal ScriptScope EntryPointScope {
            get { return _entryPointScope; }
        }
        #endregion

        #region instance variables

        private string _entryPoint;
        private bool   _consoleEnabled;
        private bool   _debug;
        private bool   _exceptionDetail;
        private bool   _reportErrors;
        private string _errorTargetID;

        private IDictionary<string, string> _initParams;

        private static int _UIThreadId;

        // we need to store this because we can't access Application.Current
        // if we're not on the UI thread
        private static volatile DynamicApplication _Current;

        private ScriptRuntime _runtime;
        private ScriptRuntimeSetup _runtimeSetup;
        private ScriptEngine _engine;
        private ScriptScope _entryPointScope;

        internal static bool InUIThread {
            get { return _UIThreadId == Thread.CurrentThread.ManagedThreadId; }
        }
        #endregion

        #region public API

        // these are instance methods so you can do Application.Current.TheMethod(...)

        /// <summary>
        /// Loads a XAML file, represented by a Uri, into a UIElement, and sets
        /// the UIElement as the RootVisual of the application.
        /// </summary>
        /// <param name="root">UIElement to load the XAML into</param>
        /// <param name="uri">Uri to a XAML file</param>
        /// <returns></returns>
        public DependencyObject LoadRootVisual(UIElement root, Uri uri) {
            Application.LoadComponent(root, uri);
            RootVisual = root;
            return root;
        }

        /// <summary>
        /// Loads a XAML file, represented by a string, into a UIElement, and sets
        /// the UIElement as the RootVisual of the application.
        /// </summary>
        /// <param name="root">UIElement to load the XAML into</param>
        /// <param name="uri">string representing the relative Uri of the XAML file</param>
        /// <returns></returns>
        public DependencyObject LoadRootVisual(UIElement root, string uri) {
            return LoadRootVisual(root, MakeUri(uri));
        }

        /// <summary>
        /// Loads a XAML file, represented by a string, into any object.
        /// </summary>
        /// <param name="component">The object to load the XAML into</param>
        /// <param name="uri">string representing the relative Uri of the XAML file</param>
        public void LoadComponent(object component, string uri) {
            LoadComponent(component, MakeUri(uri));
        }

        /// <summary>
        /// Makes a Uri object that is relative to the location of the "start" source file.
        /// </summary>
        /// <param name="relativeUri">Any Uri</param>
        /// <returns>A Uri relative to the "start" source file</returns>
        public Uri MakeUri(string relativeUri) {
            // Get the source file location so we can make the URI relative to the executing source file
            string baseUri = Path.GetDirectoryName(_entryPoint);
            if (baseUri != "") baseUri += "/";
            return new Uri(baseUri + relativeUri, UriKind.Relative);
        }

        public static ScriptRuntimeSetup CreateRuntimeSetup(IEnumerable<Assembly> assemblies) {
            ScriptRuntimeSetup setup = Configuration.TryParseFile();
            if (setup == null) {
                if (assemblies == null) {
                    assemblies = Package.GetManifestAssemblies();
                }
                if (!Package.ContainsDLRAssemblies(Deployment.Current.Parts)) {
                    assemblies = Package.GetExtensionAssemblies();
                }
                setup = Configuration.LoadFromAssemblies(assemblies);
            }
            setup.HostType = typeof(BrowserScriptHost);
            return setup;
        }

        public static ScriptRuntimeSetup CreateRuntimeSetup() {
            return CreateRuntimeSetup(null);
        }

        public static StreamResourceInfo XapFile {
            get {
                return BrowserPAL.PAL.XapFile;
            }
            set {
                BrowserPAL.PAL.XapFile = value;
            }
        }
        #endregion

        #region implementation

        /// <summary>
        /// Called by Silverlight host when it instantiates our application
        /// </summary>
        public DynamicApplication() {
            if (_Current != null) {
                throw new Exception("Only one instance of DynamicApplication can be created");
            }

            _Current = this;
            _UIThreadId = Thread.CurrentThread.ManagedThreadId;

            Startup += new StartupEventHandler(DynamicApplication_Startup);
        }

        void DynamicApplication_Startup(object sender, StartupEventArgs e) {
            // Turn error reporting on while we parse initParams.
            // (Otherwise, we would silently fail if the initParams has an error)
            ReportUnhandledErrors = true;

            ParseArguments(e.InitParams);

            if (!Package.ContainsDLRAssemblies(Deployment.Current.Parts)) {
                // FIXME: for now, we manually redownload extensions, 
                // A SL bug is stopping us from using Deployment.Current.ExternalParts 
                // to figure out what extensions has been requested by the application.
                FetchDLRExtensions();
            }
        }

        #region Downloading Extensions
        void FetchExtensionCompleted(List<string> assemblyNames, object sender, OpenReadCompletedEventArgs e) {
            var sri = new StreamResourceInfo(e.Result, null);
            foreach (var assembly in assemblyNames) {
                var dll = Application.GetResourceStream(sri,
                    new Uri(string.Format("{0}.dll", assembly), UriKind.Relative));
                if (dll != null) {
                    Package.LanguageAssemblies.Add(dll);
                }
            }
        }
        void FetchDLRExtensions() {
            WebClient wc = new WebClient(); 
            string sRequest = Package.LanguageExtensionUris[0]; // DLR 
            wc.OpenReadCompleted += new OpenReadCompletedEventHandler(FetchDLRExtensionCompleted);
            wc.OpenReadAsync(new Uri(sRequest, UriKind.Absolute));
        }

        void FetchDLRExtensionCompleted(object sender, OpenReadCompletedEventArgs e) {
            FetchExtensionCompleted(Package.DLRAssemblyNames, sender, e);
            FetchLanguageExtensions();
        }

        void FetchLanguageExtensions() {
            WebClient wc = new WebClient();
            var index = 1; // FIXME: this defaults to IronRuby. Needs to figure out how to detect language this early on.
            var uri = Package.LanguageExtensionUris[index];
            wc.OpenReadCompleted += new OpenReadCompletedEventHandler(FetchLanguageExtensionsCompleted);
            wc.OpenReadAsync(new Uri(uri));
        }

        void FetchLanguageExtensionsCompleted(object sender, OpenReadCompletedEventArgs e) {
            FetchExtensionCompleted(Package.LanguageAssemblyNames, sender, e);
            Start();
        }
        #endregion

        void Start() {
            InitializeDLR();
            StartMainProgram();
        }

        private void InitializeDLR() {
            var setup = CreateRuntimeSetup();
            setup.DebugMode = _debug;
            setup.Options["SearchPaths"] = new string[] { String.Empty };
            
            _runtimeSetup = setup;
            _runtime = new ScriptRuntime(setup);

            _runtime.LoadAssembly(GetType().Assembly); // to expose our helper APIs
            LoadDefaultAssemblies(_runtime);
        }

        public static void LoadDefaultAssemblies(ScriptRuntime runtime) {
            // Add default references to Silverlight platform DLLs
            // (Currently we auto reference CoreCLR, UI controls, browser interop, and networking stack.)
            foreach (string name in new string[] { "mscorlib", "System", "System.Windows", "System.Windows.Browser", "System.Net" }) {
                runtime.LoadAssembly(GetAssemblyByName(name));
            }
        }

        public static Assembly GetAssemblyByName(string name) {
            return BrowserPAL.PAL.LoadAssembly(name);
        }

        private void StartMainProgram() {
            string code = Package.GetEntryPointContents();
            _engine = _runtime.GetEngineByFileExtension(Path.GetExtension(_entryPoint));
            _entryPointScope = _engine.CreateScope();

            if (_consoleEnabled)
                Repl.Show();

            ScriptSource sourceCode = _engine.CreateScriptSourceFromString(code, _entryPoint, SourceCodeKind.File);
            sourceCode.Compile(new ErrorFormatter.Sink()).Execute(_entryPointScope);
        }


        private void ParseArguments(IDictionary<string, string> args) {
            // save off the initParams (otherwise user code couldn't access it)
            // also, normalize initParams because otherwise it preserves whitespace, which is not very useful
            _initParams = new Dictionary<string, string>(args.Count);
            foreach (KeyValuePair<string, string> pair in args) {
                _initParams[pair.Key.Trim()] = pair.Value.Trim();
            }

            _initParams.TryGetValue("start", out _entryPoint);

            string consoleEnabled;
            if (_initParams.TryGetValue("console", out consoleEnabled)) {
                if (!bool.TryParse(consoleEnabled, out _consoleEnabled)) {
                    throw new ArgumentException("You must set 'console' to 'true' or 'false', for example: initParams: \"..., console=true\"");
                }
            }
            
            string debug;
            if (_initParams.TryGetValue("debug", out debug)) {
                if (!bool.TryParse(debug, out _debug)) {
                    throw new ArgumentException("You must set 'debug' to 'true' or 'false', for example: initParams: \"..., debug=true\"");
                }
            }

            string exceptionDetail;
            if (_initParams.TryGetValue("exceptionDetail", out exceptionDetail)) {
                if (!bool.TryParse(exceptionDetail, out _exceptionDetail)) {
                    throw new ArgumentException("You must set 'exceptionDetail' to 'true' or 'false', for example: initParams: \"..., exceptionDetail=true\"");
                }
            }

            string reportErrorsDiv;
            if (_initParams.TryGetValue("reportErrors", out reportErrorsDiv)) {
                _errorTargetID = reportErrorsDiv;
                ReportUnhandledErrors = true;
            } else {
                // if reportErrors is unspecified, set to false
                ReportUnhandledErrors = false;
            }
        }

        private void OnUnhandledException(object sender, ApplicationUnhandledExceptionEventArgs args) {
            args.Handled = true;
            ErrorFormatter.DisplayError(_errorTargetID, args.ExceptionObject);
        }

        #endregion
    }
}
