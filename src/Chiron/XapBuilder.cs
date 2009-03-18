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
using System.Text;
using System.Xml;
using System.Diagnostics;
using System.Reflection;

namespace Chiron {
    /// <summary>
    /// XAP file builder for dynamic language applications
    /// Needs to know how to insert assemblies for the language
    /// </summary>
    static class XapBuilder {
        public static byte[] XapToMemory(string dir) {
            MemoryStream ms = new MemoryStream();
            XapFiles(new ZipArchive(ms, FileAccess.Write), dir);
            return ms.ToArray();
        }

        public static void XapToDisk(string dir, string xapfile) {
            XapFiles(new ZipArchive(xapfile, FileAccess.Write), dir);
        }

        static void XapFiles(ZipArchive zip, string dir) {
            ICollection<LanguageInfo> langs = FindSourceLanguages(dir);
            
            string manifestPath = Path.Combine(dir, "AppManifest.xaml");
            IList<Uri> assemblies;

            if (File.Exists(manifestPath)) {
                assemblies = GetManifestAssemblies(manifestPath);
            } else {
                assemblies = GetLanguageAssemblies(langs);
                // generate the manfiest
                using (Stream appManifest = zip.Create("AppManifest.xaml")) {
                    Chiron.ManifestTemplate.Generate(assemblies).Save(appManifest);
                }
            }

            AddAssemblies(zip, dir, assemblies);

            GenerateLanguagesConfig(zip, langs);

            AddPathDirectories(zip);

            // add files on disk last so they always overwrite generated files
            zip.CopyFromDirectory(dir, "");

            zip.Close();
        }

        // add directories that are on Chiron's path
        internal static void AddPathDirectories(ZipArchive zip) {
            if (Chiron.LocalPath != null) {
                foreach (var path in Chiron.LocalPath) {
                    string[] splitPath = path.Split(Path.DirectorySeparatorChar);
                    zip.CopyFromDirectory(path, splitPath[splitPath.Length - 1]);
                }
            }
        }

        // Get the URIs of the assemblies from the AppManifest.xaml file
        private static IList<Uri> GetManifestAssemblies(string manifestPath) {
            List<Uri> assemblies = new List<Uri>();

            XmlDocument doc = new XmlDocument();
            doc.Load(manifestPath);
            foreach (XmlElement ap in doc.GetElementsByTagName("AssemblyPart")) {
                string src = ap.GetAttribute("Source");
                if (!string.IsNullOrEmpty(src)) {
                    assemblies.Add(new Uri(src, UriKind.RelativeOrAbsolute));
                }
            }

            return assemblies;
        }

        // Generates AppManifest.xaml as if we were generating it for the XAP
        internal static XmlDocument GenerateManifest(string dir) {
            return Chiron.ManifestTemplate.Generate(GetLanguageAssemblies(FindSourceLanguages(dir)));
        }

        // Gets the list of DLR+language assemblies that will be automatically added to the XAP
        private static IList<Uri> GetLanguageAssemblies(IEnumerable<LanguageInfo> langs) {
            List<Uri> assemblies = new List<Uri>();
            assemblies.Add(GetUri("Microsoft.Scripting.Silverlight.dll"));
            assemblies.Add(GetUri("Microsoft.Scripting.ExtensionAttribute.dll"));
            assemblies.Add(GetUri("Microsoft.Scripting.Core.dll"));
            assemblies.Add(GetUri("Microsoft.Scripting.dll"));
            foreach (LanguageInfo lang in langs) {
                foreach (string asm in lang.Assemblies) {
                    assemblies.Add(GetUri(asm));
                }
            }
            return assemblies;
        }

        // prepends uriPrefix from the app.config file, unless the path is already absolute
        private static Uri GetUri(string path) {
            Uri uri = new Uri(path, UriKind.RelativeOrAbsolute);
            string prefix = Chiron.UrlPrefix;
            if (prefix != "" && !IsPathRooted(uri)) {
                uri = new Uri(prefix + path, UriKind.RelativeOrAbsolute);
            }
            return uri;
        }

        // returns true if the uri is absolute or starts with '/'
        // (i.e. absolute uri or absolute path)
        private static bool IsPathRooted(Uri uri) {
            return uri.IsAbsoluteUri || uri.OriginalString.StartsWith("/");
        }

        // Adds assemblies with relative paths into the XAP file
        private static void AddAssemblies(ZipArchive zip, string dir, IList<Uri> assemblyLocations) {
            foreach (Uri uri in assemblyLocations) {
                if (IsPathRooted(uri)) {
                    continue;
                }

                string targetPath = uri.OriginalString;
                string localPath = Path.Combine(dir, targetPath);

                if (!File.Exists(localPath)) {
                    localPath = Chiron.TryGetAssemblyPath(targetPath);

                    if (localPath == null) {
                        throw new ApplicationException("Could not find assembly: " + uri);
                    }
                }

                zip.CopyFromFile(localPath, targetPath);

                // Copy PDBs if available
                string pdbPath = Path.ChangeExtension(localPath, ".pdb");
                string pdbTarget = Path.ChangeExtension(targetPath, ".pdb");
                if (File.Exists(pdbPath)) {
                    zip.CopyFromFile(pdbPath, pdbTarget);
                }
            }
        }

        // Generates langauges.config file
        // this is needed by the DLR to load arbitrary DLR-based languages implementations
        private static void GenerateLanguagesConfig(ZipArchive zip, ICollection<LanguageInfo> langs) {
            bool needLangConfig = false;
            foreach (LanguageInfo lang in langs) {
                if (lang.LanguageContext != "") {
                    needLangConfig = true;
                    break;
                }
            }

            // Only need langauge configuration file for non-builtin languages
            if (needLangConfig) {
                Stream outStream = zip.Create("languages.config");
                StreamWriter writer = new StreamWriter(outStream);
                writer.WriteLine("<Languages>");

                foreach (LanguageInfo lang in langs) {
                    writer.WriteLine("  <Language languageContext=\"{0}\"", lang.LanguageContext);
                    writer.WriteLine("            assembly=\"{0}\"", lang.GetContextAssemblyName());
                    writer.WriteLine("            extensions=\"{0}\" />", lang.GetExtensionsString());
                }

                writer.WriteLine("</Languages>");
                writer.Close();
            }
        }

        // Scans the application's directory to find all files whose extension 
        // matches one of Chiron's known languages
        internal static ICollection<LanguageInfo> FindSourceLanguages(string dir) {
            Dictionary<LanguageInfo, bool> result = new Dictionary<LanguageInfo, bool>();

            foreach (string file in Directory.GetFiles(dir, "*", SearchOption.AllDirectories)) {
                string ext = Path.GetExtension(file);
                LanguageInfo lang;
                if (Chiron.Languages.TryGetValue(ext.ToLower(), out lang)) {
                    result[lang] = true;
                }
            }
            if (result.Count == 0) {
                throw new ApplicationException("Could not find any dynamic language source files under path: " + dir);
            }

            return result.Keys;
        }
    }
}
