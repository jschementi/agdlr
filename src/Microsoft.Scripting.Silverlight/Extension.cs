using System;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Ink;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;
using System.Windows.Resources;
using System.Collections.Generic;

namespace Microsoft.Scripting.Silverlight {

	public static class Extension {

        private static Action _downloadsCompleted;

        public static void FetchCompleted(List<string> assemblyNames, object sender, OpenReadCompletedEventArgs e) {
            var sri = new StreamResourceInfo(e.Result, null);
            foreach (var assembly in assemblyNames) {
                var dll = Application.GetResourceStream(sri,
                    new Uri(string.Format("{0}.dll", assembly), UriKind.Relative));
                if (dll != null) {
                    Package.LanguageAssemblies.Add(dll);
                }
            }
        }

        public static void FetchDLR(Action downloadsCompleted) {
            _downloadsCompleted = downloadsCompleted;
            WebClient wc = new WebClient(); 
            string sRequest = Package.LanguageExtensionUris[0]; // DLR 
            wc.OpenReadCompleted += new OpenReadCompletedEventHandler(FetchDLRCompleted);
            wc.OpenReadAsync(new Uri(sRequest, UriKind.Absolute));
        }

        public static void FetchDLRCompleted(object sender, OpenReadCompletedEventArgs e) {
            FetchCompleted(Package.DLRAssemblyNames, sender, e);
            FetchRuby();
        }

        public static void FetchRuby() {
            WebClient wc = new WebClient();
            var index = 1; // Ruby
            var uri = Package.LanguageExtensionUris[index];
            wc.OpenReadCompleted += new OpenReadCompletedEventHandler(FetchRubyCompleted);
            wc.OpenReadAsync(new Uri(uri));
        }

        public static void FetchRubyCompleted(object sender, OpenReadCompletedEventArgs e) {
            FetchCompleted(Package.LanguageAssemblyNames, sender, e);
            FetchPythonExtensions();
        }

        public static void FetchPythonExtensions() {
            WebClient wc = new WebClient();
            var index = 2; // Python 
            var uri = Package.LanguageExtensionUris[index];
            wc.OpenReadCompleted += new OpenReadCompletedEventHandler(FetchPythonExtensionsCompleted);
            wc.OpenReadAsync(new Uri(uri));
        }

        public static void FetchPythonExtensionsCompleted(object sender, OpenReadCompletedEventArgs e) {
            FetchCompleted(Package.LanguageAssemblyNames, sender, e);
            _downloadsCompleted.Invoke();
            _downloadsCompleted = null;
        }
	}
}
