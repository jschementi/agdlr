from System import Uri, UriKind
from System.Windows import Media
from System.Windows.Controls import Canvas

## Main logic for the entire app.
## width and height are the number of tiles in x and y direction
## Gameboard object
class Gameboard (object):

    def __init__ (self, target, width, height):
        self.target = target;
        self.width = width;
        self.height = height;
        self.rand=None
        self.scene=None
        ## Bulletproofing added for later assumptions about math in native js code.
        if (height % 2 == 1) and (width % 2) == 1:
            raise Error("Code assumes even number of tiles.")

    scoreRed = 0
    scoreBlue = 0
    tiles = None
    bombs = None
    redScore = 0
    blueScore = 0
    ## Note, tile indicators for red and blue are 1 and 2, but turn indicators are 0 and 1
    turn = 0 
    currentArsenal = None
    
    def setRand(self,rand):
      self.rand=rand
        
    def setScene(self,scene):
      self.scene=scene
    
    def getelement(self, id): 
      return self.target.FindName(id)
   
    def getbrush(self, color):
      _supported_colors = {"black": (0, 0, 0), "white": (0xFF, 0xFF, 0xFF)}
      rgb = None
      if color in _supported_colors:
        rgb = _supported_colors[color]
      else: raise Exception("Color, " + color + ", is not known")
      if color=="black" :
        return Media.SolidColorBrush(Media.Colors.Black)
      elif color=="white" :
        return Media.SolidColorBrush(Media.Colors.White)

    ## Gameboard initialization function
    def initialize (self):
        self.tiles = [Tile(i, j, self) for i in xrange(self.width) \
                                       for j in xrange(self.height)]
        redRemaining = self.width * self.height / 2
        blueRemaining = redRemaining
        for i in xrange(len(self.tiles)):
            newState = round(self.rand.random() + 1)
            if ((newState == 1 and redRemaining > 0) or blueRemaining == 0):
                redRemaining -= 1
                newState = 1
            else:
                blueRemaining -= 1
                newState = 2
            self.tiles[i].setState(newState)
  
        self.createBombs()
        ## Don't use Gameboard as reference to element since it is the name of a type.
        self.target.FindName("Gameboard").MouseLeave += self.handleMouseLeave 
        self.updateScore()
        self.turn = round(self.rand.random())
        self.player1Arsenal = Arsenal("1", self)
        self.player1Arsenal.setRand(self.rand)
        self.player2Arsenal = Arsenal("2", self)
        self.player2Arsenal.setRand(self.rand)
        self.updatePlayerStatus()
 
    
    ### Creates all the bombs the game will be using.
    def createBombs (self):
        self.bombs = []
  
        bomb = Bomb("Broken Arrow", "BlackBomb")
        bomb.points = [Point(-1, -1), Point(-1, -0), Point(-1, 1), Point(0, 1), Point(1, 1)]
        self.bombs.append(bomb)
  
        bomb = Bomb("ScatterA", "RedBomb")
        bomb.points = [Point(0, 1), Point(-1, 0), Point(1, 0), Point(0, -1)]
        self.bombs.append(bomb)
  
        bomb = Bomb("Napalm", "BigRoundBomb")
        bomb.points = [Point(2, 0), Point(2, 1), Point(1, 0), Point(1, 1), Point(0, 0), \
                 Point(0, 1), Point(-1, 0), Point(-1, 1), Point(-2, 0), Point(-2, 1), \
                 Point(-3, 0), Point(-3, 1)]
        self.bombs.append(bomb)
  
        bomb = Bomb("Trident", "purpleBomb")
        bomb.points = [Point(-1,0), Point(0,0), Point(1,0)]
        self.bombs.append(bomb)
  
        bomb = Bomb("Crossbow", "SkyBlueBomb")
        bomb.points = [Point(-2, 0), Point(-1, 0), Point(0, 0), Point(1, 0), Point(2, 0), \
                 Point(0, -1), Point(0, -2), Point(0, 1), Point(0, 2)]
        self.bombs.append(bomb)
  
        bomb = Bomb("Cluster", "BlueBomb")
        bomb.points = [Point(-2, -2), Point(-2, 0), Point(-2, 2), Point(0, -2), Point(0, 0), \
                       Point(0, 2), Point(2, -2), Point(2, 0), Point(2, 2)]
        self.bombs.append(bomb)
  
        bomb = Bomb("Bunker Buster", "SmallRoundBomb")
        bomb.points = [Point(-2, -2), Point(-2, -2), Point(-1, -2), Point(0, -2), Point(1, -2), \
                 Point(2, -2), Point(-2, 2), Point(-1, 2), Point(0, 2), Point(1, 2), \
                 Point(2, 2), Point(-2, -1), Point(-2, -0), Point(-2, 1), Point(2, -1), \
                 Point(2, 0), Point(2, 1), Point(0, 0)]
        self.bombs.append(bomb)
  
        bomb = Bomb("Barrage", "GreyBomb")
        bomb.points = [Point(-2, -2), Point(-1, -1), Point(0, 0), Point(1, 1), Point(2, 2)]
        self.bombs.append(bomb)


    def markFromTile (self, tile):
        for i in xrange(len(self.tiles)):
            self.tiles[i].unmark()
        if (self.currentArsenal and self.currentArsenal.selectedBomb):
            self.currentArsenal.selectedBomb.mark(self, tile.x, tile.y)
  
  
    def dropBomb (self):
        if self.currentArsenal and self.currentArsenal.selectedBomb:
            for i in xrange(len(self.tiles)):
                if self.tiles[i].isMarked:
                    self.tiles[i].setState(0)
            self.updateScore()
            self.currentArsenal.bombAndPopulate()
            self.turn = (self.turn + 1) % 2
            self.updatePlayerStatus()
  
  
    def updatePlayerStatus (self):
        if self.currentArsenal:
            self.currentArsenal.deactivate()
        self.currentArsenal = None
        if self.turn == 0:
            self.currentArsenal = self.player1Arsenal
            self.scene.Player1TurnIndicatorArrow.Opacity = 1
            self.scene.Player2TurnIndicatorArrow.Opacity = 0
        elif self.turn == 1:
            self.currentArsenal = self.player2Arsenal
            self.scene.Player1TurnIndicatorArrow.Opacity = 0
            self.scene.Player2TurnIndicatorArrow.Opacity = 1
        if self.currentArsenal:
            self.currentArsenal.activate()
  
  
    def handleMouseLeave (self, sender, eventArgs):
        for i in xrange(len(self.tiles)):
            self.tiles[i].unmark()
    
    
    def updateScore (self):
        self.redScore = 0
        self.blueScore = 0
        for i in xrange(len(self.tiles)):
            if (self.tiles[i].state == 1):
                self.redScore += 1
            elif self.tiles[i].state == 2:
                self.blueScore += 1
        if self.redScore == 0 and self.blueScore != 0:
            self.scene.RedScore.Text = "LOSER"
            self.scene.BlueScore.Text = "WINNER"
            self.turn = -1
        elif self.blueScore == 0 and self.redScore != 0:
            self.scene.RedScore.Text = "WINNER"
            self.scene.BlueScore.Text = "LOSER"
            self.turn = -1
        else:
            self.scene.RedScore.Text= str(self.redScore)
            self.scene.BlueScore.Text = str(self.blueScore)
    
	##    Function to set the transform to make the entire gameboard (the root element)
	##    near the same size of the browser window
	##    The function attempts to keep the aspect ratio intact as much as possible.
    def resize (self, width, height):
        coreWidth = Root.Width
        coreHeight = Root.Height
        ratio = coreWidth / coreHeight
        if (width / ratio > height):
            width = height * ratio
        else:
            height = width / ratio
        self.scene.RootScaleTransform
        self.scene.RootScaleTransform.ScaleX = width / coreWidth
        self.scene.RootScaleTransform.ScaleY = height / coreHeight


