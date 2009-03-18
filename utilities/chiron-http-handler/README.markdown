Chiron HTTP Handler
===================

Chiron.exe contains the XapHttpHandler type, which is a HttpHandler to enable 
IIS or the ASP.NET Development WebServer (Cassini) to auto-xap any directory
when requested with the .xap extension, just like Chiron does.

ChironHttpHandler.sln is a example of this working in action. To set it up for
your own project:

Visual Studio ASP.NET Development WebServer
-------------------------------------------
1. Create a ASP.NET Website project
2. Add the binaries produced from agdlr.sln to a Bin folder inside the website.
3. Add the following to web.config:

(TODO: Chiron.exe.config sections, as well as the same web.config stuff that
 ChironHttpHandler.sln has)

IIS
---
Works the same as above; just move your project to IIS.
