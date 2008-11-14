#######################################
#
#  pageturn.py
#
# 
# ?2007 Microsoft Corporation. All Rights Reserved.
#
# This file is licensed as part of the Silverlight 2.0 SDK, for details look here: http://go.microsoft.com/fwlink/?LinkID=89144&clcid=0x409
#
#######################################

import math
from System import *
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Media import *
from System.Windows.Input import *
from System.Windows.Markup import XamlReader
from System.Net import *
class PageTurnHandle:
	def __init__(self):
		self.scene = Canvas()
		Application.LoadComponent(self.scene, Uri('app.xaml', UriKind.Relative))
		Application.Current.RootVisual = self.scene
		#self.scene.Load += self.handleLoad()
	@staticmethod	
	def getTwoDigitInt(number):
		return '%02d' % number
	@staticmethod
	def getBrush(color):
		return SolidColorBrush(Color.FromArgb(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), int(color[6:8], 16)))

	class PageTurn:
		def __init__(self, maxNumPages,scene):
			self.maxNumPages = maxNumPages
			self.scene=scene

		def handleLoad(self):
			self.currentDownload = 0   # Current resource to be downloaded  
	        
			# create NavigationManager
			self.navigationManager =PageTurnHandle.NavigationManager(self.maxNumPages,self.scene)
	        
			# create InkManager element that controls the mouseCaptureCanvas
			self.inkManager = PageTurnHandle.InkManager(self.navigationManager,self.scene)
	        
			_annotateToggleButton =  PageTurnHandle.InkToggleButton("Annotate", self.inkManager.toggleInkMode, self.inkManager.toggleInkMode)
			self.scene.inkButtonCanvas.Children.Add(_annotateToggleButton.XamlElement)
	        
			_clearAnnotationButton =  PageTurnHandle.InkButton("Clear Annotations", self.inkManager.clearInk)
			_clearAnnotationButton.XamlElement.SetValue(Canvas.LeftProperty, Double(74))
			self.scene.inkButtonCanvas.Children.Add(_clearAnnotationButton.XamlElement)
	        
			# create PageGenerator
			self.pageGenerator =  PageTurnHandle.PageGenerator(self.maxNumPages)
	        
			# Begin downloading all assets
			for i in xrange(0,len(self.pageGenerator.resourceArray)):
				self.downloadAssets()
				self.currentDownload += 1
			
			# Add pages and thumbnails
			self.addOddPages()
			self.addEvenPages()
			# initialize dragging elements
			self.navigationManager.beginPageAnimation("showFold")
			self.navigationManager.updateScene(1, 380)
			# Hook up thumbnail viewer (page browser control)
			PageTurnHandle.PageBrowserControl(self.scene.pageBrowserControl, self.pageGenerator, self.navigationManager, self.maxNumPages)

		def downloadAssets(self):
			self.webClient=WebClient()
			#self.webClient.DownloadProgressChanged += DownloadProgressChangedEventHandler(self.webClient_DownloadProgressChanged)
			self.webClient.OpenReadCompleted  += OpenReadCompletedEventHandler(self.webClient_OpenReadCompleted)
			self.webClient.OpenReadAsync(Uri(self.pageGenerator.resourceArray[self.currentDownload], UriKind.Relative))

		#def webClient_DownloadProgressChanged(self, sender, args):
			#self.scene.progressRect.Width = DownloadProgressChangedEventArgs.ProgressPercentage 
			#pass
			
		def webClient_OpenReadCompleted(self, sender, e):
			pass
			#if self.currentDownload < len(self.pageGenerator.resourceArray):
				#self.scene.progressText.Text = "Downloading: " + self.pageGenerator.resourceArray[self.currentDownload]
			#else:
				# Hide progress UI
				#self.scene.fadeDownloadUI.Begin()
				#self.scene.downloadUI.IsHitTestVisible = False



		#create and Add the pages on the left hand side of the book
		def addOddPages(self):
			# this is the template for all odd pages
			oddStr = '''
				<Canvas x:Name='page0$0' xmlns='http://schemas.microsoft.com/client/2007' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'>
				  <Canvas.RenderTransform>
					<TransformGroup>
					  <RotateTransform x:Name='page$0Rotate' CenterX='0' CenterY='570' Angle='0'/>
					  <TranslateTransform x:Name='page$0Translate' X='0' Y='0'/>
					</TransformGroup>
				  </Canvas.RenderTransform>
				  <Canvas.Clip>
					<PathGeometry>
					  <PathFigure>
						<LineSegment Point='0,570'/>
						<LineSegment x:Name='page$0Point1' Point='0, 570'/>
						<LineSegment x:Name='page$0Point2' Point='0, 570'/>
						<LineSegment x:Name='page$0Point3' Point='0, 570'/>
						<LineSegment Point='0,570'/>
					  </PathFigure>
					</PathGeometry>
				  </Canvas.Clip>
				  $1
				  <InkPresenter x:Name='page$0ip' Width='420' Height='570' Canvas.Left='0' Canvas.Top='0' />
				  <Rectangle Height='1000' Width='20' Opacity='0.6' x:Name='page$0FoldShadow'>
					<Rectangle.RenderTransform>
					  <TransformGroup>
						<RotateTransform x:Name='page$0FoldShadowRotate' CenterX='0' CenterY='0' Angle='0'/>
						<TranslateTransform x:Name='page$0FoldShadowTranslate' X='0' Y='0'/>
					  </TransformGroup>
					</Rectangle.RenderTransform>
					<Rectangle.Fill>
					  <LinearGradientBrush StartPoint='0,0' EndPoint='1,0'>
						<GradientStop Color='#00000000' Offset='0'/>
						<GradientStop Color='#FF000000' Offset='1'/>
					  </LinearGradientBrush>
					</Rectangle.Fill>
				  </Rectangle>
				</Canvas>'''

			# if maxNumPages is odd, we will ignore the last page, so last odd is two behind
			if self.maxNumPages % 2 == 0:
				_lastOdd = self.maxNumPages - 1
			else:
				_lastOdd = self.maxNumPages - 2

			for i in xrange(1, _lastOdd+1, 2):
				# $0: two digit index of this page
				newOddPageStr = oddStr.replace('$0', PageTurnHandle.getTwoDigitInt(i))
				newOddPageStr = newOddPageStr.replace('$1', self.pageGenerator.getPageString(i))
				newOddPage = XamlReader.Load(newOddPageStr)

				# hook up event handlers for the odd pages
				newOddPage.MouseLeftButtonDown += self.navigationManager.oddPageMouseDown
				newOddPage.MouseLeftButtonUp += self.navigationManager.oddPageMouseUp
				newOddPage.MouseMove += self.navigationManager.oddPageMouseMove

				# Add this odd page to the scene
				self.scene.oddPageCanvas.Children.Add(newOddPage)

		#create and Add the pages on the right hand side of the book
		def addEvenPages(self):
			 # this is the template for all even pages
			evenStr = '''
				<Canvas x:Name='page0$0' xmlns='http://schemas.microsoft.com/client/2007' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'>
					<Canvas.Clip>
					<PathGeometry>
					<PathFigure>
						<LineSegment Point='0,0'/>
						<LineSegment Point='0, 570'/>
						<LineSegment x:Name='page$0Point1' Point='420, 570'/>
						<LineSegment x:Name='page$0Point2' Point='420, 570'/>
						<LineSegment x:Name='page$0Point3' Point='420, 0'/>
						<LineSegment Point='0,0'/>
					</PathFigure>
					</PathGeometry>
				</Canvas.Clip>
				$1
				<InkPresenter x:Name='page$0ip' Width='420' Height='570' Canvas.Left='0' Canvas.Top='0'/>
				$2
				</Canvas>'''
	        
			foldShadowStr = '''
				<Rectangle Height='570' Width='30' Opacity='0.2'>
				<Rectangle.Fill>
				<LinearGradientBrush StartPoint='0,0' EndPoint='1,0'>
					<GradientStop Color='#BBFFFFFF' Offset='0'/>
					<GradientStop Color='#00FFFFFF' Offset='1'/>
				</LinearGradientBrush>
				</Rectangle.Fill>
				</Rectangle>'''

			# if maxNumPages is odd, we will ignore the last page, so last odd is two behind
			if self.maxNumPages % 2 == 0:
				_lastEven = self.maxNumPages
			else:
				_lastEven = self.maxNumPages - 1

			for i in xrange(_lastEven, -1, -2):
				# $0: index of this page
				newEvenPageStr = evenStr.replace('$0', PageTurnHandle.getTwoDigitInt(i))
				newEvenPageStr = newEvenPageStr.replace('$1', self.pageGenerator.getPageString(i))
				if i == 0:
					newEvenPageStr = newEvenPageStr.replace('$2', "")
				else:
					newEvenPageStr = newEvenPageStr.replace('$2', foldShadowStr)

				newEvenPage = XamlReader.Load(newEvenPageStr)
				self.scene.evenPageCanvas.Children.Add(newEvenPage)
	    
	# Entry point from XAML
	def handleLoad(self):
		scene1 = self.PageTurn(18,self.scene)
		scene1.handleLoad()

	# Controls the content for each page and the set of resources required by them
	class PageGenerator:
		def __init__(self, numPages):
			self.numPages = numPages
			self.resourceArray = ["assets/images/logo_name.png", "assets/images/SilverlightBackgroundLight.jpg"]
			self.resourceArray += ["assets/images/page" + PageTurnHandle.getTwoDigitInt(i) + ".jpg" for i in xrange(5, self.numPages+1)]        
			self.resourceArray += ["assets/images/logo.png"]

		def getPageString(self, pageNumber, isThumbnail=False):
			retStr = ""
			if pageNumber < 0:
				return retStr
	      
			retStr =  "<Canvas>"
			if pageNumber == 0:
				retStr += '''
				<Rectangle Height='570' Width='420' Stretch='Fill'>
					<Rectangle.Fill>
					<LinearGradientBrush StartPoint='0,1' EndPoint='1,0'>
						<GradientStop Color='#FF888888' Offset='0'/>
						<GradientStop Color='#FFFFFFFF' Offset='1'/>
					</LinearGradientBrush>
					</Rectangle.Fill>
				</Rectangle>
					<Image Height='570' Width='420' Source='assets/images/SilverlightBackgroundLight.jpg' Stretch='Fill'/>
					<Image Canvas.Top='50' Canvas.Left='261' Source='assets/images/logo_name.png' Stretch='Fill'/>
					<TextBlock Canvas.Top='90' Canvas.Left='246' Text='PageTurn Sample' FontSize='20'/>
				</Canvas>'''
				return retStr
			elif pageNumber == 1:
				retStr += '''<Image Height='570' Width='420' Source='assets/images/SilverlightBackgroundDark.jpg' Stretch='Fill'/>
				<TextBlock Canvas.Left='30' Canvas.Top='30' Text='Santorini, Greece...' FontSize='30' Foreground='White' Opacity='1'/>'''  
			elif pageNumber == 2:  
				retStr += '''<Rectangle Height='570' Width='420' Stretch='Fill' Fill='#77FFFFFF'>
				</Rectangle>
				<Ellipse Height='276' Width='276' Canvas.Top='76' Canvas.Left='70' Stretch='Fill'>
				<Ellipse.Fill>
				<RadialGradientBrush >
					<GradientStop Color='#FFFFFFFF' Offset='0'/>
					<GradientStop Color='#FFFFFFFF' Offset='0.3'/>
					<GradientStop Color='#00FFFFFF' Offset='1'/>
				  </RadialGradientBrush>
				</Ellipse.Fill>
				</Ellipse>
				<Image Canvas.Top='150' Canvas.Left='138' Source='assets/images/logo.png' Stretch='Fill'/>'''  
			elif pageNumber == 3:  
				retStr += '''<Image Canvas.Top='150' Canvas.Left='282' Source='assets/images/logo.png' Stretch='Fill'>
				<Image.RenderTransform>
				  <ScaleTransform ScaleX='-1'/>
				</Image.RenderTransform>
				</Image>
				<Ellipse Height='276' Width='276' Canvas.Top='76' Canvas.Left='74' Stretch='Fill'>
				<Ellipse.Fill>
				  <RadialGradientBrush >
					<GradientStop Color='#FFFFFFFF' Offset='0'/>
					<GradientStop Color='#FFFFFFFF' Offset='0'/>
					<GradientStop Color='#00FFFFFF' Offset='1'/>
				  </RadialGradientBrush>
				</Ellipse.Fill>
				</Ellipse>
				<Rectangle Height='570' Width='420' Stretch='Fill' Fill='#77FFFFFF'>
				</Rectangle>'''
			elif pageNumber == 4:  
				retStr += '''<Image Height='570' Width='420' Source='assets/images/SilverlightBackgroundDark.jpg' Stretch='Fill'>
				<Image.RenderTransform>
				  <TransformGroup>
					<ScaleTransform ScaleX='-1'/>
					<TranslateTransform X='420'/>
				  </TransformGroup>
				</Image.RenderTransform>
				</Image>
				<TextBlock Canvas.Left='80' Canvas.Top='480' Text='... brought to you by:' FontSize='30' Foreground='White' Opacity='1'/>'''  
			elif pageNumber == 18:
				retStr += '''<Image Height='570' Width='420' Source='assets/images/page'''+PageTurnHandle.getTwoDigitInt(pageNumber)+'''.jpg'/>
				<Ellipse Height='120' Width='120' Canvas.Top='440' Canvas.Left='283' Stretch='Fill'>
				<Ellipse.Fill>
				  <RadialGradientBrush >
					<GradientStop Color='#FFFFFFFF' Offset='0'/>
					<GradientStop Color='#FFFFFFFF' Offset='0.4'/>
					<GradientStop Color='#00FFFFFF' Offset='1'/>
				  </RadialGradientBrush>
				</Ellipse.Fill>
				</Ellipse>
				<Image Height='80' Canvas.Top='460' Canvas.Left='310' Source='assets/images/logo.png' Stretch='Fill'/>'''  
			else:
				retStr += "  <Image Height='570' Width='420' Source='assets/images/page"+PageTurnHandle.getTwoDigitInt(pageNumber)+".jpg'/>"
	      
			if (pageNumber % 2) == 1:
				retStr += "  <Path Data='M 420,570 h -420 v -570 h 420' Stroke='White' StrokeThickness='15'/>"
			else:
				retStr += "  <Path Data='M 0,0 h 420 v 570 h -420' Stroke='White' StrokeThickness='15'/>"
	      
			retStr += "</Canvas>"
			return retStr

	# Controls the navigation between pages, and keeps up-to-date state
	class NavigationManager:
		def __init__(self, maxNumPages,scene):
			self.maxNumPages = maxNumPages
			self.scene=scene
	        
			self.timer = self.scene.timerStoryboard
			self.timer.Completed += self.onTick
	        
			# animation variables
			self.pageAnimationType = "none"
			self.pageAnimationDelta = 0.0
			self.pageAnimationTarget = 0.0
	        
			# whether to track movement, and previous position if so
			self.trackMovement = False
			self.previousMouseMovePosition = 0.0
	        
			self.currX1 = 880.0
			self.nextOddPage = 1

		def beginPageAnimation(self, type):
			if type == "showFold":
				if self.nextOddPage < self.maxNumPages:
					self.pageAnimationType = "showFold"
					self.pageAnimationTarget = 840.0
					self.pageAnimationDelta = 5.0
					self.timer.Begin()
			elif type == "hideFold":
				self.pageAnimationType = "hideFold"
				self.pageAnimationTarget = 880.0
				self.pageAnimationDelta = math.fabs(self.currX1 - self.pageAnimationTarget)
				self.timer.Begin()
			elif type == "finishTurn":
				if self.nextOddPage < self.maxNumPages:
					self.pageAnimationType = "finishTurn"
					self.pageAnimationDelta = 10.0
					self.pageAnimationTarget = 460.0
					self.timer.Begin()
			elif type == "none":
				self.pageAnimationType = "none"
				self.pageAnimationDelta = 0.0
				self.pageAnimationTarget = 0.0

		# method that ensures animations maintain correct state once they complete
		def onAnimationComplete(self, type):
			if type == "showFold":
				self.pageAnimationType = "none"
			elif type == "hideFold":
				self.currX1 = 460.0
				self.nextOddPage -= 2
				self.pageAnimationType = "none"
			elif type == "finishTurn":
				self.currX1 = 880.0
				self.nextOddPage += 2
				self.pageAnimationType = "none"
				self.beginPageAnimation("showFold")

		def onTick(self, sender, eventArgs):
			# if we're animating
			if self.pageAnimationType != "none":          
				# if we are done with the current animation
				if self.currX1 - self.pageAnimationTarget == 0:            
					self.onAnimationComplete(self.pageAnimationType)            
				# if we are not done with the current animation
				else:            
					# if we are within a delta of the target, draw one last frame with the final value
					if math.fabs(self.currX1 - self.pageAnimationTarget) < self.pageAnimationDelta:
						self.currX1 = self.pageAnimationTarget 
					elif self.currX1 < self.pageAnimationTarget:
						self.currX1 += self.pageAnimationDelta 
					else:
						self.currX1 -= self.pageAnimationDelta 
					self.timer.Begin()            

				# update the scene if possible
				if self.nextOddPage < self.maxNumPages:
					self.updateScene(self.nextOddPage, self.currX1 - 460)

		def oddPageMouseDown(self, sender, eventArgs):
			sender.CaptureMouse()
			self.trackMovement = True
			self.previousMouseMovePosition = eventArgs.GetPosition(None).X

			# if user clicked on a page that has fully turned
			if "page0"+PageTurnHandle.getTwoDigitInt(self.nextOddPage) != sender.Name:        
				if self.nextOddPage < self.maxNumPages:            
					self.beginPageAnimation("hideFold")            
				else:            
					self.onAnimationComplete("hideFold")
			else:
				self.pageAnimationType = "none"

		def oddPageMouseUp(self, sender, eventArgs):
			sender.ReleaseMouseCapture()
			self.trackMovement = False

			# if we are far enough to the left, finish the turn
			if self.currX1 < 600:
				self.beginPageAnimation("finishTurn")
			# otherwise, go back to the folded position
			else:
				self.beginPageAnimation("showFold")

		def oddPageMouseMove(self, sender, eventArgs):
			# if we have an animation pending, don't animate
			if (self.trackMovement) and (self.pageAnimationType == "none"):
				_currDelta = (eventArgs.GetPosition(None).X - self.previousMouseMovePosition)*1.05
				self.previousMouseMovePosition = eventArgs.GetPosition(None).X
				self.currX1 = min(880.0, max(460.0, self.currX1 + _currDelta))
				self.updateScene(self.nextOddPage, self.currX1 - 460)
	          
			  # if we are tracking movement but in the middle of an animation, update mouse position
			elif self.trackMovement:          
				self.previousMouseMovePosition = eventArgs.GetPosition(None).X

		def jumpToPage(self, newOddPage):
			# cancel all animations
			self.beginPageAnimation("none")

			# goal is self.nextOddPage == newOddPage + 2
			if self.nextOddPage == newOddPage + 2:
				return

			# if we need to go backwards
			if self.nextOddPage > newOddPage + 2:
				if self.nextOddPage > self.maxNumPages:
					self.nextOddPage -= 2

				while (self.nextOddPage > newOddPage + 2) and (self.nextOddPage >= 1):
					self.currX1 = 880.0
					self.updateScene(self.nextOddPage, self.currX1 - 460)
					self.nextOddPage -= 2

				# if our goal is a valid page
				if self.nextOddPage >= 1:
					self.currX1 = 880.0
					self.updateScene(self.nextOddPage, self.currX1 - 460)
				else:
					self.nextOddPage = 1
	            
				self.beginPageAnimation("showFold")
	      
			# if we need to go forward
			else:
				while (self.nextOddPage < newOddPage + 2) and (self.nextOddPage < self.maxNumPages):
					self.currX1 = 460.0
					self.updateScene(self.nextOddPage, self.currX1 - 460)
					self.nextOddPage += 2

				# if our goal is a valid page
				if self.nextOddPage < self.maxNumPages:
					self.currX1 = 880.0
					self.updateScene(self.nextOddPage, self.currX1 - 460)
					self.beginPageAnimation("showFold")

		# @oddPageNumber: number of the odd page that is currently the next
		# @x1: point where the bottom edges of the odd and even pages intersect, in even page coordinates.  Ranges from 0 to 420.
		def updateScene(self, oddPageNumber, x1):
			# variables related to odd page
			oddPoint1 = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "Point1")
			oddPoint2 = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "Point2")
			oddPoint3 = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "Point3")
			oddRotate = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "Rotate")
			oddTranslate = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "Translate")
			foldShadow = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "FoldShadow")
			foldShadowRotate = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "FoldShadowRotate")
			foldShadowTranslate = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber) + "FoldShadowTranslate")

			# variables related to the even page
			evenPoint1 = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber-1) + "Point1")
			evenPoint2 = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber-1) + "Point2")
			evenPoint3 = MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(oddPageNumber-1) + "Point3")

			# _alpha: angle between horizontal axis and bottom edge of odd page.
			#        this can be any function of x1.
			_alpha = 90.0/420*x1

			# update point 1 of even page
			evenPoint1.Point = Point(x1, 570)
			shadowPts=PointCollection()
			shadowPts.Add(Point(x1 ,570))
			shadowPts.Add(Point(min((x1 + 30), 420), 570))

			# _leftEdgeAngle: angle between horizontal axis and left edge of odd page
			_leftEdgeAngle = 90 - _alpha
			_bottomLeftCornerX = x1 - math.cos(_alpha*math.pi/180) * (420 - x1)
			_bottomLeftCornerY = math.sin(_alpha*math.pi/180) * (420 - x1)

			# update odd page's rotate and translate transform
			oddRotate.Angle = _alpha
			oddTranslate.X = 420 + _bottomLeftCornerX
			oddTranslate.Y = (-1) * _bottomLeftCornerY

			# how much of the odd page's left edge can be seen
			_visibleLeftEdgeHeight = (420 - _bottomLeftCornerX) / math.cos(_leftEdgeAngle*math.pi/180)

			# if the top left corner can be seen
			if _visibleLeftEdgeHeight >= 570:      
				# height between top left corner of the odd page and top edge of the even page
				_topLeftCornerY = _bottomLeftCornerY + math.sin(_leftEdgeAngle*math.pi/180)*570

				# _visibleTopEdgeWidth: Width of top edge of odd page that is visible
				# _x2: x coordinate of the point where top edges of odd and even pages intersect
				if _topLeftCornerY > 570:        
					_visibleTopEdgeWidth = (_topLeftCornerY - 570) / math.sin(_alpha*math.pi/180)
					_x2 = _bottomLeftCornerX + math.cos(_leftEdgeAngle*math.pi/180)* 570 + (_topLeftCornerY - 570)/math.tan(_alpha*math.pi/180)        
				else:        
					_visibleTopEdgeWidth = 420
					_x2 = 0

				oddPoint1.Point = Point(0, 0)
				oddPoint2.Point = Point(_visibleTopEdgeWidth, 0)

				# update foldShadow properties
				_foldAngle = 90 - (180/math.pi)*math.atan2(570, 420 - x1 - _visibleTopEdgeWidth)
				foldShadowRotate.Angle = -_foldAngle

				# need to adjust the position of the foldShadow so that it covers the entire folded edge
				_foldShadowAdjustment = 40.0
				foldShadowTranslate.X = _visibleTopEdgeWidth - 20 * math.cos(_foldAngle*math.pi/180) - _foldShadowAdjustment*math.cos((90 - _foldAngle)*math.pi/180)
				foldShadowTranslate.Y =  20 * math.sin(_foldAngle*math.pi/180) - _foldShadowAdjustment*math.sin((90 - _foldAngle)*math.pi/180)

				evenPoint2.Point = Point(_x2, 0)
				evenPoint3.Point = Point(_x2, 0)
				shadowPts.Add( Point(min((_x2+10), 420), 0))
				shadowPts.Add( Point(_x2, 0))
	      
			# if the top left corner cannot be seen
			else:
				# update points of the odd page, which are both the same
				oddPoint1.Point = Point(0, 570 - _visibleLeftEdgeHeight)
				oddPoint2.Point = Point(0, 570 - _visibleLeftEdgeHeight)

				# update points of the even page
				_y2 = 570 - _bottomLeftCornerY - (420 - _bottomLeftCornerX) * math.tan(_leftEdgeAngle*math.pi/180)
				evenPoint2.Point = Point(420, _y2)
				evenPoint3.Point = Point(420, 0)

				# update shadow string on top of the even page
				shadowPts.Add( Point(420, _y2))
				shadowPts.Add( Point(420, _y2))

				# update foldShadow properties
				_foldAngle = 90 - (180/math.pi)*math.atan2(_visibleLeftEdgeHeight, 420 - x1)

				foldShadowRotate.Angle = - _foldAngle
				foldShadowTranslate.X = -20 * math.cos(_foldAngle*math.pi/180) 
				foldShadowTranslate.Y =  (570 - _visibleLeftEdgeHeight) +  20 * math.sin(_foldAngle*math.pi/180) 

			oddPoint3.Point = Point(420 - x1, 570)
			self.scene.shadowOnEvenPage.Points = shadowPts

			if x1 < 15:      
				self.scene.shadowOnEvenPage.Opacity = 0.25*(x1/15.0)
				#foldShadow.Opacity = 0.6*(x1/15)
				if oddPageNumber > 1:
					self.scene.shadowBehindPage01.Opacity = 0.8 
				else:
					self.scene.shadowBehindPage01.Opacity = 0.8 - 0.8*(x1/15.0)   
			else:
				self.scene.shadowOnEvenPage.Opacity = 0.25
				#foldShadow.Opacity = 0.6
				if oddPageNumber > 1:
					self.scene.shadowBehindPage01.Opacity = 0.8 
				else:
					self.scene.shadowBehindPage01.Opacity = 0.0

	# Thumbnail object keeps track of whether mouse is over it, it whether it has mousecapture
	class Thumbnail:
		#   $index: index of this thumbnail.  Starts at 0.
		#   $pageGenerator: object from which this thumbnail should get its content representation.
		def __init__(self, pageGenerator, index, clickHandler):
			self.index = index
			self.clickHandler = clickHandler

			# this is the template for all thumbnails, given the following variables
			# $2: UIElement corresponding to the left page of this thumbnail
			# $3: UIElement corresponding to the right page of this thumbnail
			_str = '''
				<Canvas xmlns='http://schemas.microsoft.com/client/2007' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml' Canvas.Top='42' x:Name='thumb' Opacity='0.5'>
				  <Canvas.Resources>
						<Storyboard BeginTime='0' Duration='Forever' FillBehavior='Stop' x:Name='storyZoomIn'>
						  <DoubleAnimationUsingKeyFrames BeginTime='00:00:00' Storyboard.TargetProperty='ScaleX' Storyboard.TargetName='scale'>
							<SplineDoubleKeyFrame KeySpline='0.7,0,0.4,1' Value='0.25' KeyTime='00:00:00.3'/>
						  </DoubleAnimationUsingKeyFrames>
						  <DoubleAnimationUsingKeyFrames BeginTime='00:00:00' Storyboard.TargetProperty='ScaleY' Storyboard.TargetName='scale'>
							<SplineDoubleKeyFrame KeySpline='0.7,0,0.4,1' Value='0.25' KeyTime='00:00:00.3'/>
						  </DoubleAnimationUsingKeyFrames>
						  <DoubleAnimationUsingKeyFrames BeginTime='00:00:00' Storyboard.TargetProperty='Y' Storyboard.TargetName='pos'>
							<SplineDoubleKeyFrame KeySpline='0.7,0,0.4,1' Value='-30' KeyTime='00:00:00.3'/>
						  </DoubleAnimationUsingKeyFrames>
						  <DoubleAnimationUsingKeyFrames BeginTime='00:00:00' Storyboard.TargetProperty='Opacity' Storyboard.TargetName='thumb'>
							<SplineDoubleKeyFrame KeySpline='0.7,0,0.4,1' Value='1' KeyTime='00:00:00.3'/>
						  </DoubleAnimationUsingKeyFrames>
						</Storyboard>
				  </Canvas.Resources>
				  <Rectangle x:Name='thumbBackground' Height='44' Width='63' Fill='#37FFFFFF' Opacity='1' Canvas.Left='-31' Canvas.Top='-42'/>
				  <Canvas>
					<Canvas.RenderTransform>
					  <TransformGroup>
						<ScaleTransform x:Name='scale' ScaleX='0.07' ScaleY='0.07'/>
						<TranslateTransform x:Name='pos' X='0' Y='0'/>
					  </TransformGroup>
					</Canvas.RenderTransform>
					<Rectangle x:Name='thumbOver' Height='630' Width='900' Fill='#66000000' Opacity='0' Canvas.Top='-600' Canvas.Left='-450'/>
					<Canvas Canvas.Top='-570' Canvas.Left='-420'>
					  $2
					</Canvas>
					<Canvas Canvas.Top='-570' Canvas.Left='0'>
					  $3
					</Canvas>
				  </Canvas>
				</Canvas>'''

			# $2, $3: UIElements corresponding to the left and right pages, respectively, of this thumbnail
			thumbStr = _str.replace('$2', pageGenerator.getPageString(2*self.index-1, True))
			thumbStr = thumbStr.replace('$3', pageGenerator.getPageString(2*self.index, True))

			# create XAML thumbnail using createFromXaml
			self.XamlElement = XamlReader.Load(thumbStr)
	        
			# attach event handlers for the thumbnail
			self.XamlElement.MouseEnter += self.handleMouseEnter
			self.XamlElement.MouseLeave += self.handleMouseLeave
			self.XamlElement.MouseLeftButtonDown += self.handleMouseDown
			self.XamlElement.MouseLeftButtonUp += self.handleMouseUp
	        
			# initialize mouse state
			self.isMouseOver = False
			self.isMouseDown = False

		def handleMouseEnter(self, sender, eventArgs):
			if not self.isMouseDown:        
				# ensure current thumbnail is on top
				self.XamlElement.SetValue(Canvas.ZIndexProperty, 1)

				# zoom in thumbnail
				self.XamlElement.FindName("storyZoomIn").Begin()
				self.XamlElement.FindName("thumbOver").Opacity = 1
			else:
				# go back to pressed down state
				self.XamlElement.FindName("thumbOver").Fill = PageTurnHandle.getBrush("6623A3E0")
				self.XamlElement.FindName("thumbBackground").Fill = PageTurnHandle.getBrush("3723A3E0")
	        
			self.isMouseOver = True

		def handleMouseLeave(self, sender, eventArgs):
			if not self.isMouseDown:
				# ensure current thumbnail is not on top
				self.XamlElement.SetValue(Canvas.ZIndexProperty, 0)
	            
				# Stop storyboard and minimize thumbnail
				self.XamlElement.FindName("storyZoomIn").Stop()
				self.XamlElement.FindName("thumbOver").Opacity = 0        
			else:        
				# if we were highlighted, go back to mouse over state since we have mouse capture
				self.XamlElement.FindName("thumbOver").Fill = PageTurnHandle.getBrush("66000000")
				self.XamlElement.FindName("thumbBackground").Fill = PageTurnHandle.getBrush("37FFFFFF")
	        
			self.isMouseOver = False

		def handleMouseDown(self, sender, eventArgs):
			self.XamlElement.FindName("thumbOver").Fill = PageTurnHandle.getBrush("6623A3E0")
			self.XamlElement.FindName("thumbBackground").Fill = PageTurnHandle.getBrush("3723A3E0")
	        
			sender.CaptureMouse()
			self.isMouseDown = True
			self.isPageBrowserScrolling = False

		def handleMouseUp(self, sender, eventArgs):
			if self.isMouseOver:
				if self.clickHandler:
					self.clickHandler(self)

			# ensure current thumbnail is not on top
			self.XamlElement.SetValue(Canvas.ZIndexProperty, 0)
	        
			# minimize this thumbnail
			self.XamlElement.FindName("storyZoomIn").Stop()
			self.XamlElement.FindName("thumbOver").Fill = PageTurnHandle.getBrush("66000000")
			self.XamlElement.FindName("thumbOver").Opacity = 0
			self.XamlElement.FindName("thumbBackground").Fill = PageTurnHandle.getBrush("37FFFFFF")

			sender.ReleaseMouseCapture()
			self.isMouseDown = False

	# InkToggleButton and InkButton Classes

	# Controls the Annotations for the PageTurn app
	class InkToggleButton:
		def __init__(self, text, checkedHandler, uncheckedHandler):
			# create XAML string
			_str = '''
				<Canvas xmlns="http://schemas.microsoft.com/client/2007" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
					<TextBlock Height="19" Width="64" Canvas.Top="2" Canvas.Left="4" x:Name="toggleButtonText" Foreground="gray" FontFamily="Verdana" FontSize="12" TextWrapping="Wrap"/>
					<Rectangle Height="19" Width="0" x:Name="toggleButtonRectangle" Stroke="gray" Fill="transparent" StrokeThickness="1.5"  RadiusX="4" RadiusY="4" Opacity="1"/>
				</Canvas>'''
	        
			# create XAML thumbnail using createFromXaml
			self.XamlElement = XamlReader.Load(_str)
	        
			self.rectangle = self.XamlElement.FindName("toggleButtonRectangle")
			self.TextBlock = self.XamlElement.FindName("toggleButtonText")
			self.TextBlock.Text = text
			self.rectangle.Width = self.TextBlock.ActualWidth + 8
	      
			self.checkedHandler = checkedHandler
			self.uncheckedHandler = uncheckedHandler
	        
			self.currentState = "unchecked"
			self.isMouseOver = False
			self.isMouseDown = False
	        
			# Register eventhandlers
			self.XamlElement.MouseEnter += self.handleMouseEnter
			self.XamlElement.MouseLeave += self.handleMouseLeave
			self.XamlElement.MouseLeftButtonDown += self.handleMouseDown

		def handleMouseEnter(self, s, e): 
			self.rectangle.StrokeThickness = 2.5
			self.isMouseOver = True

		def handleMouseLeave(self, s, e): 
			self.rectangle.StrokeThickness = 1.5
			self.isMouseOver = False

		def handleMouseDown(self, s, e): 
			# toggle button state
			if self.currentState == "unchecked":
				self.currentState = "checked"
				self.TextBlock.Foreground = SolidColorBrush(Colors.White)
				self.rectangle.Stroke = SolidColorBrush(Colors.White)

				if self.checkedHandler:
					self.checkedHandler()
	            
			else:
				self.currentState = "unchecked"
				self.TextBlock.Foreground = SolidColorBrush(Colors.Gray)
				self.rectangle.Stroke = SolidColorBrush(Colors.Gray)
	            
				if self.uncheckedHandler:
					self.uncheckedHandler()

	class InkButton:
		def __init__(self, text, clickedHandler):
			# create XAML string
			_str =    '''
				<Canvas xmlns="http://schemas.microsoft.com/client/2007" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
					<TextBlock Height="19" Canvas.Top="2" Canvas.Left="4" x:Name="buttonText" Foreground="White" FontFamily="Verdana" FontSize="12" TextWrapping="Wrap"/>
					<Rectangle Height="19" Width="0" x:Name="buttonRectangle" Stroke="White" Fill="transparent" StrokeThickness="1.5"  RadiusX="4" RadiusY="4" Opacity="1"/>
				</Canvas>'''
	        
			# create XAML thumbnail using createFromXaml
			self.XamlElement = XamlReader.Load(_str)
	        
			self.rectangle = self.XamlElement.FindName("buttonRectangle")
			self.TextBlock = self.XamlElement.FindName("buttonText")
			self.TextBlock.Text = text
			self.rectangle.Width = self.TextBlock.ActualWidth + 8
	      
			self.clickedHandler = clickedHandler
	            
			# Register eventhandlers
			self.XamlElement.MouseEnter += self.handleMouseEnter
			self.XamlElement.MouseLeave += self.handleMouseLeave
			self.XamlElement.MouseLeftButtonDown += self.handleMouseDown

		def handleMouseEnter(self, s, e): 
			self.rectangle.StrokeThickness = 2.5

		def handleMouseLeave(self, s, e): 
			self.rectangle.StrokeThickness = 1.5

		def handleMouseDown(self, s, e): 
			self.TextBlock.Foreground = SolidColorBrush(Colors.White)
			self.rectangle.Stroke = SolidColorBrush(Colors.White)

			if self.clickedHandler:
				self.clickedHandler()

	# Controls the state of the ink annotation system
	class InkManager:
		def __init__(self, navigationManager,scene):
			# need the navigation manager to obtain the number of the current ink canvas to draw on.
			self.scene=scene
			self.navigationManager = navigationManager
	        
			self.mouseCaptureCanvas = self.scene.mouseCaptureCanvas
	        
			self.inkingMode = False
			self.newStroke = None
			self.newStroke2 = None
			self.inkThickness = 4
			self.inkColor = Colors.White
			self.inkColorContrast = Colors.Black
	        
			# Register eventhandlers
			self.mouseCaptureCanvas.MouseLeave += self.handleMouseLeave
			self.mouseCaptureCanvas.MouseLeftButtonDown += self.handleMouseDown
			self.mouseCaptureCanvas.MouseLeftButtonUp += self.handleMouseUp
			self.mouseCaptureCanvas.MouseMove += self.handleMouseMove

		def toggleInkMode(self):
			self.inkingMode = not self.inkingMode
			if self.inkingMode:
				self.mouseCaptureCanvas.IsHitTestVisible = True
			else:
				self.mouseCaptureCanvas.IsHitTestVisible = False

		def clearInk(self):
			if self.navigationManager.nextOddPage > 1:
				inkPresenter1 =MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(self.navigationManager.nextOddPage-2) + "ip")
				inkPresenter1.Strokes.Clear()
	      
			inkPresenter2 =MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(self.navigationManager.nextOddPage-1) + "ip")
			inkPresenter2.Strokes.Clear()

		def handleMouseLeave(self, sender, args):
			self.newStroke = None   # Stop inking the current stroke if the mouse/stylus leaves the control area
			self.newStroke2 = None

		def handleMouseDown(self, sender, args):
			if self.inkingMode:      
				sender.CaptureMouse()
				inkPresenter =MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(self.navigationManager.nextOddPage-2) + "ip")
				if inkPresenter:             
					self.newStroke = XamlReader.Load("<Stroke xmlns='http://schemas.microsoft.com/client/2007' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'/>")
					stroke=self.newStroke
					inkPresenter.Strokes.Add(self.newStroke)
					self.newStroke.DrawingAttributes.Width = self.inkThickness
					self.newStroke.DrawingAttributes.Height = self.inkThickness
					self.newStroke.DrawingAttributes.Color = self.inkColor
					self.newStroke.DrawingAttributes.OutlineColor = self.inkColorContrast
					self.newStroke.StylusPoints.Add(args.StylusDevice.GetStylusPoints(inkPresenter))

				# Inking Page 2 (copy to other page so you can ink crossing pages)
				inkPresenter2 =MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(self.navigationManager.nextOddPage-1) + "ip")
				if inkPresenter2:
					self.newStroke2 = XamlReader.Load("<Stroke xmlns='http://schemas.microsoft.com/client/2007' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'/>")
					stroke=self.newStroke2
					inkPresenter2.Strokes.Add(self.newStroke2)
					self.newStroke2.DrawingAttributes.Width = self.inkThickness
					self.newStroke2.DrawingAttributes.Height = self.inkThickness
					self.newStroke2.DrawingAttributes.Color = self.inkColor
					self.newStroke2.DrawingAttributes.OutlineColor = self.inkColorContrast
					self.newStroke2.StylusPoints.Add(args.StylusDevice.GetStylusPoints(inkPresenter2))

		def handleMouseUp(self, sender, args):
			self.newStroke = None
			self.newStroke2 = None

		def handleMouseMove(self, sender, args):
			if self.inkingMode:
				if self.newStroke:
					inkPresenter =MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(self.navigationManager.nextOddPage-2) + "ip")
					self.newStroke.StylusPoints.Add(args.StylusDevice.GetStylusPoints(inkPresenter))
	             
				# Inking Page 2
				if self.newStroke2:
					inkPresenter2 =MyFindName(self.scene.MainCanvas.Children,"page" + PageTurnHandle.getTwoDigitInt(self.navigationManager.nextOddPage-1) + "ip")
					if inkPresenter2:
						self.newStroke2.StylusPoints.Add(args.StylusDevice.GetStylusPoints(inkPresenter2))

	# Controls the Button that Opens/Closes Page Browser
	class PageBrowserButton:
		def __init__(self, target, checkedHandler, uncheckedHandler):
			self.target = target
			self.checkedHandler = checkedHandler
			self.uncheckedHandler = uncheckedHandler
	        
			self.pageBrowserButtonCurrentState = "unchecked"
			self.isMouseOver = False
			self.isMouseDown = False
	        
			# Register eventhandlers
			target.MouseEnter += self.handleMouseEnter
			target.MouseLeave += self.handleMouseLeave
			target.MouseLeftButtonDown += self.handleMouseDown
			target.MouseLeftButtonUp += self.handleMouseUp


		def handleMouseEnter(self, s, e): 
			over = self.target.FindName(self.pageBrowserButtonCurrentState + "_over")
			normal = self.target.FindName(self.pageBrowserButtonCurrentState + "_normal")
			down = self.target.FindName(self.pageBrowserButtonCurrentState + "_down")

			if self.isMouseDown:
				normal.Opacity = 0
				over.Opacity = 0      
				down.Opacity = 1
			else:
				normal.Opacity = 0
				over.Opacity = 1

			self.isMouseOver = True

		def handleMouseLeave(self, s, e): 
			over = self.target.FindName(self.pageBrowserButtonCurrentState + "_over")
			normal = self.target.FindName(self.pageBrowserButtonCurrentState + "_normal")
			down = self.target.FindName(self.pageBrowserButtonCurrentState + "_down")

			if self.isMouseDown:
				normal.Opacity = 0
				over.Opacity = 1
				down.Opacity = 0
			else:
				normal.Opacity = 1
				over.Opacity = 0

			self.isMouseOver = False

		def handleMouseDown(self, s, e): 
			over = self.target.FindName(self.pageBrowserButtonCurrentState + "_over")
			down = self.target.FindName(self.pageBrowserButtonCurrentState + "_down")

			down.Opacity = 1
			over.Opacity = 0

			self.isMouseDown = True
			self.target.CaptureMouse()

		def handleMouseUp(self, sender, eventArgs):
			over = self.target.FindName(self.pageBrowserButtonCurrentState + "_over")
			normal = self.target.FindName(self.pageBrowserButtonCurrentState + "_normal")
			down = self.target.FindName(self.pageBrowserButtonCurrentState + "_down")

			if self.isMouseOver:
				# change button state
				if self.pageBrowserButtonCurrentState == "unchecked":
					self.pageBrowserButtonCurrentState = "checked"
					if self.checkedHandler:
						self.checkedHandler(sender, eventArgs)
				else:
					self.pageBrowserButtonCurrentState = "unchecked"
					if self.uncheckedHandler:
						self.uncheckedHandler(sender, eventArgs)

				newover = self.target.FindName(self.pageBrowserButtonCurrentState + "_over")
				newover.Opacity = 1      
				down.Opacity = 0
			else:
				normal.Opacity = 1
				down.Opacity = 0
				over.Opacity = 0

			self.isMouseDown = False
			self.target.ReleaseMouseCapture()

	# Controls the Horizontal Scroll of Thumbnails
	class PageBrowserControl:
		#   $target: pageBrowserControl XAML element
		def __init__(self, target, pageGenerator, navigationManager, maxNumPages):
			self.target = target
			self.navigationManager = navigationManager
			self.maxNumPages = maxNumPages
			button=target.FindName("pageBrowserButton")
			self.pageBrowserButton = target.FindName("pageBrowserButton")
			self.pageBrowserWindow = target.FindName("pageBrowserWindow")
			self.pageBrowser = target.FindName("pageBrowser")
			self.openPageBrowserStoryboard = target.FindName("openPageBrowserSB")
	        
			# create PageBrowserButton
			PageTurnHandle.PageBrowserButton(self.pageBrowserButton, self.onPageBrowserButtonChecked, self.onPageBrowserButtonUnchecked)

			# Register event handlers    
			self.pageBrowserWindow.MouseMove += self.onPageBrowserWindowMouseMove
			self.isPageBrowserScrolling = True
	        
			# create thumbnails
			for i in xrange(0, self.maxNumPages/2 + 1):
				_currThumb = PageTurnHandle.Thumbnail(pageGenerator, i, self.onThumbnailClicked)
				_currThumb.XamlElement.SetValue(Canvas.LeftProperty, Double(i * 70 + 42))
				self.pageBrowser.Children.Add(_currThumb.XamlElement)
		
		def onPageBrowserButtonChecked(self, sender, eventArgs):
			self.openPageBrowserStoryboard.Begin()
			self.pageBrowserWindow.IsHitTestVisible = True

		def onPageBrowserButtonUnchecked(self, sender, eventArgs):
			self.openPageBrowserStoryboard.Stop()
			self.pageBrowserWindow.IsHitTestVisible = False

		def onPageBrowserWindowMouseMove(self, s, e):
			if self.isPageBrowserScrolling:
				_currX = (e.GetPosition(None).X - 74)
				_totalPageBrowserWidth = math.floor(self.maxNumPages/2)*70

			self.pageBrowser.SetValue(Canvas.LeftProperty, Double(350 - (_totalPageBrowserWidth)*(_currX/770)))

		def onThumbnailClicked(self, sender):
			self.navigationManager.jumpToPage((sender.index*2)-1)
			
def MyFindName(collect, name):
	itr = collect.GetEnumerator()
	for i in range(0,collect.Count):
		itr.MoveNext()
		current = itr.Current
		na=current.Name
		o = current.FindName(name)
		if (None == o):
			if(hasattr(current,"Children")):
				obj=MyFindName(current.Children,name)
				if(None==obj ):
					continue
				return obj
			continue
		return o
	return None
PageTurnHandle().handleLoad()