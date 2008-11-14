require 'wpf.rb'
require 'lib/clock'

def now
  Time.now
end

class CoolDemo
  def initialize
    @clock = Clock.new canvas
  end
  
  def clock; @clock; end
  def show_clock
    @clock.load 'clock.xaml'
    canvas.children.add @clock.canvas
    self
  end

  def set_time_to(t)
    @clock.set_hands t
    self
  end
end