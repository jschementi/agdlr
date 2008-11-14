Import("System");
Import("System.Windows")
Import("System.Windows.Interop.*") // need BrowserHost.Resize event from here
Import("System.Windows.Controls.Canvas")

xaml = System.Windows.Application.Current.LoadRootVisual(new Canvas, 'collateral.xaml')
xaml.Subroot.Loaded += handleLoad;

function dump(str)
{
	//xaml.tracer.Text+="\n"+str;
	
}

var silverhostcontent = System.Windows.Application.Current.Host.Content;


var gameboard = null;
var gameControl = null;

function handleLoad(sender, args) {

	dump("handleload()");
	
    gameControl = sender;
    gameboard = new Gameboard(gameControl.findName('Root'), 10, 10);       

    handleResize();

	dump("handleload() out");

}

function handleResize(sender, eventArgs) {

//	dump("handleresize()");
	
    // new window width and height that we'd like to resize to
    var frameWidth = silverhostcontent.ActualWidth
    var frameHeight = silverhostcontent.ActualHeight

    if (gameboard) {
        gameboard.resize(frameWidth - 20, frameHeight - 20);
    }

//	dump("handleresize() out");

}

silverhostcontent.Resized += new System.EventHandler(handleResize);

// Represents each tile position in the gameboard.
function Tile(x, y, gameboard) {

//dump("tile()");

    this.x = x;
    this.y = y;
    this.gameboard = gameboard;

    // these elements are defined in the xaml file.
    this.groundTile = this.gameboard.target.FindName("groundTile" + this.x + "_" + this.y);
    this.playTile = this.gameboard.target.FindName("playTile" + this.x + "_" + this.y);
    this.markingTile = this.gameboard.target.FindName("markingTile" + this.x + "_" + this.y);
    this.markingTileParent = this.gameboard.target.FindName("markingTileParent" + this.x + "_" + this.y);
    this.markingTileParent.MouseEnter += delegate(this, this.handleMarkerEnter);
    this.markingTileParent.MouseLeftButtonDown += delegate(this, this.handleMarkerClick);

//dump("tile() out");
}

Tile.prototype.state = 0;
Tile.prototype.isMarked = false;

// Updates what state the tile is in-
//      0 = empty
//      1 = Red
//      2 = Blue
Tile.prototype.setState = function(state) {

//dump("setstate() "+state);

    this.state = state;


    switch(state) {
        case 0:
            //this.playTile.Source = new System.Uri("",System.UriKind.Relative);
            
			tempuri = new System.Uri("",System.UriKind.Relative);
            tempimage = new System.Windows.Media.Imaging.BitmapImage(tempuri);
            this.playTile.Source = tempimage; 
            
            this.unmark();
            break;
        case 1:
            //this.playTile.Source = new System.Uri("red.png",System.UriKind.Relative);

			tempuri = new System.Uri("red.png",System.UriKind.Relative);
            tempimage = new System.Windows.Media.Imaging.BitmapImage(tempuri);
            this.playTile.Source = tempimage; 
            break;
        case 2:
            //this.playTile.Source = new System.Uri("blue.png",System.UriKind.Relative);

			tempuri = new System.Uri("blue.png",System.UriKind.Relative);
            tempimage = new System.Windows.Media.Imaging.BitmapImage(tempuri);
            this.playTile.Source = tempimage; 
            break;
    }

    
//dump("setstate() out");    
}

// Set this tile as marked for explosion.
// Shows the yellow bomb marking squares over the square.
Tile.prototype.mark = function() {
    this.markingTile.opacity = 1;
    this.isMarked = true;
}

// Clear the bomb marking on this tile.
Tile.prototype.unmark = function() {
    if (this.isMarked) {
        this.markingTile.opacity = 0.01;
        this.isMarked = false;
    }
}

// Handler for mouse enter over this tile, for moving the bomb marker.
Tile.prototype.handleMarkerEnter = function() {
    this.gameboard.markFromTile(this);
}

// Used for triggering dropping the bomb.
Tile.prototype.handleMarkerClick = function() {
    this.gameboard.dropBomb();
}

// Random helper class.
function Point(x, y) {
    this.x = x;
    this.y = y;
}

// Bomb class, represents bombing pattern and icon
function Bomb(name, iconName) {
    this.name = name;
    this.iconName = iconName;
    this.points = new Array();
}

// Mark the tiles on the gameboard this will effect
Bomb.prototype.mark = function(gameboard, x, y) {
    for (var i = 0; i < this.points.length; ++i)
        this.markPoint(gameboard, x + this.points[i].x, y + this.points[i].y);
}

