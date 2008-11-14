require 'mscorlib'
require 'System.Windows, Version=2.0.5.0, Culture=neutral, PublicKeyToken=7cec85d7bea7798e'
require 'System.Windows.Browser, Version=2.0.5.0, Culture=neutral, PublicKeyToken=7cec85d7bea7798e'

include System::Windows
include System::Windows::Browser
include System::Windows::Controls
include System::Windows::Documents
include System::Windows::Input
include System::Windows::Interop
include System::Windows::Markup
include System::Windows::Media
include System::Windows::Media::Animation
include System::Windows::Shapes
        
# Inject "canvas"

# TODO: why doesn't the following work
#$canvas = ::System::Windows::Application.Current.RootVisual.FindName('XamlRootCanvas')
$canvas = Application.Current.RootVisual.children.last.children.last

def canvas()
    $canvas
end

class FrameworkElement
  def left
    Canvas.get_left self
  end
  def top
    Canvas.get_top self
  end
  def left=(x)
    Canvas.set_left(self, x)
  end
  def top=(y)
    Canvas.set_top(self, y)
  end 
end
