import clr
import math
# reference to these dlls is added by the host
#clr.AddReference("agclr")
#clr.AddReference("System.Silverlight")
from System.Windows.Controls import *
from System.Windows.Browser import *
from System.Windows import *
from System import *

tileEntries = []
class TileText:
	def __init__(self):
		self.scene = Canvas()
		Application.LoadComponent(self.scene, Uri('app.xaml', UriKind.Relative))
		Application.Current.RootVisual = self.scene
		self.tileText()
	# GLOBALS
	

	#def root_Loaded(self,sender, args):
	#	tileText(root)

	def tileText(self):
		button = self.scene.root.FindName("button")
		
		# Hook up the button event handlers	
		button.MouseEnter += self.handleMouseEnter
		button.MouseLeave += self.handleMouseLeave
		button.MouseLeftButtonUp += self.handleMouseUp
		button.MouseLeftButtonDown += self.handleMouseDown
		
		self.showTiles()

	def showTiles(self):
		# clear the previous tiles
		self.clearTree()
		# Initialize the tiles
		self.setupTileEntries()

		# Make the HTML text input visible
		textInput = HtmlPage.Document.textInput # don't need to call GetElementByID
		textInput.SetStyleAttribute("visibility", "visible") # args are 'attribute', 'value'

		# Process the default string i.e. have the tiles show this string
		self.processString(textInput.GetAttribute("value"))

	def handleMouseEnter(self,sender, eventArgs):
		buttonBG = sender.FindName("buttonBG")
		b = Media.SolidColorBrush()
		b.Color = Media.Colors.Red
		buttonBG.Fill = b

	def handleMouseLeave(self,sender, eventArgs):
		buttonBG = sender.FindName("buttonBG")
		b = Media.SolidColorBrush()
		b.Color = Media.Colors.Blue
		buttonBG.Fill = b

	def handleMouseUp(self,sender, eventArgs):
		buttonBG = sender.FindName("buttonBG")
		b = Media.SolidColorBrush()
		b.Color = Media.Color.FromArgb(0xff, 0xff, 0xd7, 0x00) # Gold
		buttonBG.Fill = b
		# show the tiles again
		self.showTiles()

	def handleMouseDown(self,sender, eventArgs):
		buttonBG = sender.FindName("buttonBG")
		b = Media.SolidColorBrush()
		b.Color = Media.Color.FromArgb(0xff, 0xd2, 0xb4, 0x8c) # Tan
		buttonBG.Fill = b

	# Handles the JoltControl's error event
	def ErrorHandler(self,line, column, hr, errorString):
		str = errorString + " at ("+line+", "+column+")"
		raise str

	# Takes a string and turns it into tiles
	def processString(self,text):
		
		# Protect from characters that our XML parser doesn't like
		text = text.replace("<", "_")
		text = text.replace("&", "_")
		text = text.replace("'", "_")
		# make text UPPERCASE for tiles
		text = text.upper()
		
		# Determine if this will fit in one line
		multiline = False
		top = 65
		if (len(text) > 11):
			multiline = True
			top = 25

		# If we're multiline, determine how to break the lines
		breakIndex = 0;
		if (multiline):
			spaceIndex = text.rfind(' ')
			if ((spaceIndex > -1) and (len(text) - spaceIndex < 11)):
				breakIndex = spaceIndex
			if ((breakIndex > 11) or (len(text) - breakIndex > 11)):
				breakIndex = 11

		leftPosition = None
		leftPosition2 = None

		if (multiline):
			leftPosition = (600 - (breakIndex * 52)) / 2
			leftPosition2 = ((600 - (len(text) - breakIndex) * 52)) / 2
		else:
			leftPosition = (600 - (len(text) * 52)) / 2

		for i in range(0,len(text)):
			if (multiline and (i == breakIndex)):
				top = 100
				leftPosition = leftPosition2
			if (text[i] == ' '):
				leftPosition += 10
				continue
			charCode = ord(text[i]) - 65
	    
			if not text[i].isalpha():
				self.addTile(i, text[i], 1, top, leftPosition, "", 17, "00:00:0" + str((i + 1) * .2)[0:3])
			else:
				self.addTile(i, text[i], 1, top, leftPosition, tileEntries[charCode].value, 12 + tileEntries[charCode].offset, "00:00:0" + str((i + 1) * .2)[0:3])
			leftPosition += 52 + 2

	#this is the template for tiles
	# $0: index of this tile
	# $1: letter on this tile
	# $2: grainIndex for this tile
	# $3: top coordinate this tile
	# $4: left coordinate of this tile
	# $5: point value of this tile
	# $6: left letter offset
	# $7: beginTime
	def addTile(self,tileNumber, letter, grainIndex, top, left, value, letterOffset, beginTime):
		xamlString = "<Canvas xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml' x:Name='tile$0' Canvas.Top='0' Canvas.Left='0' RenderTransformOrigin='0.5,0.5' Height='53' Width='53'>"
		xamlString = xamlString + "<Canvas x:Name='tileTarget$0' Canvas.Top='-100'>"
		
		xamlString = xamlString + "	 <Canvas.Triggers>"
		xamlString = xamlString + "	 <EventTrigger RoutedEvent='Canvas.Loaded'>"
		xamlString = xamlString + "	 <BeginStoryboard>"
		xamlString = xamlString + "	 <Storyboard BeginTime='$7'>"
		xamlString = xamlString + "	 <DoubleAnimationUsingKeyFrames BeginTime='00:00:00' Storyboard.TargetName='tileTarget$0' Storyboard.TargetProperty='(Canvas.Left)'>"
		xamlString = xamlString + "	 <SplineDoubleKeyFrame KeyTime='00:00:00.6' KeySpline='.75,0,0,.75' Value='$4'/>"
		xamlString = xamlString + "	 </DoubleAnimationUsingKeyFrames>"
		xamlString = xamlString + "	 <DoubleAnimationUsingKeyFrames BeginTime='00:00:00' Storyboard.TargetName='tileTarget$0' Storyboard.TargetProperty='(Canvas.Top)'>"
		xamlString = xamlString + "	 <SplineDoubleKeyFrame KeyTime='00:00:00.6' KeySpline='.75,0,0,.75' Value='$3'/>"
		xamlString = xamlString + "	 </DoubleAnimationUsingKeyFrames>"
		xamlString = xamlString + "	 </Storyboard>"
		xamlString = xamlString + "	 </BeginStoryboard>"
		xamlString = xamlString + "	 </EventTrigger>"
		xamlString = xamlString + "	 </Canvas.Triggers>"
			
		xamlString = xamlString + "	 <Image Source='assets/images/$2.png' />"
		xamlString = xamlString + "	 <TextBlock Canvas.Top='9' Canvas.Left='$6' FontFamily='Arial' FontSize='34' FontWeight='bold' Text='$1' />"
		xamlString = xamlString + "	 <TextBlock Canvas.Top='36' Canvas.Left='37.5' FontFamily='Arial' FontSize='12' FontWeight='bold' Text='$5' />"
		xamlString = xamlString + "</Canvas>"
		xamlString = xamlString + "</Canvas>"
		

		xamlString = xamlString.replace("$0", str(tileNumber))
		xamlString = xamlString.replace("$1", letter)
		xamlString = xamlString.replace("$2", str(grainIndex))
		xamlString = xamlString.replace("$3", str(top))
		xamlString = xamlString.replace("$4", str(left))
		xamlString = xamlString.replace("$5", str(value))
		xamlString = xamlString.replace("$6", str(letterOffset))
		xamlString = xamlString.replace("$7", beginTime)
		
		tile = Markup.XamlReader.Load(xamlString)
		self.scene.root.Children.Add(tile)

	# Removes the current tiles from the XAML so that a new string can be processed and pushed to the XAML
	def clearTree(self):
		# Remove every child tile...only keep the initial children we started with: button and workaround_canvas
		while self.scene.root.Children.Count >= 2:
			# # remove the last child which must be a tile since the first 2 must be what we started with (button + textbox)
			c = self.scene.root.Children.RemoveAt(self.scene.root.Children.Count-1)

	# value of tile 'A' is the small subscript in the lower right corner of the tile
	# offset of tile 'A' is its starting left position in the tile (offset from leftmost side of tile)
	class tileEntry(object):
		def __init__(self, value, offset):
			self.value = value
			self.offset = offset
	        
	# Initializes the tile entries
	def setupTileEntries(self):
		global tileEntries
		tileEntries=[]
		# 26 tile entries...
		tileEntries.append(self.tileEntry(1, 1)) # A
		tileEntries.append(self.tileEntry(3, 0)) # B
		tileEntries.append(self.tileEntry(3, 0)) # C
		tileEntries.append(self.tileEntry(2, 0)) # D
		tileEntries.append(self.tileEntry(1, 0)) # E
		tileEntries.append(self.tileEntry(4, 0)) # F
		tileEntries.append(self.tileEntry(2, 0)) # G
		tileEntries.append(self.tileEntry(4, 1)) # H
		tileEntries.append(self.tileEntry(1, 8)) # I
		tileEntries.append(self.tileEntry(8, 1)) # J
		tileEntries.append(self.tileEntry(5, 0)) # K
		tileEntries.append(self.tileEntry(1, 2)) # L
		tileEntries.append(self.tileEntry(3, -2)) # M
		tileEntries.append(self.tileEntry(1, 0)) # N
		tileEntries.append(self.tileEntry(1, 0)) # O
		tileEntries.append(self.tileEntry(3, 0)) # P
		tileEntries.append(self.tileEntry(10, -2)) # Q
		tileEntries.append(self.tileEntry(1, 0)) # R
		tileEntries.append(self.tileEntry(1, 0)) # S
		tileEntries.append(self.tileEntry(1, 1)) # T
		tileEntries.append(self.tileEntry(1, 0)) # U
		tileEntries.append(self.tileEntry(4, 1)) # V
		tileEntries.append(self.tileEntry(4, -3)) # W
		tileEntries.append(self.tileEntry(8, 1)) # X
		tileEntries.append(self.tileEntry(4, 2)) # Y
		tileEntries.append(self.tileEntry(10, 2)) # Z
	

TileText()