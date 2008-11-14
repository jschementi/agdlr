Import("System.Windows.Application")
Import("System.Windows.Browser.*")
Import("System.Windows.Controls.UserControl")
Import("System")

function dump(msg) {
    scene.Message.Text+="\n"+msg;
}

scene = Application.Current.LoadRootVisual(new UserControl(), "app.xaml")
scene.Loaded += OnLoaded
scene.buttonArea1.Loaded += Buttons

var cube0 = scene.cube0;
var bt1_a = scene.bt1_a
var bt1_b = scene.bt1_b

var	ag, currentShape
var ht;
var mouseX,mouseY;
mouseX = mouseY = null     // Mouse Position

// random mouse position seems more fun !!
mouseX = mouseY = Math.floor(Math.random()*200);

function Buttons(sender, eventArgs){
    bt1_a.Opacity = 0
    bt1_b.Opacity = 1
}    
    
cubePoints = [
    [[-90,-90,90],[90,-90,90],[90,90,90],[-90,90,90]], 
    [[-90,-90,-90],[-90,-90,90],[-90,90,90],[-90,90,-90]],
    [[-90,90,-90],[90,90,-90],[90,-90,-90],[-90,-90,-90]],
    [[90,-90,90],[90,-90,-90],[90,90,-90],[90,90,90]],
    [[-90,90,90],[90,90,90],[90,90,-90],[-90,90,-90]],
    [[-90,-90,-90],[90,-90,-90],[90,-90,90],[-90,-90,90]]
]

