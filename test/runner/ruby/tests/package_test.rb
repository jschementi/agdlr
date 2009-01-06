module ArbitraryModuleSoConsoleDoesNotConflict

  include System
  include System::IO
  include System::Windows
  
  describe 'Package' do
    def get_stream_contents(stream)
      sr = StreamReader.new(stream)
      contents = sr.read_to_end
      sr.close
      contents
    end
  
    before do
      @path ||= 'tests/assets/tmp.txt'
      @uri ||= Uri.new(@path, UriKind.relative)
      @contents ||= "Hello!\r\n".to_clr_string
      @doesnotexist ||= 'tests/assets/doesnotexist.txt'
    end
  
    it 'should get file contents from a string' do
      Package.get_file_contents(@path).should.equal @contents
    end
  
    it 'should get file contents from a Uri' do
      Package.get_file_contents(@uri).should.equal @contents
    end
  
    it 'should not get a file contents' do
      Package.get_file_contents(@doesnotexist).should.be.nil
    end
  
    it 'should get file stream from string' do
      get_stream_contents(Package.get_file(@path)).
        should.equal get_stream_contents(Application.get_resource_stream(@uri).stream)
    end
  
    it 'should get file stream from Uri' do
      get_stream_contents(Package.get_file(@uri)).
        should.equal get_stream_contents(Application.get_resource_stream(@uri).stream)
    end
  
    it 'should not get a file' do
      Package.get_file(@doesnotexist).should.be.nil
    end
  
    it 'should normalize a path' do
      Package.normalize_path('this\is\a\path\to\foo.txt').
        should.equal 'this/is/a/path/to/foo.txt'.to_clr_string
    end
  
    it 'should get manifest assemblies' do
      parts = [
        "Microsoft.Scripting.ExtensionAttribute",
        "Microsoft.Scripting.Core",
        "Microsoft.Scripting",
        "IronRuby",
        "IronRuby.Libraries",
        "System.Xml.Linq"
      ].sort
  
      assemblies = Package.get_manifest_assemblies.collect do |a|
        a.to_string.to_s.split(",").first
      end.sort
  
      parts.size.should.equal assemblies.size
  
      i = 0
      while i < assemblies.size
        parts[i].should.equal assemblies[i]
        i += 1
      end
    end
  
    it 'should get entry point contents' do
      app = Package.get_entry_point_contents
      (app =~ /Test harness for running Microsoft::Scripting::Silverlight tests/).should.not.be.nil
    end
  end
  
end