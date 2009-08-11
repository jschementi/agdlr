AgDLR is no longer the latest+greatest bits for dynamic languages in Silverlight; the language's respective websites have the latest version of these bits. The source code in this GitHub project will not be updated anymore, and day-to-day development has moved directly into the language's source tree.

[IronPython](http://ironpython.codeplex.com)
[IronRuby](http://ironruby.net)


README contents:

AgDLR - Dynamic Languages in Silverlight
========================================
  [Dynamic Languages on Silverlight.net](http://silverlight.net/dlr)
  [AgDLR Project Homepage](http://sdlsdk.codeplex.com)

  "agdlr", the Silverlight Dynamic Languages project, is the integration 
  between Silverlight and Dynamic Languages running on the Dynamic Language 
  Runtime (DLR). The languages included in this package are IronPython and IronRuby.

  Note: this package is meant to be used to develop applications with 
  Silverlight 2 RTW. Install Silverlight for [Windows](http://go.microsoft.com/fwlink/?LinkID=119972)
  or the [Mac](http://go.microsoft.com/fwlink/?LinkID=119973)

Package
-------
  /bin:       AgDLR Binaries
  
  /docs:      Documentation

  /samples:   See /samples/README for more information
  
  /script:    Tools for creating and running Silverlight applications

  /test:      AgDLR Test Suite. Run with /script/test.bat
  
  /utilities: See /utilities/README.markdown

  /src.url:   Source code download link for Microsoft.Scripting.Silverlight.dll and Chiron.exe.

  /LICENSE:   Microsoft Public License

Getting Started
---------------
  1. Create a new Silverlight application

      script/sl [ruby|python] <application_name>

    This will create a Silverlight application in the language of your choosing in
    the "application_name" directory where you ran the script.

  2. Run an application

      script/server /b

    This will launch Chiron, the Silverlight development utility, as well as open
    your default browser to [http://localhost:2060](http://localhost:2060). If you pass the /w
    instead of the /b switch, it will just start the server and not launch your
    browser. See the Chiron section below for more of its usage details.

    Note: run script/env.bat, which will add scripts to your path, shortening the command
    to just "server".

    This command requires Mono to be installed on the Mac.
    [Download Mono](http://www.go-mono.com/mono-downloads/download.html)

CHANGELOG
---------
  0.5.0 - 2009-03-20

  - MIX09 release for Silverlight 2 and Silverlight 3 Beta.

  - Adds a dynamic language REPL to any Silverlight app for a explorative
    developer experience (add console=true to initParams. See 
    samples/(python|ruby)/repl as well for how to use Repl programatically.)

  - Run the Test suite (using IronRuby and Bacon) as any other Silverlight
    application, and use Bacon to write your own tests suites. 
    http://github.com/jschementi/eggs

  - Beginnings of a port of the internal Microsoft DLR Silverlight test suite.

  - API improvement for hosting DLR language in C#/VB Silverlight applications.

  - Fix Codeplex Bug# 11803 (zip version fix)

  - chiron-here.reg - Run Chiron by right-clicking on a directory (in utilities)

  - set DynamicApplication.XapFile to change where a language's filesystem 
    features/libraries look for files.

  - Chiron /path option - ";" separated list of folder to be included in XAP
    (poor mans lib path)

  - New versions of IronRuby (0.3) and IronPython (2.6 pre-alpha)

  - DynamicApplication.LoadAssemblies - support for SL3 Transparent Platform
    Extensions.

  - Managed JScript has been removed from the package.

  - Thanks for the contributions!
    * Removed UI thread check in FileExists (Eloff) November 26, 2008
      commit bd9b2d56eeda8aea69b90245f86493fc22ca0803
    * Fixed ErrorReporter bug when _sourceFileName is not a file on disk (e.g. <string>) (Eloff) November 26, 2008
      commit 61ee0134167a546a55cf138ef63edc5d7eb4b830
    * XapHttpHandler gives IIS or Cassini the auto-XAPing power of Chiron (also in utilities) (Harry Pierson) March 19, 2009
      commit 63a5ea3cf94068b87273531b5c96d84d8de983d2

  0.4.0 - 2008-10-15

  - New builds of DLR/Languages for Silverlight 2 RTW

  - Custom Fonts: In Silverlight 2 Beta 2 a custom font could either be placed 
    in the XAP file, or as an assembly resource, and loaded by Silverlight. 
    In Silverlight 2 RC0, only an assembly resource is allowed. The current 
    work-around for dynamic languages is to load a dummy DLL with the fonts as
    resources.

  - JScript/Python Interop: This version breaks JScript/Python interop since
    JScript does not support IDynamicObject, which Python uses to do dynamic 
    method dispatch. Therefore, the sample that showed this, jscript/fractulator,
    is not in this release.

  0.3.9 - 2008-09-29

  - New builds of DLR/Languages for Silverlight 2 RC

  0.3.0 - 2008-08-29

  - New builds of DLR/Languages

  0.2.1 - 2008-06-11

  - Now script/sl.bat does not depend on Ruby being installed

  0.2.0 - 2008-06-09

  - Release for Silverlight 2 Beta 2. Removes samples and source code from 
    main project to seperate downloads on http://codeplex.com/sdlsdk.

  0.1.1 - 2008-05-06

  - Adds Managed JScript to the package, as well as the "sl" command

  0.1.0 - 2008-03-07

  - MIX08 release for Silverlight 2; IronRuby and IronPython support for 
    Silverlight 2 Beta 1.
    
  - Abandons <x:Code /> model for a in XAP solution, and uses a auto-xapping 
    tool (Chiron.exe) for a nice development experience.

