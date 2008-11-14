class Drag
  def initialize(obj)
    @click = nil
    @obj = obj
  end
  
  def enable
    @obj.mouse_left_button_down do |s,e| 
      @click = e.get_position @obj
    end
    Application.current.root_visual.mouse_left_button_up do |s,e| 
      @click = nil
    end
    canvas.mouse_move do |s,e|
      unless @click.nil?
        mouse_pos = e.get_position canvas
        @obj.left, @obj.top = mouse_pos.x - @click.x, mouse_pos.y - @click.y
      end
    end
    self
  end
end
