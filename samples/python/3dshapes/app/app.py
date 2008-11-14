from System import *
from System.Windows import *
from System.Windows.Browser import * 
from System.Windows.Controls import Canvas
from _random import Random
from System.Windows.Media import PointCollection
from System.Windows.Threading import *

##----------------------------------------
##    Class 3DShapes
##----------------------------------------
class ThreeDShapes:
    def __init__(self):

        self.scene = Canvas()
        Application.LoadComponent(self.scene, Uri('app.xaml', UriKind.Relative))
        Application.Current.RootVisual = self.scene
        #start(scene)

        #self.cube0 = self.scene.cube0
        self.bt1_a = self.scene.FindName("bt1_a")
        self.bt1_b = self.scene.FindName("bt1_b")


        self.currentShape = None

        self.mouseX = self.mouseY = None     # Mouse Position

        # random mouse position seems more fun !!
        random = Random().random
        self.mouseX = self.mouseY = random()*200
        self.centerX = 400
        self.centerY = 300

    
        self.cubePoints = [
            [[-90,-90,90],[90,-90,90],[90,90,90],[-90,90,90]], 
            [[-90,-90,-90],[-90,-90,90],[-90,90,90],[-90,90,-90]],
            [[-90,90,-90],[90,90,-90],[90,-90,-90],[-90,-90,-90]],
            [[90,-90,90],[90,-90,-90],[90,90,-90],[90,90,90]],
            [[-90,90,90],[90,90,90],[90,90,-90],[-90,90,-90]],
            [[-90,-90,-90],[90,-90,-90],[90,-90,90],[-90,-90,90]]
        ]

        self.torusPoints = [
            [[75,1,75],[0,0,105],[0,43,137],[97,43,97]], 
            [[1,0,105],[-74,1,75],[-96,43,97],[1,43,137]], 
            [[-74,0,75],[-104,1,0],[-136,43,0],[-96,43,97]], 
            [[-104,0,0],[-74,0,-74],[-96,43,-96],[-136,43,0]], 
            [[-74,1,-74],[1,0,-104],[0,43,-136],[-96,43,-96]], 
            [[0,0,-104],[75,1,-74],[97,43,-96],[0,43,-136]], 
            [[75,0,-74],[105,0,1],[137,43,1],[97,43,-96]], 
            [[105,0,0],[75,1,75],[97,43,97],[137,43,1]], 
            [[97,43,97],[1,43,137],[1,27,187],[132,27,132]], 
            [[1,43,137],[-96,43,97],[-131,27,132],[1,27,187]], 
            [[-96,43,97],[-136,43,0],[-186,27,1],[-131,27,132]], 
            [[-136,43,0],[-96,43,-96],[-131,27,-131],[-186,27,0]], 
            [[-96,43,-96],[0,43,-136],[0,27,-186],[-131,27,-131]], 
            [[0,43,-136],[97,43,-96],[132,27,-131],[0,27,-186]], 
            [[97,43,-96],[137,43,0],[187,27,0],[132,27,-131]], 
            [[137,43,1],[97,43,97],[132,27,132],[187,27,1]], 
            [[132,27,132],[1,27,187],[1,-26,187],[132,-26,132]], 
            [[1,27,187],[-131,27,132],[-131,-26,132],[1,-26,187]], 
            [[-131,27,132],[-186,27,0],[-186,-26,0],[-131,-26,132]], 
            [[-186,27,1],[-131,27,-131],[-131,-26,-131],[-186,-26,1]], 
            [[-131,27,-131],[1,27,-186],[1,-26,-186],[-131,-26,-131]], 
            [[0,27,-186],[132,27,-131],[132,-26,-131],[0,-26,-186]], 
            [[132,27,-131],[187,27,1],[187,-26,1],[132,-26,-131]], 
            [[187,27,1],[132,27,132],[132,-26,132],[187,-26,1]], 
            [[187,-26,0],[132,-26,132],[97,-42,97],[137,-42,0]], 
            [[132,-26,132],[1,-26,187],[1,-42,137],[97,-42,97]], 
            [[0,-26,187],[-131,-26,132],[-96,-42,97],[0,-42,137]], 
            [[-131,-26,132],[-186,-26,1],[-136,-42,0],[-96,-42,97]], 
            [[-186,-26,0],[-131,-26,-131],[-96,-42,-96],[-136,-42,1]], 
            [[-131,-26,-131],[0,-26,-186],[0,-42,-136],[-96,-42,-96]], 
            [[1,-26,-186],[132,-26,-131],[97,-42,-96],[1,-42,-136]], 
            [[132,-26,-131],[187,-26,0],[137,-42,0],[97,-42,-96]], 
            [[97,-42,97],[0,-42,137],[0,1,105],[75,0,75]], 
            [[1,-42,137],[-96,-42,97],[-74,1,75],[1,1,105]], 
            [[-96,-42,97],[-136,-42,1],[-104,0,1],[-74,0,75]], 
            [[-136,-42,0],[-96,-42,-96],[-74,1,-74],[-104,1,1]], 
            [[-96,-42,-96],[1,-42,-136],[1,1,-104],[-74,0,-74]], 
            [[0,-42,-136],[97,-42,-96],[75,0,-74],[0,1,-104]], 
            [[97,-42,-96],[137,-42,0],[105,0,1],[75,0,-74]], 
            [[137,-42,0],[97,-42,97],[75,0,75],[105,1,0]]
        ]

        self.shipPoints = [
            [[-15,36,140],[16,36,140],[16,26,140],[-15,26,140]], 
            [[-34,-7,35],[35,-7,35],[35,-34,-75],[-34,-34,-75]], 
            [[-9,-10,-157],[10,-10,-157],[10,7,-157],[-9,7,-157]], 
            [[-34,35,-75],[35,35,-75],[35,35,35],[-34,35,35]], 
            [[197,34,-38],[197,34,-76],[197,29,-76],[197,29,-38]], 
            [[-196,34,-76],[-196,34,-38],[-196,29,-38],[-196,29,-76]], 
            [[-34,35,35],[35,35,35],[16,36,140],[-15,36,140]], 
            [[35,35,35],[35,-7,35],[16,26,140],[16,36,140]], 
            [[35,-7,35],[-34,-7,35],[-15,26,140],[16,26,140]], 
            [[-34,-7,35],[-34,35,35],[-15,36,140],[-15,26,140]], 
            [[-1,-85,-109],[2,-85,-109],[3,-85,-158],[-2,-85,-158]], 
            [[101,-5,-113],[102,2,-114],[76,2,-160],[76,-5,-160]], 
            [[35,35,-75],[-34,35,-75],[-9,7,-157],[10,7,-157]], 
            [[-101,2,-114],[-100,-5,-113],[-75,-5,-160],[-75,2,-160]], 
            [[35,35,35],[35,35,-75],[197,34,-76],[197,34,-38]], 
            [[35,35,-75],[35,-34,-75],[197,29,-76],[197,34,-76]], 
            [[35,-34,-75],[35,-7,35],[197,29,-38],[197,29,-76]], 
            [[35,-7,35],[35,35,35],[197,34,-38],[197,29,-38]], 
            [[-34,35,-75],[-34,35,35],[-196,34,-38],[-196,34,-76]], 
            [[-34,35,35],[-34,-7,35],[-196,29,-38],[-196,34,-38]], 
            [[-34,-7,35],[-34,-34,-75],[-196,29,-76],[-196,29,-38]], 
            [[-34,-34,-75],[-34,35,-75],[-196,34,-76],[-196,29,-76]], 
            [[-34,-34,-75],[35,-34,-75],[4,-34,-75],[-3,-34,-75]], 
            [[35,-34,-75],[10,-10,-157],[10,-10,-157],[4,-34,-75]], 
            [[10,-10,-157],[-9,-10,-157],[-9,-10,-157],[10,-10,-157]], 
            [[-9,-10,-157],[-34,-35,-75],[-3,-34,-75],[-9,-10,-157]], 
            [[-3,-34,-75],[4,-34,-75],[2,-85,-109],[-1,-85,-109]], 
            [[4,-34,-75],[10,-10,-157],[3,-85,-158],[2,-85,-109]], 
            [[10,-10,-157],[-9,-10,-157],[-2,-85,-158],[3,-85,-158]], 
            [[-9,-10,-157],[-3,-34,-75],[-1,-85,-109],[-2,-85,-158]], 
            [[35,-34,-75],[35,35,-75],[102,2,-114],[101,-5,-113]], 
            [[35,35,-75],[10,7,-157],[76,2,-160],[102,2,-114]], 
            [[10,7,-157],[10,-10,-157],[76,-5,-160],[76,2,-160]], 
            [[10,-10,-157],[35,-34,-75],[101,-5,-113],[76,-5,-160]], 
            [[-34,35,-75],[-34,-34,-75],[-100,-5,-113],[-101,2,-114]], 
            [[-34,-34,-75],[-9,-10,-157],[-75,-5,-160],[-100,-5,-113]], 
            [[-9,-10,-157],[-9,7,-157],[-75,2,-160],[-75,-5,-160]], 
            [[-9,7,-157],[-34,35,-75],[-101,2,-114],[-75,2,-160]]
        ]
        self.transformMatrix = [ [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0] ]
        self.shapes = [  ThreeDShapes.Shape("cube", "wire", 1, self.cubePoints, self.scene),
                ThreeDShapes.Shape("cube", "shade", 2, self.cubePoints,self.scene),

                ThreeDShapes.Shape("torus", "wire", 3, self.torusPoints,self.scene),
                ThreeDShapes.Shape("torus", "shade", 4, self.torusPoints,self.scene),

                ThreeDShapes.Shape("ship", "wire", 5, self.shipPoints,self.scene),
                ThreeDShapes.Shape("ship", "shade", 6, self.shipPoints,self.scene)
             ]
        
        self.scene.Loaded += self.OnLoaded
        self.scene.buttonArea1.Loaded += self.Buttons
        
    def Buttons(self,sender, eventArgs):
        self.bt1_a.Opacity = 0
        self.bt1_b.Opacity = 1
        
    class Shape:
        def __init__(self,name, render, ordinal, points, scene):
	        self.name       = name
	        self.render     = render
	        self.ordinal    = ordinal
	        self.polygon    = points
	        self.scene = scene
	        self.transformMatrix = None

	        self.length     = len(points)
	        self.poly       = None
	        self.f = 400.0  
        def clear(self):
            if self.poly:
                for i in range(self.length):
                    self.poly[i].Points = PointCollection()
        def settransformMatrix(self,transformMatrix):
            self.transformMatrix=transformMatrix
        def initPoly(self):
            if (self.name == "cube" and self.render == "shade"):
                polygonType = "cube%s"
            else :
                if self.render == "wire": polygonType = "wire%s"
                else: polygonType = "shade%s"

            self.poly = [None] * self.length
            for i in range(self.length):
                self.poly[i] = self.scene.FindName(polygonType % i)

            
        def resetButton(self):
            self.bt_a.Opacity = 0.6
            self.scale.ScaleX = self.scale.ScaleY = 1
            self.bt_b.Opacity = 0
                


        def redrawPolygons(self):
        #dumpnew("redrawpolygons()\n");

            if not self.poly:
                self.initPoly()
                
            dist    = [0] * self.length
            
            pointsX = [None] * self.length
            pointsY = [None] * self.length
                
            for j in range(self.length):
                distPoly = 0
                
                iLength = len(self.polygon[j])
                
                pointsX[j] = [0] * iLength
                pointsY[j] = [0] * iLength
                aaa=self.transformMatrix
                for i in range(iLength):
                    point = ThreeDShapes.mvm(self.transformMatrix, self.polygon[j][i])
                    pointsX[j][i] = point[0]/(1-(point[2]/self.f))
                    pointsY[j][i] = point[1]/(1-(point[2]/self.f))
                    camdist = Math.Sqrt(Math.Pow(point[0],2) + Math.Pow(point[1],2) + Math.Pow(self.f-(point[2]),2))
                    distPoly += camdist

                dist[j] = distPoly

            zList = dist[:]

            dist.sort()
            dist.reverse()

            for j in range(self.length):
                key = dist[j]
                i = 0
                while i < self.length and key != zList[i]:
                    i += 1
                if i == self.length:
                    raise str(dist) + str(zList)

                pointsStr = PointCollection()
                
                for k in range(len(pointsX[i])): 
                    #pointsStr.append(Point(pointsX[i][k], pointsY[i][k]))
                    pointsStr.Add(Point(pointsX[i][k], pointsY[i][k]))
                self.poly[j].Points = pointsStr #Array[Point](pointsStr)