### Represents each tile position in the gameboard.
class Tile (object):
    def __init__ (self, x, y, gameboard):
        self.x = x
        self.y = y
        self.gameboard = gameboard
  
        ## these elements are defined in the xaml file.
        self.groundTile = self.gameboard.getelement("groundTile" + str(x) + "_" + str(y))
        self.playTile = self.gameboard.getelement("playTile" + str(x) + "_" + str(y))
        self.markingTile = self.gameboard.getelement("markingTile" + str(x) + "_" + str(y))
        self.markingTileParent \
            = self.gameboard.getelement("markingTileParent" + str(x) + "_" + str(y))
        
        self.markingTileParent.MouseEnter += self.handleMarkerEnter
        self.markingTileParent.MouseLeftButtonDown += self.handleMarkerClick


    state = 0
    isMarked = False


    ## Updates what state the tile is in-
    ##      0 = empty
    ##      1 = Red
    ##      2 = Blue
    def setState (self, state):
        self.state = state
        if state == 0:
            tempuri=Uri("", UriKind.Relative)
            tempimage = Media.Imaging.BitmapImage(tempuri)
            self.playTile.Source =tempimage 
            
            self.unmark()
        elif state == 1:
            tempuri=Uri("assets/images/red.png", UriKind.Relative)
            tempimage = Media.Imaging.BitmapImage(tempuri)
            self.playTile.Source =tempimage 
        elif state == 2:
            tempuri=Uri("assets/images/blue.png", UriKind.Relative)
            tempimage = Media.Imaging.BitmapImage(tempuri)
            self.playTile.Source =tempimage 

  
    ## Set this tile as marked for explosion.
    ## Shows the yellow bomb marking squares over the square.
    def mark (self):
        self.markingTile.Opacity = 1
        self.isMarked = True

  
    ## Clear the bomb marking on this tile.
    def unmark (self):
        if self.isMarked:
            self.markingTile.Opacity = 0.01
            self.isMarked = False


    ## Handler for mouse enter over this tile, for moving the bomb marker.
    def handleMarkerEnter (self, sender, args):
        self.gameboard.markFromTile(self)
  
  
    ## Used for triggering dropping the bomb.
    def handleMarkerClick (self, sender, args):
        self.gameboard.dropBomb()


