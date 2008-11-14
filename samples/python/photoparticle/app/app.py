from System.Windows import *
from System.Windows.Controls import Canvas 
from System.Windows.Browser import *
from _random import Random
from System.Windows.Markup import XamlReader
from System import EventHandler, Uri, UriKind, Math
from math import sqrt

class PhotoParticle:
    def __init__(self):
        self.scene = Canvas()
        Application.LoadComponent(self.scene, Uri('app.xaml', UriKind.Relative))
        Application.Current.RootVisual = self.scene
        
        self.scene.Loaded += self.onMainPageLoaded
        self.scene.MouseLeftButtonDown += self.onMouseLeftButtonDown
        self.scene.timerSB.Completed += self.OnTimerCompleted
        
        self.timer = self.scene.FindName("timerSB")

        self.numFlakes = 0
        self.bStarted = False
        
        self.random = Random().random
        self.urls = ["assets/images/151357567_1feee2792a_m.jpg",
            "assets/images/439074330_bdc4c69e76_m.jpg",
            "assets/images/262008209_b51badb1b4_m.jpg",
            "assets/images/432960949_3bc5c86c9b_m.jpg",
            "assets/images/281646581_ba66b522bc_m.jpg",
            "assets/images/69521107_a2a48e3088_m.jpg",
            "assets/images/437559825_654f71d6db_m.jpg",
            "assets/images/422208375_8369c7cade_m.jpg",
            "assets/images/438253880_8a61c50854_m.jpg",
            ]
        self.chrs = ['A','B','C','D','E','F','G','H',
            'I','J','K','L','M','N',' O','P','Q',
            'R','S','T','U','V','W','X','Y','Z',]
        self.ptcls = []
    
    def onMainPageLoaded(self, sender, eventArgs):
        doc = HtmlPage.Document
        #button1 = doc.withRotation
        button1 = doc.GetElementById("withRotation")
        if button1 :
            button1.AttachEvent("onclick", EventHandler(onWithRotClick))
        button2 = doc.GetElementById("withoutRotation")
        if button2 :
            button2.AttachEvent("onclick", EventHandler(onWithoutRotClick))
        for i in range (0, 20):
            self.addFlake(i)
            
        self.bStarted = True
        
    def onMouseLeftButtonDown(self, sender, eventArgs):
        pass
        
    #def onMouseEnter(self,sender, args):
        #self.updateMousePosition(sender, args)
        
    def Interact(self):
        for i in range(0,len(self.ptcls)):
            MyParticle = self.ptcls[i]
            for j in range(0,len(self.ptcls)):
                MyParticle.PositionAdjust(self.ptcls[j])
            MyParticle.Update(self.ptcls)
    
    def OnTimerCompleted(self, sender, eventArgs):
        if self.bStarted:
            self.Interact()

        self.timer.Begin()
        
    def addFlake(self, index):
        # define vars
        nChr = Math.Floor(self.random() * len(self.chrs))
        hanStr = self.chrs[int(nChr)]
        nUrl = Math.Floor(self.random() * len(self.urls))
        urlStr= self.urls[int(nUrl)]
        newFlakeStr = newFlakeStr1 + urlStr + newFlakeStr2
        myFlakeStr = newFlakeStr.replace('$0', str(self.numFlakes))
        
        size = (20 + self.random() * 30)
        myFlakeStr = myFlakeStr.replace('$1', str(size))
        
        cR = Math.Floor(self.random() * 256)
        cG = Math.Floor(self.random() * 256)
        cB = Math.Floor(self.random() * 256)
        color = "#00" + self.NumToHex(cR) + self.NumToHex(cG) + self.NumToHex(cB)
        myFlakeStr = myFlakeStr.replace('$color', color)
        newFlake = XamlReader.Load(myFlakeStr)
        self.scene.FindName("MainCanvas").Children.Add(newFlake)
        
        ptcl = self.Particle(MyFindName(self.scene.Children,"t"+str(self.numFlakes)), MyFindName(self.scene.Children,"r"+str(self.numFlakes)), MyFindName(self.scene.Children,"s"+str(self.numFlakes)), size * 0.5, index, self.scene)
        self.ptcls.append(ptcl)
        self.numFlakes+=1

    def getTwoDigitInt(self, number):
      ## if this number already has two digits, return the int part
        if ((number < 0) or (number >= 10)):
            return str(Math.Floor(number))
      ## otherwise, prepend zero
        return "0" + Math.Floor(number)

    def NumToHex(self,strNum):
        base = strNum / 16
        rem = strNum % 16
        base = base - (rem / 16)
        baseS = self.MakeHex(base)
        remS = self.MakeHex(rem)
        return str(baseS) + str(remS)
        
    def MakeHex(self, x):
        if((x >= 0) and (x <= 9)):
            return int(x)
        else :
            if (x == 10) : return "A"
            elif (x == 11) : return "B"
            elif (x == 12) : return "C"
            elif (x == 13) : return "D"
            elif (x == 14) : return "E"
            elif (x == 15) : return "F"
            
    
    
    class Particle:
        def __init__(self, pos, rot, scale, radius,index, scene):
            self.rand = Random().random
            self.x = self.rand() * 400
            self.y = self.rand() * 400
            self.vx = 0
            self.vy = 0
            self.dt = 0.025
            self.decay = 0.95
            self.mouseX = 0
            self.mouseY = 0
            
            self.pos = pos
            self.rot = rot
            self.scale = scale
            self.index = index
            self.scene = scene
            
            self.o_radius = radius
            self.R = radius
            self.radius = radius
            self.m_radius = radius
            
            self.favId = Math.Floor(self.rand() * 20)
            self.age = 0
            
            self.rotZ = 0
            self.m_rotZ = 0
            self.turn = Math.Floor(self.rand() * 240) + 60
            
            self.scene.MouseMove += self.updateMousePosition

        def Update(self,ptcls):
            global bWithRot
            if not bWithRot:
                self.m_rotZ = 0
                
            self.rotZ += (self.m_rotZ - self.rotZ) * self.dt
            self.radius += (self.m_radius - self.radius) * self.dt
            
            dx = self.mouseX - self.x
            dy = self.mouseY - self.y
            d = Math.Sqrt(dx*dx + dy*dy)        ##distance between Mouse and Particle
            if d < 200:
                if (d > 0) and (d < 100):
                    self.m_radius = (100 - d) * 0.9 + self.o_radius
                    self.vx *= 0.9
                    self.vy *= 0.9
                else:
                    self.vx *= 1.03
                    self.vy *= 1.03
            else :
                self.m_radius = self.o_radius

            favPtcl = ptcls[int(self.favId)] #var
            
            self.vx += (favPtcl.x - self.x) * self.dt
            self.vy += (favPtcl.y - self.y) * self.dt
            self.x += self.vx * self.dt
            self.y += self.vy * self.dt
            self.vx *= self.decay
            self.vy *= self.decay
            
            self.pos.X = self.x - self.R
            self.pos.Y = self.y - self.R
            self.rot.Angle = self.rotZ
            self.scale.ScaleX = self.radius / self.o_radius
            self.scale.ScaleY = self.scale.ScaleX
            
            if(self.x + self.radius < 0) : self.x = 640 + self.R
            if(self.y + self.radius < 0) : self.y = 480 + self.R
            if(self.x - self.radius > 640) : self.x = 0 - self.R
            if(self.y - self.radius > 480) : self.y = 0 - self.R
            
            self.age += 1
            
            if(self.age > self.turn):
                self.age = 0
                self.turn = Math.Floor(self.rand() * 240) + 60
                self.m_rotZ = self.rand() * 360
                
        def PositionAdjust(self,other):
            dx = self.x - other.x
            dy = self.y - other.y
            d = Math.Sqrt (dx*dx + dy*dy)
            R = self.radius + other.radius
            if (d > 0) and (d < R):
                dr = R - d
                ux = dx / d
                uy = dy / d
                self.x += dr * ux * 0.5
                self.y += dr * uy * 0.5
                other.x += -dr * ux * 0.5
                other.y += -dr * uy * 0.5
                        
        ##Mouse move event handler
        def updateMousePosition(self, sender, args):
            self.mouseX = args.GetPosition(None).X
            self.mouseY = args.GetPosition(None).Y
            if (self.mouseX < 0): self.mouseX = 0
            if (self.mouseY < 0): self.mouseY = 0
        
                        
bWithRot = True
def onWithRotClick(sender, args):
    global bWithRot
    bWithRot = True

def onWithoutRotClick(sender, args):
    global bWithRot
    bWithRot = False
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
	
newFlakeStr1 = "<Canvas RenderTransformOrigin='0.5, 0.5' Background='$color' Width='$1' Height='$1' xmlns='http://schemas.microsoft.com/client/2007' xmlns:x='http://schemas.microsoft.com/winfx/2006/xaml'> \
<Canvas.RenderTransform> \
<TransformGroup> \
<ScaleTransform x:Name='s$0' ScaleX='1' ScaleY='1'/> \
<RotateTransform x:Name='r$0' Angle='0'/> \
<TranslateTransform x:Name='t$0' X='-100' Y='-100'/> \
</TransformGroup> \
</Canvas.RenderTransform> \
<Image Width='$1' Height='$1' Stretch='Fill' Source='"
newFlakeStr2 =  "'> \
<Image.OpacityMask> \
<ImageBrush ImageSource='./assets/images/circle_mask.png'/> \
</Image.OpacityMask> \
</Image> \
</Canvas>"

PhotoParticle()