#--------------------------
    def hookupButtonEvents(self,sp):
        sp.buttonArea = self.scene.FindName("buttonArea%s" % sp.ordinal)
        
        sp.buttonArea.MouseEnter += self.enterButton
        sp.buttonArea.MouseLeave += self.leaveButton
        sp.buttonArea.MouseLeftButtonDown += self.downButton
        sp.buttonArea.MouseLeftButtonUp += self.upButton
        
        sp.bt_a   = self.scene.FindName("bt%s_a" % sp.ordinal)
        sp.bt_b   = self.scene.FindName("bt%s_b" % sp.ordinal)
        sp.scale  = self.scene.FindName("scale%s" % sp.ordinal)
            

    def lastchar(self,str):
        str+=""
        return str[len(str)-1:]

    def enterButton(self, sender, eventArgs):
        i=int(self.lastchar(sender.Name))-1
        self.shapes[i].bt_a.Opacity = 1
        #self.bt_a.Opacity = 1

    def leaveButton(self, sender, eventArgs):
        #if self.bt_b.Opacity != 1:
            #self.bt_a.Opacity = 0.6
        i=int(self.lastchar(sender.Name))-1 
        if( self.shapes[i].bt_b.Opacity != 1):
            self.shapes[i].bt_a.Opacity = 0.6

    def downButton(self, sender, eventArgs):
        i=int(self.lastchar(sender.Name))-1 
        self.shapes[i].scale.ScaleX = self.shapes[i].scale.ScaleY = 0.9
        #self.scale.ScaleX = self.scale.ScaleY = 0.9

    

    def upButton(self, sender, eventArgs):
        #global currentShape, transformMatrix
        i=int(self.lastchar(sender.Name))-1 
        if(self.currentShape != self.shapes[i]):
            self.currentShape.resetButton()
            self.currentShape.clear()
            self.currentShape = self.shapes[i]
        self.shapes[i].bt_a.Opacity = 0
        self.shapes[i].bt_b.Opacity = 1

    def OnLoaded(self,sender, e):
        
        #self.currentShape = shapes[0]
        #ag = sender.Parent
      #  ag.MouseMove += getMouseXY
        self.scene.MouseMove += self.getMouseXY
        self.scene.MouseEnter += self.getMouseXY

        for x in self.shapes:
            self.hookupButtonEvents(x)
        
        self.currentShape = self.shapes[0]
        
        self.refreshScene(None,None)

        ht = DispatcherTimer()
        ht.Tick += self.refreshScene
        #ht.Isenabled = True
        ht.Interval = TimeSpan.FromMilliseconds(30)
        ht.Start()

    ## -------------------------------
    ## Updates drawing
    ## -------------------------------

    

    def refreshScene(self,sender, args):
      #dump("refreshing...");
        if (self.mouseX ==None): 
		    #dump("abort refreshing");
            return 
        
        y = - self.mouseY + self.centerY
        x =  self.mouseX - self.centerX
        if (y > 300):
            y = 300
        elif(y < -300):
            y = -300

        if (x > 400):
            x = 400
        elif (x < -400):
            x = -400
            
        x *= 2
        y *= 2.5
        
        self.setTransformMatrix(y, x, 0, self.transformMatrix)
        self.currentShape.settransformMatrix(self.transformMatrix)
        self.currentShape.redrawPolygons()


    def getMouseXY(self,sender, eventArgs) :
        
    #    dump("mousexy")
        
        self.mouseX = eventArgs.GetPosition(None).X
        self.mouseY = eventArgs.GetPosition(None).Y

        if (self.mouseX < 0):self.mouseX = 0
        if (self.mouseY < 0):self.mouseY = 0
        
    #    dump("mousexy "+mouseX+","+mouseY);
        return True
       


    def setTransformMatrix(self,x, y, z, M) :
        
    #    dump("setTM() enter"+x+" "+y+" "+z+" "+M);
        #global transformMatrix
        vectorLength = Math.Sqrt(x*x+y*y+z*z)
        
        if (vectorLength > 0.0001):
            pi = 3.14159265
            x = x / vectorLength
            y = y / vectorLength
            z = z / vectorLength
            Theta = vectorLength / 100
            cosT = Math.Cos(Theta * pi/180)
            sinT = Math.Sin(Theta * pi/180)
            tanT = 1-cosT
            
            T = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            T[0][0] = tanT*x*x+cosT
            T[0][1] = tanT*x*y-sinT*z
            T[0][2] = tanT*x*z+sinT*y
            T[1][0] = tanT*x*y+sinT*z
            T[1][1] = tanT*y*y+cosT
            T[1][2] = tanT*y*z-sinT*x
            T[2][0] = tanT*x*z-sinT*y
            T[2][1] = tanT*y*z+sinT*x
            T[2][2] = tanT*z*z+cosT
            ssss= self.transformMatrix
            self.transformMatrix = self.mmm(T, M)
            
    @staticmethod
    def mvm (a, v):
        m = [0, 0, 0]
        for i in xrange(3): 
            m[i] = a[i][0]*v[0]+a[i][1]*v[1]+a[i][2]*v[2]
        return m

    # -------------------------------
    # Multiply Matrix a by Matrix b
    # -------------------------------
    def mmm (self, a, b):
        m = [[0, 0, 0], [0, 0, 0], [0, 0, 0],]
        for j in xrange(3):
            for i in xrange(3):
                m[j][i] = a[j][0]*b[0][i]+a[j][1]*b[1][i]+a[j][2]*b[2][i]
        return m
        

ThreeDShapes()