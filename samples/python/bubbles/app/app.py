from System import EventHandler,TimeSpan,Math,Uri,UriKind,Array,DateTime
from System.Windows import *
from System.Windows.Browser import *
from System.Windows.Threading import DispatcherTimer
from System.Threading import *
from System.Windows.Controls import Canvas
from System.Windows.Markup import XamlReader
from System import Threading
from _random import Random

  
class Bubbles:
	def __init__(self):
		self.scene = Canvas()
		Application.LoadComponent(self.scene, Uri('app.xaml', UriKind.Relative))
		Application.Current.RootVisual = self.scene
		self.rootCanvas=0
		
		self.startOnLoad = True
		self.isLoaded = False
		self.numBalls = 128
		self.wpfeTest = Bubbles.WPFETest(self.numBalls)
		self.wpfeTest.setRootCanvas(self.rootCanvas)
		
		#self.wpfeLoaded(self.scene,None)
		self.scene.Loaded+= RoutedEventHandler(self.wpfeLoaded)
	#numBalls = 16
	#Work around for browser setInterval

	def wpfeLoaded(self,sender,e) :
		self.rootCanvas = sender
		if (self.startOnLoad):
			self.wpfeTest.setRootCanvas(self.rootCanvas)
			self.wpfeTest.start(self.numBalls)
			self.startOnLoad = False
		self.isLoaded = True
		self.wpfeTest.changeNumberOfBalls(int(Browser.HtmlPage.Document.ballselect.value))


	def dump(self,message):
		self.scene.dbgwin.Text+=message

	
	class Ball :
		def __init__(self,x, y, vx, vy):
			self.rand=None
			self.model = {"walls" : {"left":0, "top":0, "right": 500, "bottom": 300},
				"elastity" : -0.2,
				"ballRadius" : 26,
				"maxSpeed" : 3.0 }
		# default provisioning
			self.rand=Random()
			if (x == None) :
				Threading.Thread.Sleep(15)
				x = (self.model["walls"]["right"] - self.model["walls"]["left"] - 2*self.model["ballRadius"])* self.rand.random()
				y = (self.model["walls"]["bottom"] - self.model["walls"]["top"] - 2*self.model["ballRadius"])* self.rand.random()
				vx = 2*self.model["maxSpeed"]* self.rand.random() - self.model["maxSpeed"]
				vy = 2*self.model["maxSpeed"]* self.rand.random() - self.model["maxSpeed"]
			
			self._x = x
			self._y = y
			self._vx = vx
			self._vy = vy
			self._r = self.model["ballRadius"] # d = 52 px
			self._d = 2*self._r
			self._d2 = self._d*self._d
		
		def Ballmove(self):
			self._x +=self._vx
			self._y += self._vy
			if (self._x < self.model["walls"]["left"] and self._vx<0):
				#self._vx += (self._x - walls.left)*elastity
				self._vx = -self._vx
			# top
			if (self._y < self.model["walls"]["top"] and self._vy<0):
				#self._vy += (self._y - walls.top)*elastity
				self._vy = -self._vy
			# left
			if (self._x > self.model["walls"]["right"] - self._d and self._vx>0):
				#self._vx += (self._x - walls.right + self._d)*elastity
				self._vx = -self._vx
			# top
			if (self._y > self.model["walls"]["bottom"] - self._d and self._vy>0) :
				#self._vy += (self._y - walls.bottom + self._d)*elastity
				self._vy = -self._vy
			    
		def doCollide(self,b):
			dx = self._x - b._x
			dy = self._y - b._y
			dvx = self._vx - b._vx
			dvy = self._vy - b._vy	
			distance2 = dx*dx + dy*dy
	    		
			if (Math.Abs(dx) > self._d or Math.Abs(dy) > self._d): 
				return False
			if (distance2 > self._d2):
				return False
	    	
			# make absolutely elastic collision
			mag = dvx*dx + dvy*dy
			# test that balls move towards each other	
			if (mag > 0):
				return False
			mag /= distance2
			delta_vx = dx*mag
			delta_vy = dy*mag
			self._vx -= delta_vx
			self._vy -= delta_vy
			b._vx += delta_vx
			b._vy += delta_vy
			return True    

	#
	# Abstract test class
	# 
	# @param {Object} N
	#
	class BallsTest :
		def __init__(self,N):
			#dump("\n BallsTest() enter")
			self._N = N # number of objects
			self._ballsO = []
			self._isRunning = False
			self._showFPS=None
			self.timerM=None
			self.timerF=None
			self.doc = Browser.HtmlPage.Document
			self.nBallSel = self.doc.ballselect.value
			self.statbox = self.doc.status
			
		
		
		def BallsTeststart(self,N):
			#dump("\n Ballstest.prototype.start() enter")
			if (self._isRunning):
				return False

			self._isRunning = True

			if (N != None):
				self._N = N
			self._F = 0  # frames counter for FPS
			self._lastF = 0
			self._lastTime = DateTime()
			self.setInterval("move", self.moveBalls,5)
			self.setInterval("fps", self.showFps, 3000)
			self.timerM.Start()
			return True
	    	
		def changeNumberOfBalls(self,n):
			self.pause()
			oldno = int(self._N)
			newno = int(n)
			numBalls = n
			self._N = n
			if(newno<oldno):
				for i in range(newno,oldno):
					self._ballsO[i]._elem.Opacity=0
					
			else:
				for i in range(0,newno):
					self._ballsO[i]._elem.Opacity=1
					

			# NOTE : <karthikv>
			# This is a very ungraceful workaround for an issue which I am seeing from Beta 1 build (moved to DispatcherTimer from HTMLTimer) 
			# SL ( i.e the host IE ) crashes with more no.of balls at same timer interval
			# maybe a re-entrant thread issue.. not sure
			# so invoking increasing timer interval with increase in no.of.balls

			if(n>=128):
				self.timerM.Interval = TimeSpan(0,0,0,0,250)
			elif(n>=64):
				self.timerM.Interval = TimeSpan(0,0,0,0,75)
			elif(n>=32):
				self.timerM.Interval = TimeSpan(0,0,0,0,25)
			else:
				self.timerM.Interval = TimeSpan(0,0,0,0,5)
			self.resume()
		
		def setInterval(self,timerName, code, delay):
			if(timerName=="fps"):
				if (self.timerF==None):
					self.timerF = DispatcherTimer()
					self.timerF.Tick += EventHandler(code)
				self.timerF.Interval = TimeSpan(0,0,0,delay/1000)
				self.timerF.Start()
			else:
				if (self.timerM==None):
					self.timerM =  DispatcherTimer()
					self.timerM.Tick +=  EventHandler(code)
				self.timerM.Interval =  TimeSpan(0,0,0,0,delay)
				self.timerM.Start()

		def clearInterval(self,timerName):
			if(timerName=="fps"):
				self.timerF.Stop()
			else:
				self.timerM.Stop()
		
		def pause(self):
			self.doc.status.value="stopped"
			self.timerM.Stop()
	    
		def resume(self):
			self.doc.status.value="started"
			self.timerM.Start()

		
		def moveBalls(self,sender,e):
			##dump(" ::mb() "+self._N+ " , "+ self._ballsO.Count)
			if (self._N > self._ballsO.__len__()):
				return
			self._F=self._F+1
			# move balls
				#dump("\n about to move "+self._N+" balls")
			for i in range(0,self._N):
				self._ballsO[i].move()
			# process collisions
			for i in range(0,self._N):
				for j in range(i+1,self._N):
					self._ballsO[i].doCollide(self._ballsO[j])


		def showFps(self,sender,e):
			nNewBall = int(Browser.HtmlPage.Document.ballselect.value)
			if(nNewBall != self._N):
				self.changeNumberOfBalls(nNewBall)
				return
			statbox=Browser.HtmlPage.Document.status
			if(	statbox.value=="stop"):
				self.pause()
			if(	statbox.value=="start"):
				self.resume()
		
			#dump("\n ::showFps() enter")

			if (self._F - self._lastF < 10):
				return
			
			currTime = DateTime.Now
			delta_t = (currTime.Minute - self._lastTime.Minute)*60 + currTime.Second - self._lastTime.Second + (currTime.Millisecond - self._lastTime.Millisecond)/1000.0

			fps = (self._F - self._lastF)/delta_t
			
			self._lastF = self._F
			self._lastTime = currTime
			
			#self._showFPS(Math.Round(fps))
			self._ballsO[0]._elem.Parent.FindName("fps").Text = str(Math.Round(fps)) + " fps"


		def stop(self):
			#dump("\n Ballstest.prototype.stop() enter")
			if (not self._isRunning):
				return False
			self._isRunning = False
			slef.clearInterval("move")
			self.clearInterval("fps")

			#dump("\n Ballstest.prototype.stop() enter")
			return True


	#
	# WPF/e-specific implementation
	# 
	# @param {Object} name
	# @param {Object} x
	# @param {Object} y
	# @param {Object} vx
	# @param {Object} vy
	#
	class WPFEBall(Ball):
		def __init__(self,host, name, x, y, vx, vy):
			#dump("\n wpfeball() enter")
			Bubbles.Ball.__init__(self, x, y, vx, vy)
			self._host = host
			self._name = name
			#self._elem = host.FindName(name)
			self._elem = MyFindName(host.Children,name)
			self.move()
			#dump("\n wpfeball() exit") 

		def move(self):
			#dump("\n wpfeball.prototype.move() enter")
			self.Ballmove()
			#dump("\nsetting x,y")
			#	self._elem["canvas.left"] = self._x
			#	self._elem["canvas.top"] = self._y
			self._elem.SetValue(Canvas.LeftProperty, self._x)
			debug_x=self._x
			self._elem.SetValue(Canvas.TopProperty, self._y)
			#    self._elem.SetValue[Int32](Canvas.LeftProperty, self._x)
			#    self._elem.SetValue[Int32](Canvas.TopProperty, self._y)
			#dump("\nx,y set done wpfeball.prototype.move() exit")

		def clone(self,newName, is_bmp):
			#dump("\n wpfeball.prototype.clone() enter")
			# oops, wpf/e doesn't support objects cloning nor getting their XAML source!
			# it's just too bad -- I had to paste all XAML right here
			# 
			newXAML = ""
			if (is_bmp and is_bmp != None) :
				newXAML = '<Canvas xmlns="http://schemas.microsoft.com/client/2007" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" x:Name="' + newName + '" Width="54.6667" Height="54.6667" Canvas.Left="0" Canvas.Top="0"><Image Source="assets/ball.png"/></Canvas>'
			else :
				newXAML = '<Canvas xmlns="http://schemas.microsoft.com/client/2007" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" x:Name="' + newName + '" Width="52" Height="52" Canvas.Left="0" Canvas.Top="30"><Path Opacity="0.900000" StrokeThickness="2.000000" Stroke="#ffa6d000" StrokeMiterLimit="1.000000" Fill="#ffcbff00" Data="F1 M 51.000000,26.000000 C 51.000000,39.806641 39.807129,51.000000 26.000000,51.000000 C 12.192871,51.000000 1.000000,39.806641 1.000000,26.000000 C 1.000000,12.193359 12.192871,1.000000 26.000000,1.000000 C 39.807129,1.000000 51.000000,12.193359 51.000000,26.000000 Z"/><Path Opacity="0.740000" Data="F1 M 43.143066,13.087891 C 50.602051,22.888672 49.009766,36.642578 39.590332,43.812500 C 30.170898,50.980469 16.489258,48.842773 9.032715,39.042969 C 1.573242,29.240234 3.166016,15.486328 12.584961,8.316406 C 22.003906,1.149414 35.685547,3.285156 43.143066,13.087891 Z"><Path.Fill><RadialGradientBrush MappingMode="Absolute" GradientOrigin="156.791016,170.453125" Center="156.791016,170.453125" RadiusX="53.626404" RadiusY="53.626404"><RadialGradientBrush.GradientStops><GradientStop Offset="0.000000" Color="#ffffffff"/><GradientStop Offset="0.361685" Color="#fff5f7dd"/><GradientStop Offset="0.415730" Color="#ffebf0bc"/><GradientStop Offset="1.000000" Color="#ffcbff00"/></RadialGradientBrush.GradientStops><RadialGradientBrush.Transform><MatrixTransform Matrix="1.190000,0.165000,-0.165000,-1.281300,-113.414185,241.757843" /></RadialGradientBrush.Transform></RadialGradientBrush></Path.Fill></Path> <Path Fill="#ffffffff" Data="F1 M 23.100586,9.477539 C 24.741699,11.634766 23.116211,15.630859 19.470703,18.404297 C 15.825684,21.178711 11.540039,21.678711 9.899414,19.522461 C 8.258301,17.365234 9.883789,13.369141 13.529297,10.594727 C 17.174316,7.821289 21.459961,7.321289 23.100586,9.477539 Z"/></Canvas>'
			#	newNode = self._host.content.createFromXaml(newXAML)
			#	newNode = System.Windows.XamlReader.Load(newXAML)
			newNode = XamlReader.Load(newXAML)

			#	self._elem.getParent().children.add(newNode)
			self._elem.Parent.Children.Add(newNode)
			return Bubbles.WPFEBall(self._host, newName,None,None,None,None)





	class WPFETest(BallsTest):
		def __init__(self, N):
			#dump("\n WpfeTest() enter")
			Bubbles.BallsTest.__init__(self,N)
			#	#dump("\n" + N + " balls")
		
		def setRootCanvas(self,rootCanvas):
			self._wpfeBlock=rootCanvas
		
		def start(self,N):
		#dump("\n WPFEtest.prototype.start() enter")
			if (not self.BallsTeststart(N)) :
				return
				#dump("\n" + N + " balls to be created")
				#dump("\n" + self._ballsO.length + " len of array")

			self._savedXaml = Application.Current.Host.Source
			self._ballsO.append(Bubbles.WPFEBall(self._wpfeBlock, "wpfe_ball_0",None, None, None, None))
			#dump("\nmade first ball")

			for i in range(1,self._N):
				self._ballsO.append(self._ballsO[0].clone("wpfe_ball_" + str(i),None))

		#dump("\n" + self._ballsO.length + " len of array")

		def stop(self):
			#dump("\n WPFEtest.prototype.stop() enter")
			if (not self.stop):
				return
			#self._wpfeBlock.reload() self is no longer supported in Silverlight
			#System.Windows.Application.Current.Host.Source = self._savedXaml
			#xaml = System.Windows.Application.Current.LoadRootVisual('bubbles.xaml')
			#kv have not found a way of reloading the xaml in m3 build
			isLoaded = False

			#dump("\n WPFEtest.prototype.stop() exit")
		def _showFPS (self,fps):
			self._wpfeBlock.FindName("fps").text = fps + " fps"

def MyFindName(collect, name):
	itr = collect.GetEnumerator()
	for i in range(0,collect.Count):
		itr.MoveNext()
		current = itr.Current
		na=current.Name
		if na == name:
		    return current
		else:
			if (hasattr(current,"Children")):
				obj=MyFindName(current.Children,name)
				if(obj is not None): 
				    return obj
				
			continue
		
	return None


Bubbles()