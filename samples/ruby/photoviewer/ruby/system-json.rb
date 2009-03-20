require 'System.Json'
include System

module System::Json
  class JsonValue
    def method_missing(index)
      item = self.get_Item(index.to_s.to_clr_string)
      super if item.nil?
      type = item.get_JsonType
      return item.to_string.to_s.to_f if type == JsonType.Number
      return item.to_string.to_s.split("\"").last if type == JsonType.String
      return System::Boolean.parse(item) if type == JsonType.Boolean
      item
    end

    def inspect
      to_string.to_s
    end
  end
end