### Random helper class.
class Point (object):
    def __init__ (self,x, y):
        self.x = x
        self.y = y


### Bomb class, represents bombing pattern and icon
class Bomb (object):
    def __init__ (self, name, iconName):
        self.name = name
        self.iconName = iconName
        self.points = []

    ## Mark the tiles on the gameboard this will effect
    def mark (self, gameboard, x, y):
        for i in xrange(len(self.points)):
            self.markPoint(gameboard, x + self.points[i].x, y + self.points[i].y)
  
    def markPoint (self, gameboard, x, y):
        if x >= 0 and x < gameboard.width:
            if y >= 0 and y < gameboard.height:
                gameboard.tiles[gameboard.width * x + y].mark()
                
 
class Arsenal (object):
 
    def __init__ (self, playerName, gameboard):
        self.playerName = playerName
        self.gameboard = gameboard
        self.rand=None
        for i in xrange(len(gameboard.bombs)):
            bomb = self.gameboard.bombs[i]
            bombIcon = self.gameboard.getelement(bomb.iconName + playerName)
            bombIcon.Opacity = 0
            bombIcon.MouseLeftButtonDown += self.selectBomb
        self.bombs = []
        
    selectedBomb = None
    
    def setRand(self,rand):
        self.rand=rand
        self.bombAndPopulate()
        self.deactivate()

    def bombAndPopulate (self):
        if self.selectedBomb:
            self.gameboard.getelement(self.selectedBomb.iconName + self.playerName).Opacity = 0
            self.gameboard.getelement(self.selectedBomb.iconName + "Back" + self.playerName).Stroke \
                =  self.gameboard.getbrush("black")
            self.bombs.remove(self.selectedBomb)
        while len(self.bombs) < 3:
            index = int(round(self.rand.random() * (len(self.gameboard.bombs) - 1)))
            newBomb = self.gameboard.bombs[index]
            hasBomb = False
            for i in xrange(len(self.bombs)):
                if self.bombs[i] == newBomb:
                    hasBomb = True
            if (not hasBomb and (newBomb != self.selectedBomb)):
                self.bombs.append(newBomb)

        for i in xrange(len(self.gameboard.bombs)):
            self.setUpBombIcon(self.gameboard.bombs[i], -1, 0)
        for i in xrange(len(self.bombs)):
            self.setUpBombIcon(self.bombs[i], i, 1)
        self.selectedBomb = None


    def setUpBombIcon(self, bomb, index, opacity):
        bombIcon = self.gameboard.getelement(bomb.iconName + self.playerName)
        bombIcon.Opacity = opacity
        bombIcon.SetValue(Canvas.LeftProperty, index * 105.0)
        self.gameboard.getelement(bomb.iconName + "Back" + self.playerName).Stroke \
            = self.gameboard.getbrush("black")


    def deactivate (self):
        for i in xrange(len(self.bombs)):
            bomb = self.bombs[i]
            bombIcon = self.gameboard.getelement(bomb.iconName + self.playerName)
            bombIcon.Opacity = 0.5

    def activate (self):
        for i in xrange(len(self.bombs)):
            bomb = self.bombs[i]
            bombIcon = self.gameboard.getelement(bomb.iconName + self.playerName)
            bombIcon.Opacity = 1


    def selectBomb (self, bombIconTarget, args):
        if (self != self.gameboard.currentArsenal):
            return
        if (self.selectedBomb != None):
            self.gameboard.getelement(self.selectedBomb.iconName + "Back" \
                + self.playerName).Stroke \
                = self.gameboard.getbrush("black")
            self.selectedBomb = None
        for i in xrange(len(self.bombs)):
            bomb = self.bombs[i]
            bombIcon = self.gameboard.getelement(bomb.iconName + self.playerName)
            if (bombIconTarget.Equals(bombIcon)):
                self.gameboard.getelement(bomb.iconName + "Back" + self.playerName).Stroke \
                    = self.gameboard.getbrush("white")
                self.selectedBomb = bomb

