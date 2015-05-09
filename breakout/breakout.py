# breakout.py
# Michelle Nelson (mhn29)
# 12/10/14
"""Primary module for Breakout application

This module contains the App controller class for the Breakout application.
There should not be any need for additional classes in this module.
If you need more classes, 99% of the time they belong in either the gameplay
module or the models module. If you are ensure about where a new class should go, 
post a question on Piazza."""
from constants import *
from gameplay import *
from game2d import *


# PRIMARY RULE: Breakout can only access attributes in gameplay.py via getters/setters
# Breakout is NOT allowed to access anything in models.py

class Breakout(GameApp):
    """Instance is a Breakout App
    
    This class extends GameApp and implements the various methods necessary 
    for processing the player inputs and starting/running a game.
    
        Method init starts up the game.
        
        Method update either changes the state or updates the Gameplay object
        
        Method draw displays the Gameplay object and any other elements on screen
    
    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the init method instead.  This is only for this class.  All other classes
    behave normally.
    
    Most of the work handling the game is actually provided in the class Gameplay.
    Gameplay should have a minimum of two methods: updatePaddle(touch) which moves
    the paddle, and updateBall() which moves the ball and processes all of the
    game physics. This class should simply call that method in update().
    
    The primary purpose of this class is managing the game state: when is the 
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.
    
    INSTANCE ATTRIBUTES:
        view     [Immutable instance of GView, it is inherited from GameApp]:
            the game view, used in drawing (see examples from class)
        _state   [one of STATE_INACTIVE, STATE_COUNTDOWN, STATE_PAUSED, STATE_ACTIVE]:
            the current state of the game represented a value from constants.py
        _last    [GPoint, or None if mouse button is not pressed]:
            the last mouse position (if Button was pressed)
        _game    [GModel, or None if there is no game currently active]: 
            the game controller, which manages the paddle, ball, and bricks
    
    ADDITIONAL INVARIANTS: Attribute _game is only None if _state is STATE_INACTIVE.
        
    
    You may have more attributes if you wish (you might need an attribute to store
    any text messages you display on the screen). If you add new attributes, they
    need to be documented here.
    
    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    
    INSTANCE ATTRIBUTES
        _message [GLabel, or None if the game is being played]
            the welcome message, which is displayed before the game begins
        _time [int >= 0] the time since _state changed to STATE_COUNTDOWN
        _success [Boolean] True if game is won, False is game is lost
    
    ADDITIONAL INVARIANTS
        Attribute _message is None if _state is STATE_ACTIVE,
            otherwise _message is of type GLabel
        Attribute _time is 0 if _state is STATE_INACTIVE
    
    """
    
    # DO NOT MAKE A NEW INITIALIZER!
    
    # GAMEAPP METHODS
    def init(self):
        """Initialize the game state.
        
        This method is distinct from the built-in initializer __init__.
        This method is called once the game is running. You should use
        it to initialize any game specific attributes.
        
        This method should initialize any state attributes as necessary 
        to statisfy invariants. When done, set the _state to STATE_INACTIVE
        and create a message (in attribute _message) saying that the user should 
        press to play a game."""
        
        self._last = None
        self._game = None          
        self._time = 0
        self._success = False
        self._state = STATE_INACTIVE
        self._message = GLabel(
            x=GAME_WIDTH/2,
            y=GAME_HEIGHT/2,
            halign='center',
            valign='middle',
            text='Click to play!\n\nLives: 3',
            font_name='Akashi.ttf',
            font_size=40)
        
    def update(self,dt):
        """Animate a single frame in the game.
        
        It is the method that does most of the work. Of course, it should
        rely on helper methods in order to keep the method short and easy
        to read.  Some of the helper methods belong in this class, but most
        of the others belong in class Gameplay.
        
        The first thing this method should do is to check the state of the
        game. We recommend that you have a helper method for every single
        state: STATE_INACTIVE, STATE_COUNTDOWN, STATE_PAUSED, STATE_ACTIVE.
        The game does different things in each state.
        
        In STATE_INACTIVE, the method checks to see if the player clicks
        the mouse (_last is None, but view.touch is not None). If so, it 
        (re)starts the game and switches to STATE_COUNTDOWN.
        
        STATE_PAUSED is similar to STATE_INACTIVE. However, instead of 
        restarting the game, it simply switches to STATE_COUNTDOWN.
        
        In STATE_COUNTDOWN, the game counts down until the ball is served.
        The player is allowed to move the paddle, but there is no ball.
        Paddle movement should be handled by class Gameplay (NOT in this class).
        This state should delay at least one second.
        
        In STATE_ACTIVE, the game plays normally.  The player can move the
        paddle and the ball moves on its own about the board.  Both of these
        should be handled by methods inside of class Gameplay (NOT in this class).
        Gameplay should have methods named updatePaddle and updateBall.
        
        While in STATE_ACTIVE, if the ball goes off the screen and there
        are tries left, it switches to STATE_PAUSED.  If the ball is lost 
        with no tries left, or there are no bricks left on the screen, the
        game is over and it switches to STATE_INACTIVE.  All of these checks
        should be in Gameplay, NOT in this class.
        
        You are allowed to add more states if you wish. Should you do so,
        you should describe them here.
        
        Precondition: dt is the time since last update (a float).  This
        parameter can be safely ignored. It is only relevant for debugging
        if your game is running really slowly. If dt > 0.5, you have a 
        framerate problem because you are trying to do something too complex."""
        
        if (self._state == STATE_INACTIVE):
            if (self._last == None and self.view.touch != None):
                self._last = self.view.touch
                self._state = STATE_COUNTDOWN
                self._game = Gameplay()
            self._last = self.view.touch
        
        if self._state == STATE_COUNTDOWN:
            self._game.updatePaddle(self.view.touch)
            self.__countdownhelper()
            
        if self._state == STATE_PAUSED:
            if (self._last == None and self.view.touch != None):
                self._state = STATE_PAUSED_COUNTDOWN
                self._game.set_tries(self._game.get_tries()-1)
            self._last = self.view.touch
        
        if self._state == STATE_PAUSED_COUNTDOWN:
            self._game.resetball()
            self._game.updatePaddle(self.view.touch)
            self._game.set_lostlife(False)
            self.__countdownhelper()
        
        if self._state == STATE_ACTIVE:
            self._game.updatePaddle(self.view.touch)
            self._game.moveBall()
            self.__active()
            
        if self._state == STATE_GAME_OVER:
            self.__gameover()
    
    def draw(self):
        """Draws the game objects to the view.
        
        Every single thing you want to draw in this game is a GObject. 
        To draw a GObject g, simply use the method g.draw(view).  It is 
        that easy!
        
        Many of the GObjects (such as the paddle, ball, and bricks) are
        attributes in Gameplay. In order to draw them, you either need to
        add getters for these attributes or you need to add a draw method
        to class Gameplay.  We suggest the latter.  See the example 
        subcontroller.py from class."""
        
        if (self._message != None):
            self._message.draw(self.view)
        if (self._game != None):
            self._game.draw(self.view)
    
    # HELPER METHODS FOR THE STATES GO HERE
    def __countdownhelper(self):
        """Displays the countdown messages before the game begins or when paused
        
        Changes the countdown message depending on the variable _time, which
        is incremented +1 every time the funciton is called
        After three seconds, _state is changed to active, _message is changed
        to None, and the game begins
        """
        
        if self._time < 60:
            self._message = GLabel(
                x=GAME_WIDTH/2,
                y=GAME_HEIGHT/2 - GAME_HEIGHT/5,
                halign='center',
                valign='middle',
                text='3',
                font_name='Akashi.ttf',
                font_size=60)
        elif self._time < 120:
            self._message = GLabel(
                x=GAME_WIDTH/2,
                y=GAME_HEIGHT/2 - GAME_HEIGHT/5,
                halign='center',
                valign='middle',
                text='2',
                font_name='Akashi.ttf',
                font_size=60)
            self._message.font_size = 60
        elif self._time < 180:
            self._message = GLabel(
                x=GAME_WIDTH/2,
                y=GAME_HEIGHT/2 - GAME_HEIGHT/5,
                halign='center',
                valign='middle',
                text='1',
                font_name='Akashi.ttf',
                font_size=60)
        elif self._time >= 180:
            self._message = None
            self._state = STATE_ACTIVE   
        self._time = self._time + 1
    
    def __active(self):
        """Carries out changes in _state from STATE_ACTIVE
        
        If the ball hits the bottom and the player still has lives, the game
        is paused and a message is displayed. If the game is lost and the player
        has no more lives or if the game is won, the state is switched to
        the game over state.
        """
        if (self._game.get_lostlife() and self._game.get_tries()>0):
            self._state = STATE_PAUSED
            self._message = GLabel(
                x=GAME_WIDTH/2,
                y=GAME_HEIGHT/2,
                halign='center',
                valign='middle',
                text='Lost a life!\nClick for a new ball\n\nLives: '+`self._game.get_tries()`,
                font_name='Akashi.ttf',
                font_size=40)
            self._time = 0
        if (self._game.get_lostlife() and self._game.get_tries()==0):
            self._game = None
            self._state = STATE_GAME_OVER
        elif self._game.wall_none():
            self._success = True
            self._game = None
            self._state = STATE_GAME_OVER
    
    def __gameover(self):
        """Displays the game over screen and gives the option to play again
        
        The displayed message depends on if the game was won or lost. After the
        user clicks again, a new game is begun by calling the initalizer.
        
        Precondition: _game is None
        """
        
        if self._success:
            msgtxt = 'You win!\nClick to start over'
        else:
            msgtxt = 'Game over!\nClick to start over'
        self._message = GLabel(
                x=GAME_WIDTH/2,
                y=GAME_HEIGHT/2,
                halign='center',
                valign='middle',
                text=msgtxt,
                font_name='Akashi.ttf',
                font_size=40)
        if (self._last == None and self.view.touch != None):
            self.init()
        self._last = self.view.touch
    
    