torusPoints = [
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

shipPoints = [
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

function Shape(name, render, ordinal, points)
{
    this.name       = name
    this.render     = render
    this.ordinal    = ordinal
    this.polygon    = points

    this.length     = points.length
    this.poly       = null

}

Shape.prototype.clear = function()
{
    if(this.poly) {
        for(i=0;i<this.length;i++)
            this.poly[i].Points = new System.Windows.Media.PointCollection();
    }
}

Shape.prototype.initPoly = function()
{
    if(this.name == "cube" && this.render == "shade") {
        polygonType = "cube"
    }
    else if(this.render == "wire")
    { polygonType = "wire" } 
    else
    { polygonType = "shade" }
    this.poly = [];
        
    for(i=0;i<this.length;i++)
        this.poly[i] = null;
        
    for(i=0;i<this.length;i++)
    {
        this.poly[i] = scene.FindName(polygonType+i);
    }
}

Shape.prototype.hookupButtonEvents = function()
{
    this.buttonArea = scene.FindName("buttonArea"+this.ordinal)

    this.buttonArea.MouseEnter += this.enterButton
    this.buttonArea.MouseLeave += this.leaveButton
    this.buttonArea.MouseLeftButtonDown += this.downButton
    this.buttonArea.MouseLeftButtonUp += this.upButton
            
    this.bt_a   = scene.FindName("bt"+this.ordinal+"_a")
    this.bt_b   = scene.FindName("bt"+this.ordinal+"_b")
    this.scale  = scene.FindName("scale"+this.ordinal)
}

function lastchar(str)
{
    str+="";
    return str.charAt(str.length-1);
}

Shape.prototype.enterButton = function(sender, eventArgs)
{ 
    //doesn't work . this is not shape object but global object
    //my workaround - karthikv
    //sender.name is buttonArea1 or buttonArea2 ...
    //wont scale up for more than 9 shapes
    var i=Number(lastchar(sender.name))-1 
    shapes[i].bt_a.Opacity = 1
}    

Shape.prototype.leaveButton = function(sender, eventArgs)
{
    var i=Number(lastchar(sender.name))-1 
    if( shapes[i].bt_b.Opacity != 1)
        shapes[i].bt_a.Opacity = 0.6
}

Shape.prototype.downButton = function( sender, eventArgs)
{
    var i=Number(lastchar(sender.name))-1 
    shapes[i].scale.ScaleX = shapes[i].scale.ScaleY = 0.9
}
 
Shape.prototype.resetButton = function()
{
    this.bt_a.Opacity = 0.6
    this.scale.ScaleX = this.scale.ScaleY = 1
    this.bt_b.Opacity = 0
}

Shape.prototype.upButton = function(sender, eventArgs)
{
    var i=Number(lastchar(sender.name))-1 
    if(currentShape != shapes[i])
    {
        currentShape.resetButton()
        currentShape.clear()
        currentShape = shapes[i]
    }
    
    shapes[i].bt_a.Opacity = 0
    shapes[i].bt_b.Opacity = 1
}

Shape.prototype.redrawPolygons = function()
{
    if(!this.poly) 
        this.initPoly()
    
    var dist = [0];
    var pointsX = [[null]];
    var pointsY = [[null]];
    
    for(i=0;i<this.length;i++)
    {
        dist[i]    = 0
        pointsX[i] = [null]
        pointsY[i] = [null]
    }   
    
    var i,j,k;
      
    for(j=0;j< this.length;j++)
    {
        distPoly = 0
        
        iLength = this.polygon[j].length
        for(i=0;i<iLength;i++)
        {
            pointsX[j][i] = 0
            pointsY[j][i] = 0
        }
        
        for(i=0;i<iLength;i++)
        {
            point = mvm(transformMatrix, this.polygon[j][i])
            pointsX[j][i] = point[0]/(1-(point[2]/f))
            pointsY[j][i] = point[1]/(1-(point[2]/f))
            camdist = Math.sqrt(Math.pow(point[0],2) + Math.pow(point[1],2) + Math.pow(f-(point[2]),2))
            distPoly += camdist
            
        }
        
        dist[j] = distPoly
    }
    
    zList = [0];
    for(i=0;i<dist.length;i++) zList[i] = dist[i];
    
    for(i=0;i<dist.length;i++)
        for(j=i+1;j<dist.length;j++)
            if(dist[i]<dist[j])
            {
                temp = dist[i];
                dist[i] = dist[j];
                dist[j] = temp;
            }

    for( j=0;j<this.length;j++)
    {
        key = dist[j]
        i = 0 
        while( i < this.length && key != zList[i])
            i += 1
        if( i == this.length)
        {
            dump("exception"+dist);
            throw dist+" "+zList
        }
        
        pointsStr = new System.Windows.Media.PointCollection();
        
        for(k=0;k<pointsX[i].length;k++)
        {
            pointsStr.Add(new System.Windows.Point(pointsX[i][k], pointsY[i][k]));
         }
            
        this.poly[j].Points = pointsStr
    }
}


ag = currentShape = null
f = 400.0

shapes = [  new Shape("cube", "wire", 1, cubePoints),
            new Shape("cube", "shade", 2, cubePoints),

            new Shape("torus", "wire", 3, torusPoints),
            new Shape("torus", "shade", 4, torusPoints),

            new Shape("ship", "wire", 5, shipPoints),
            new Shape("ship", "shade", 6, shipPoints)
         ]
transformMatrix = [ [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 0] ]

function OnLoaded(sender, e){

    ag = sender.Parent
    scene.MouseMove += getMouseXY
    scene.MouseEnter += getMouseXY
    
    for(x in shapes)
    {
        shapes[x].hookupButtonEvents()
    }
    
    currentShape = shapes[0]
    
    refreshScene(null,null)
    
    ht = new System.Windows.Threading.DispatcherTimer()
    ht.Tick += refreshScene
    ht.IsEnabled = true
    ht.Interval = System.TimeSpan.FromMilliseconds(30)
    ht.Start()
}

//# -------------------------------
//# Updates drawing
//# -------------------------------

centerX = 400
centerY = 300

function refreshScene(sender, args) {
    if (mouseX == null)
    { 
        return 
    }
    
    y = - mouseY + centerY
    x =  mouseX - centerX
    if (y > 300)
        y = 300
    else if (y < -300)
        y = -300

    if (x > 400)
        x = 400
    else if (x < -400)
        x = -400
        
    x *= 2
    y *= 2.5
    
    setTransformMatrix(y, x, 0, transformMatrix)
    currentShape.redrawPolygons()
}


function getMouseXY(sender, eventArgs) {
     
    mouseX = eventArgs.GetPosition(null).X
    mouseY = eventArgs.GetPosition(null).Y

    if (mouseX < 0) mouseX = 0
    if (mouseY < 0) mouseY = 0
    
    return true
}    


function setTransformMatrix(x, y, z, M) {
    
    vectorLength = Math.sqrt(x*x+y*y+z*z)
    
    if (vectorLength > 0.0001)
    {
        pi = 3.14159265;
        
        x = x / vectorLength
        y = y / vectorLength
        z = z / vectorLength
        Theta = vectorLength / 100
        cosT = Math.cos(Theta * pi/180)
        sinT = Math.sin(Theta * pi/180)
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
        
        transformMatrix = mmm(T, M)
    }
}

//# -------------------------------
//# Multiply Matrix a by Matrix b
//# -------------------------------
function mmm (a, b){
    m = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for (j=0;j<3;j++) {
        for(i=0;i<3;i++) {
            m[j][i] = a[j][0]*b[0][i]+a[j][1]*b[1][i]+a[j][2]*b[2][i]
        }
    }
    return m
}
//# -------------------------------
//# Multiply Matrix a by Vector v
//# -------------------------------
function mvm (a, v){
    m = [0, 0, 0]
    for (i=0;i<3;i++) { 
        m[i] = a[i][0]*v[0]+a[i][1]*v[1]+a[i][2]*v[2]
    }
    return m
}
