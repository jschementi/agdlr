module XAP
  include Microsoft::Scripting::Silverlight
  
  def self.get_file_contents(relative_path_or_uri)
    Package.get_file_contents(relative_path_or_uri)
  end
  
  def self.get_file(relative_path_or_uri)
    Package.get_file(relative_path_or_uri)
  end
end
