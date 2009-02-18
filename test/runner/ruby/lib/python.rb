require 'Microsoft.Scripting'
include Microsoft::Scripting
include Microsoft::Scripting::Hosting

def python(str, type = :file)
  @python_engine ||= DynamicApplication.Current.Runtime.
    GetEngine("IronPython")
  @python_scope ||= @python_engine.CreateScope()
  @python_engine.
    CreateScriptSourceFromString(str.strip, SourceCodeKind.send(type)).
    Execute(@python_scope)
end