Bomb.prototype.markPoint = function(gameboard, x, y) {
    if (x >= 0 && x < gameboard.width) {
        if (y >= 0 && y < gameboard.height) {
            gameboard.tiles[gameboard.width * x + y].mark();
        }
    }
}

// Main logic for the entire app.
// width and height are the number of tiles in x and y direction
// Gameboard object
function Gameboard(target, width, height) {

dump("gameboard() - "+typeof(target));

    this.target = target;
    this.width = width;
    this.height = height;

    this.initialize();
    
dump("gameboard() out");
}

Gameboard.prototype.scoreRed = 0;
Gameboard.prototype.scoreBlue = 0;
Gameboard.prototype.tiles = null;
Gameboard.prototype.bombs = null;
Gameboard.prototype.redScore = 0;
Gameboard.prototype.blueScore = 0;
Gameboard.prototype.turn = 0;

// Gameboard initialization function
Gameboard.prototype.initialize = function() {

dump("gameboard.init() - "+typeof(this.tiles));

    this.tiles = new Array();
    
    for (var i = 0; i < this.width; ++i) {
        for (var j = 0; j < this.height; ++j) {
			var temp = new Tile(i, j, this);
            this.tiles.push(temp);
        }
    }

dump("made"+ this.tiles.length+ " tiles");

    var redRemaining = this.width * this.height / 2;
    var blueRemaining = redRemaining;

    for (var i = 0; i < this.tiles.length; ++i) {
        var newState = Math.round(Math.random() + 1);
        if ((newState == 1 && redRemaining > 0) || blueRemaining == 0) {
            --redRemaining;
            newState = 1;
        }
        else {
            --blueRemaining;
            newState = 2;
        }
        
        this.tiles[i].setState(newState);
        
    }

    this.createBombs();

dump("created bombs");

    this.redScoreBox = this.target.FindName("RedScore");
    this.blueScoreBox = this.target.FindName("BlueScore");
    this.player1TurnIndicator = this.target.FindName("Player1TurnIndicatorArrow");
    this.player2TurnIndicator = this.target.FindName("Player2TurnIndicatorArrow");
    this.root = this.target.FindName("Root");

    this.target.FindName("Gameboard").MouseLeave += delegate(this, this.handleMouseLeave);

    this.updateScore();

    this.turn = Math.round(Math.random());

    this.player1Arsenal = new Arsenal("1", this);
    this.player2Arsenal = new Arsenal("2", this);

    this.updatePlayerStatus();


dump("gameboard.init() out");

}

// Creates all the bombs the game will be using.
Gameboard.prototype.createBombs = function() {
    this.bombs = new Array();

    bomb = new Bomb("Broken Arrow", "BlackBomb");
    bomb.points.push(new Point(-1, -1));
    bomb.points.push(new Point(-1, -0));
    bomb.points.push(new Point(-1, 1));
    bomb.points.push(new Point(0, 1));
    bomb.points.push(new Point(1, 1));
    this.bombs.push(bomb);

    bomb = new Bomb("ScatterA", "RedBomb");
    bomb.points.push(new Point(0, 1));
    bomb.points.push(new Point(-1, 0));
    bomb.points.push(new Point(1, 0));
    bomb.points.push(new Point(0, -1));
    this.bombs.push(bomb);

    bomb = new Bomb("Napalm", "BigRoundBomb");
    bomb.points.push(new Point(2, 0));
    bomb.points.push(new Point(2, 1));
    bomb.points.push(new Point(1, 0));
    bomb.points.push(new Point(1, 1));
    bomb.points.push(new Point(0, 0));
    bomb.points.push(new Point(0, 1));
    bomb.points.push(new Point(-1, 0));
    bomb.points.push(new Point(-1, 1));
    bomb.points.push(new Point(-2, 0));
    bomb.points.push(new Point(-2, 1));
    bomb.points.push(new Point(-3, 0));
    bomb.points.push(new Point(-3, 1));
    this.bombs.push(bomb);

    bomb = new Bomb("Trident", "purpleBomb");
    bomb.points.push(new Point(-1,0));
    bomb.points.push(new Point(0,0));
    bomb.points.push(new Point(1,0));
    this.bombs.push(bomb);

    bomb = new Bomb("Crossbow", "SkyBlueBomb");
    bomb.points.push(new Point(-2, 0));
    bomb.points.push(new Point(-1, 0));
    bomb.points.push(new Point(0, 0));
    bomb.points.push(new Point(1, 0));
    bomb.points.push(new Point(2, 0));
    bomb.points.push(new Point(0, -1));
    bomb.points.push(new Point(0, -2));
    bomb.points.push(new Point(0, 1));
    bomb.points.push(new Point(0, 2));
    this.bombs.push(bomb);

    bomb = new Bomb("Cluster", "BlueBomb");
    bomb.points.push(new Point(-2, -2));
    bomb.points.push(new Point(-2, 0));
    bomb.points.push(new Point(-2, 2));
    bomb.points.push(new Point(0, -2));
    bomb.points.push(new Point(0, 0));
    bomb.points.push(new Point(0, 2));
    bomb.points.push(new Point(2, -2));
    bomb.points.push(new Point(2, 0));
    bomb.points.push(new Point(2, 2));
    this.bombs.push(bomb);

    bomb = new Bomb("Bunker Buster", "SmallRoundBomb");
    bomb.points.push(new Point(-2, -2));
    bomb.points.push(new Point(-2, -2));
    bomb.points.push(new Point(-1, -2));
    bomb.points.push(new Point(0, -2));
    bomb.points.push(new Point(1, -2));
    bomb.points.push(new Point(2, -2));
    bomb.points.push(new Point(-2, 2));
    bomb.points.push(new Point(-1, 2));
    bomb.points.push(new Point(0, 2));
    bomb.points.push(new Point(1, 2));
    bomb.points.push(new Point(2, 2));
    bomb.points.push(new Point(-2, -1));
    bomb.points.push(new Point(-2, -0));
    bomb.points.push(new Point(-2, 1));
    bomb.points.push(new Point(2, -1));
    bomb.points.push(new Point(2, 0));
    bomb.points.push(new Point(2, 1));
    bomb.points.push(new Point(0, 0));
    this.bombs.push(bomb);

    bomb = new Bomb("Barrage", "GreyBomb");
    bomb.points.push(new Point(-2, -2));
    bomb.points.push(new Point(-1, -1));
    bomb.points.push(new Point(0, 0));
    bomb.points.push(new Point(1, 1));
    bomb.points.push(new Point(2, 2));
    this.bombs.push(bomb);
}

