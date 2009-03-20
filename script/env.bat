@ECHO OFF
@pushd %~dp0..\
@git submodule init
@git submodule update
@set PATH=%PATH%;%~dp0..\bin\debug;%~dp0..\bin\release;%~dp0
@cls
