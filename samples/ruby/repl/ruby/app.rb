include Microsoft::Scripting::Silverlight
include System::Windows::Browser

replDiv = Repl.create
HtmlPage.document.body.append_child replDiv
Repl.current.start

class IO
  def write(str)
    Repl.current.output_buffer.write(str)
  end
end