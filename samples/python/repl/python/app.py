import sys
from Microsoft.Scripting.Silverlight import Repl
from System.Windows.Browser import HtmlPage

replDiv = Repl.Create()
HtmlPage.Document.Body.AppendChild(replDiv)
Repl.Current.Start()

sys.stdout = Repl.Current.OutputBuffer
