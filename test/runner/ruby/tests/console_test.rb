describe 'Console regressions' do
  
  def inspect_object(obj)
    require 'IronRuby'
    engine = IronRuby::Ruby.get_engine(DynamicApplication.current.runtime)
    IronRuby::Ruby.
      get_execution_context(engine).
      define_global_variable('__test_object__', obj)
    engine.
      create_script_source_from_string('$__test_object__.inspect.to_clr_string').
      execute
  end

  it 'should escape HTML property' do
    ReplOutputBuffer = Microsoft::Scripting::Silverlight::ReplOutputBuffer
    element = HtmlPage.document.create_element 'div'
    result = inspect_object(element)
    
    buffer = ReplOutputBuffer.new element, 'output'
    buffer.write(result)
    buffer.flush
    $element = element
    element.get_property('innerHTML').to_s.should.match(
      /<div class="output">#&lt;System::Windows::Browser::HtmlElement:0x[0-9a-f]+&gt;<\/div>/
    )
  end
end