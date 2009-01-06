include System::Windows::Browser

def append_to_body(tag_name, options)
  div = HtmlPage.document.create_element tag_name
  options.each do |key, value|
    div.set_property key.to_s.to_clr_string, value.to_s.to_clr_string
  end	
  HtmlPage.document.body.append_child div
  div
end

describe 'Html document extension' do
  before do
    @div ||= append_to_body 'div', :id => 'foo'
  end

  after do
    HtmlPage.document.body.remove_child @div
    @div = nil
  end

  it 'should find a HTML element' do
    div = HtmlDocumentExtension.get_bound_member HtmlPage.document, 'foo'
    div.should.equal @div
  end

  it 'should not find a HTML element' do
    id = 'doesnotexist'
    HtmlPage.document.get_element_by_id(id).should.be.nil
    div = HtmlDocumentExtension.get_bound_member HtmlPage.document, id
    div.should.equal Microsoft::Scripting::Runtime::OperationFailed.value
  end
end

describe 'Html element extension' do
  before do
    @div ||= append_to_body 'div', :id => 'foo', :innerHTML => 'test'
  end
  
  after do
    HtmlPage.document.body.remove_child @div
    @div = nil
  end

  it 'should get properties of a HTML element' do
    value = HtmlElementExtension.get_bound_member @div, 'innerHTML'
    value.to_s.should.equal 'test'
  end
  
  it 'should not get property of a HTML element' do
    value = HtmlElementExtension.get_bound_member @div, 'doesnotexist'
    value.should.be.nil
  end
  
  it 'should set a property of a HTML element' do
    @div.get_property('innerHTML').to_s.should.not.equal 'updated'
    HtmlElementExtension.set_member(@div, 'innerHTML', 'updated')
    @div.get_property('innerHTML').to_s.should.equal 'updated'
  end
end

describe 'Framework element extension' do
  before do
    @root = System::Windows::Controls::UserControl.new
    DynamicApplication.current.load_component @root, 'tests/assets/foo.xaml'
  end

  it 'should find a UIElement' do
    element = FrameworkElementExtension.get_bound_member(@root, 'message')
    element.should.not.be.nil
    element.name.to_s.should.equal 'message'
  end
  
  it 'should not find a UIElement' do
    @root.find_name('doesnotexist').should.be.nil
    result = FrameworkElementExtension.get_bound_member(@root, 'doesnotexist')
    result.should.equal Microsoft::Scripting::Runtime::OperationFailed.value
  end
end