from System.Windows import Application
from System.Windows.Controls import UserControl
from System.Windows.Media import SolidColorBrush, Colors

class App:
  def __init__(self):
    root = Application.Current.LoadRootVisual(UserControl(), "app.xaml")
    root.Message.Text = "Welcome to Python!"
    root.Message.MouseLeftButtonDown += self.Message_MLBD
    root.Message.MouseLeftButtonUp   += self.Message_MLBU

  def Message_MLBD(self, s, e):
    s.Foreground = SolidColorBrush(Colors.Red)

  def Message_MLBU(self, s, e):
    s.Foreground = SolidColorBrush(Colors.Black)

App()