Gameboard.prototype.markFromTile = function(tile) {
    for (var i = 0; i < this.tiles.length; ++i) {
        this.tiles[i].unmark();
    }

    if (this.currentArsenal && this.currentArsenal.selectedBomb)
        this.currentArsenal.selectedBomb.mark(this, tile.x, tile.y);
}

Gameboard.prototype.dropBomb = function() {
    if (this.currentArsenal && this.currentArsenal.selectedBomb) {
        for (var i = 0; i < this.tiles.length; ++i) {
            if (this.tiles[i].isMarked)
                this.tiles[i].setState(0);
        }

        this.updateScore();

        this.currentArsenal.bombAndPopulate();

        this.turn = (this.turn + 1) % 2;
        this.updatePlayerStatus();
    }
}

Gameboard.prototype.updatePlayerStatus = function() {

    if (this.currentArsenal)
        this.currentArsenal.deactivate();
    this.currentArsenal = null;

    if (this.turn == 0) {
        this.currentArsenal = this.player1Arsenal;
        this.player1TurnIndicator.opacity = 1;
        this.player2TurnIndicator.opacity = 0;
    }
    else if (this.turn == 1) {
        this.currentArsenal = this.player2Arsenal;
        this.player1TurnIndicator.opacity = 0;
        this.player2TurnIndicator.opacity = 1;
    }

    if (this.currentArsenal)
        this.currentArsenal.activate();
}

Gameboard.prototype.handleMouseLeave = function(sender, eventArgs) { 
    for (var i = 0; i < this.tiles.length; ++i)
        this.tiles[i].unmark();
}

Gameboard.prototype.updateScore = function() {
    this.redScore = 0;
    this.blueScore = 0;
    for (var i = 0; i < this.tiles.length; ++i) {
        if (this.tiles[i].state == 1)
            ++this.redScore;
        else if (this.tiles[i].state == 2)
            ++this.blueScore;
    }

    if (this.redScore == 0 && this.blueScore != 0) {
        this.redScoreBox.text = "LOSER";
        this.blueScoreBox.text = "WINNER";
        this.turn = -1;
    }
    else if (this.blueScore == 0 && this.redScore != 0) {
        this.redScoreBox.text = "WINNER";
        this.blueScoreBox.text = "LOSER";
        this.turn = -1;
    }
    else
    {
        this.redScoreBox.text= this.redScore.toString();
        this.blueScoreBox.text = this.blueScore.toString();
    }
}

// Function to set the transform to make the entire gameboard (the root element)
// near the same size of the browser window
// The function attempts to keep the aspect ratio intact as much as possible.
Gameboard.prototype.resize = function(width, height) {
    var coreWidth = this.root.width;
    var coreHeight = this.root.height;
    var ratio = coreWidth / coreHeight;

    if (width / ratio > height)
        width = height * ratio;
    else
        height = width / ratio;

    var rootScale = this.target.FindName("RootScaleTransform");
    rootScale.scaleX = width / coreWidth;
    rootScale.scaleY = height / coreHeight;
}

