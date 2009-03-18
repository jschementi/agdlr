pushd %~dp0..\..
msbuild
popd
copy %~dp0..\..\bin\debug\* %~dp0ChironHttpHandler.SampleSite\Bin
