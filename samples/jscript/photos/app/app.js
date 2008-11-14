Import("System.Windows.Application")
Import("System.Windows.Controls.Canvas")

function dump(msg) {
  // TODO: put application logic here
  scene.msgbox.Text += "\n"+msg
}



Import("System");		
Import("System.Windows.*");
Import("System.Windows.Markup.XamlReader");
Import("System.Windows.Controls.Canvas");
Import("System.Uri");
Import("System.UriKind");

var current = 1;
var sequence = 0;
var order = [0, 2, 6, 3, 1, 4, 5, 7];
var region = [[100, 0], [350, 0], [600, 0], [100, 250], [350, 250], [600, 250], [350, 500], [600, 500]];
var pictures = ['jaguar', 'gorilla', 'gyr', 'heron1', 'heron2', 'penguin1', 'penguin2', 'penguin3', 'tamarin', 'eagle'];

function CreatePhoto(path, x, y, rotation, sequence){

var newXAML = '<Canvas xmlns="http://schemas.microsoft.com/client/2007" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" x:Name="' + sequence + '" Width="259" Height="179" Canvas.Left="'+x+'" Canvas.Top="'+y+'" Background="#FFFFFFFF">'+
		   "	<Canvas.Triggers>" +
           "		<EventTrigger RoutedEvent='Canvas.Loaded'>" +
           "			<EventTrigger.Actions>" +
           "				<BeginStoryboard>" +
           "					<Storyboard>" +
           "						<DoubleAnimationUsingKeyFrames 	BeginTime='00:00:00' " + 
		   "														Storyboard.TargetName='PhotoScale" + sequence + "' " + 
		   " 														Storyboard.TargetProperty='ScaleX'>"+
           "							<SplineDoubleKeyFrame KeyTime='00:00:00.0000000' Value='0.2'/>"+
           "					    	<SplineDoubleKeyFrame KeyTime='00:00:00.2000000' Value='0.935'/>"+
           "						    <SplineDoubleKeyFrame KeyTime='00:00:00.3000000' Value='0.852'/>"+
           "						    <SplineDoubleKeyFrame KeyTime='00:00:00.4000000' Value='0.935'/>	"+
           "			    		</DoubleAnimationUsingKeyFrames>	"+
           "				    	<DoubleAnimationUsingKeyFrames 	BeginTime='00:00:00' " + 
           "														Storyboard.TargetName='PhotoScale" + sequence + "' " + 
           "												        Storyboard.TargetProperty='ScaleY'>"+
           "						    <SplineDoubleKeyFrame KeyTime='00:00:00.0000000' Value='0.2'/>	"+
           "					    	<SplineDoubleKeyFrame KeyTime='00:00:00.2000000' Value='0.935'/>	"+
           "					    	<SplineDoubleKeyFrame KeyTime='00:00:00.3000000' Value='0.852'/>	"+
           "				    		<SplineDoubleKeyFrame KeyTime='00:00:00.4000000' Value='0.935'/>	"+
           "			    		</DoubleAnimationUsingKeyFrames>		"+
           "	    			</Storyboard>			"+
           "   				</BeginStoryboard>	"+
           "   			</EventTrigger.Actions>	"+
           "   		</EventTrigger>  "+
           "	</Canvas.Triggers> "+
           "	<Canvas.RenderTransform>    "+
           "		<TransformGroup>    "+
           "			<ScaleTransform x:Name='PhotoScale"+sequence+"' ScaleX='0.2' ScaleY='0.2'/>   "+
           "			<SkewTransform AngleX='0' AngleY='0'/>     "+
           "			<RotateTransform Angle='" + rotation + "'/>   "+
           "			<TranslateTransform X='0' Y='0'/>     "+
           "		</TransformGroup>   "+
           "	</Canvas.RenderTransform>     "+
           "	<Image Width='242' Height='161' Canvas.Left='8' Canvas.Top='8' Source='" + path + "' /> "+
           "</Canvas>"


  var tile = XamlReader.Load(newXAML);
  scene.Children.Add(tile);
}


function OnClick(sender, args){
  if(sequence == pictures.length - 2){
    return;
  }

  var r = new System.Random();
  
  
  CreatePhoto(	"./assets/images/" +  pictures[current] + ".jpg", 
				region[order[sequence]][0], 
				region[order[sequence]][1], 
				r.Next(40) - 20, 
				sequence);
  
  if(current >= pictures.length - 1){
    current = 0;
  } else {
    current = current + 1;
  }
  
  sequence += 1;
}


var scene = Application.Current.LoadRootvisual(new Canvas, 'Scene.xaml');
scene.FindName("photo_frame").MouseLeftButtonDown += OnClick;
