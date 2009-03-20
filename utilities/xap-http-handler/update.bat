pushd %~dp0..\..
msbuild
popd
copy %~dp0..\..\bin\debug\* %~dp0XapHttpHandler.SampleSite\Bin