function Arsenal(playerName, gameboard) {

//dump("arsenal()");
    this.playerName = playerName;
    this.gameboard = gameboard;

    for (var i = 0; i < gameboard.bombs.length; ++i) {
        var bomb = gameboard.bombs[i];
        var bombIcon = gameboard.target.FindName(bomb.iconName + playerName);
        bombIcon.opacity = 0;

        bombIcon.MouseLeftButtonDown += delegate(this, this.selectBomb);
    }

    this.bombs = new Array();
    this.bombAndPopulate();
    this.deactivate();
//dump("arsenal() out");
}

Arsenal.prototype.selectedBomb = null;

Arsenal.prototype.bombAndPopulate = function() {
//dump("populate()");
    if (this.selectedBomb != null) {
        this.gameboard.target.FindName(this.selectedBomb.iconName + this.playerName).opacity = 0;
        this.gameboard.target.FindName(this.selectedBomb.iconName + "Back" + this.playerName).Stroke = new Windows.Media.SolidColorBrush(Windows.Media.Colors.Transparent);;


        for (var i = 0; i < this.bombs.length; ++i)
            if (this.bombs[i] == this.selectedBomb) {
                this.bombs = this.bombs.splice(i, i);
                break;
            }
    }

    while (this.bombs.length < 3) {
        var index = Math.round(Math.random() * (this.gameboard.bombs.length - 1));

        var newBomb = this.gameboard.bombs[index];
        var hasBomb = false;
        for (var i = 0; i < this.bombs.length; ++i) {
            if (this.bombs[i] == newBomb)
                hasBomb = true;
        }

        if (!hasBomb && (newBomb != this.selectedBomb)) {
            this.bombs.push(newBomb);
        }
    }



    // Shouldn't be necessary....
    for (var i = 0; i < this.gameboard.bombs.length; ++i) {
        var bomb = this.gameboard.bombs[i];
        var bombIcon = this.gameboard.target.FindName(bomb.iconName + this.playerName);
        bombIcon.opacity = 0;
        bombIcon.SetValue(Windows.Controls.Canvas.LeftProperty, -105); // Get it out of the way
        this.gameboard.target.FindName(bomb.iconName + "Back" + this.playerName).Stroke = new Windows.Media.SolidColorBrush(Windows.Media.Colors.Transparent);

    }
    

    for (var i = 0; i < this.bombs.length; ++i) {
        var bomb = this.bombs[i];
        var bombIcon = this.gameboard.target.FindName(bomb.iconName + this.playerName);
        bombIcon.opacity = 1;
        bombIcon.SetValue(Windows.Controls.Canvas.LeftProperty, i * 105);
        this.gameboard.target.FindName(bomb.iconName + "Back" + this.playerName).Stroke = new Windows.Media.SolidColorBrush(Windows.Media.Colors.Transparent);
    }

    this.selectedBomb = null;

//dump("populate() out");

}

Arsenal.prototype.deactivate = function() {
    for (var i = 0; i < this.bombs.length; ++i) {
        var bomb = this.bombs[i];
        var bombIcon = this.gameboard.target.FindName(bomb.iconName + this.playerName);
        bombIcon.opacity = .5;
    }
}

Arsenal.prototype.activate = function() {
    for (var i = 0; i < this.bombs.length; ++i) {
        var bomb = this.bombs[i];
        var bombIcon = this.gameboard.target.FindName(bomb.iconName + this.playerName);
        bombIcon.opacity = 1;
    }
}

Arsenal.prototype.selectBomb = function(bombIconTarget) {
    if (this != this.gameboard.currentArsenal)
        return;

    if (this.selectedBomb != null) {
        this.gameboard.target.FindName(this.selectedBomb.iconName + "Back" + this.playerName).stroke = new Windows.Media.SolidColorBrush(Windows.Media.Colors.Transparent);
        this.selectedBomb = null;
    }

    for (var i = 0; i < this.bombs.length; ++i) {
        var bomb = this.bombs[i];
        var bombIcon = this.gameboard.target.FindName(bomb.iconName + this.playerName);

        if (bombIconTarget.equals(bombIcon)) {
            this.gameboard.target.FindName(bomb.iconName + "Back" + this.playerName).stroke = new Windows.Media.SolidColorBrush(Windows.Media.Colors.White);
            this.selectedBomb = bomb;
        }
    }
    
}

// Implements a delegate by calling the apply() method on the function object
function delegate(target, callback) {
    var func = function() {
        callback.apply(target, arguments);
    }
    return func;
}
