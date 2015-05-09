# gameplay.py
# Michelle Nelson (mhn29)
# 12/10/14
"""Subcontroller module for Breakout

This module contains the subcontroller to manage a single game in the Breakout App. 
Instances of Gameplay represent a single game.  If you want to restart a new game,
you are expected to make a new instance of Gameplay.

The subcontroller Gameplay manages the paddle, ball, and bricks.  These are model
objects.  The ball and the bricks are represented by classes stored in models.py.
The paddle does not need a new class (unless you want one), as it is an instance
of GRectangle provided by game2d.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer."""
from constants import *
from game2d import *
from models import *


# PRIMARY RULE: Gameplay can only access attributes in models.py via getters/setters
# Gameplay is NOT allowed to access anything in breakout.py (Subcontrollers are not
# permitted to access anything in their parent. To see why, take CS 3152)


class Gameplay(object):
    """An instance controls a single game of breakout.
    
    This subcontroller has a reference to the ball, paddle, and bricks. It
    animates the ball, removing any bricks as necessary.  When the game is
    won, it stops animating.  You should create a NEW instance of 
    Gameplay (in Breakout) if you want to make a new game.
    
    If you want to pause the game, tell this controller to draw, but do not
    update.  See subcontrollers.py from Lecture 24 for an example.
    
    INSTANCE ATTRIBUTES:
        _wall   [BrickWall]:  the bricks still remaining 
        _paddle [GRectangle]: the paddle to play with 
        _ball [Ball, or None if waiting for a serve]: 
            the ball to animate
        _last [GPoint, or None if mouse button is not pressed]:  
            last mouse position (if Button pressed)
        _tries  [int >= 0]:   the number of tries left 
    
    As you can see, all of these attributes are hidden.  You may find that you
    want to access an attribute in call Breakout. It is okay if you do, but
    you MAY NOT ACCESS THE ATTRIBUTES DIRECTLY. You must use a getter and/or
    setter for any attribute that you need to access in Breakout.  Only add
    the getters and setters that you need for Breakout.
    
    You may change any of the attributes above as you see fit. For example, you
    might want to make a Paddle class for your paddle.  If you make changes,
    please change the invariants above.  Also, if you add more attributes,
    put them and their invariants below.
                  
    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    
    INSTANCE INVARIANTS
        _clickdist [float, 0 if paddle hasn't been clicked]
            the horizontal distance between the left edge of the paddle and
            the point where the paddle was clicked
        _lostlife [boolean]
            False during regular game play
            True when the ball hits the bottom; pauses the game.
    """
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def get_tries(self):
        """Returns the number of tries left in the game"""
        return self._tries
    
    def get_lostlife(self):
        """Returns True if the player lost a life, False otherwise."""
        return self._lostlife
    
    def set_tries(self,lives):
        """Sets the number of tries the value lives
        
        Precondition: lives >= 0"""
        self._tries = lives
    
    def set_lostlife(self,lostlife):
        """Sets _lostlife
        
        Precondition: lostlife is a Boolean"""
        self._lostlife = lostlife
    
    # INITIALIZER (standard form) TO CREATE PADDLES AND BRICKS
    def __init__(self):
        """Creates the necessary objects and conditions for playing the game
        
        The brickwall is created as a BrickWall object, and the paddle is a
        GRectangle object. The ball is created as a Ball object.
        Since the player has not lost a life yet (the game hasn't started),
        _lost life is False and _tries is 2.
        """
        
        self._wall = BrickWall()  
        self._paddle = GRectangle(
            x=GAME_WIDTH/2 - PADDLE_WIDTH/2,
            y=PADDLE_OFFSET,
            width=PADDLE_WIDTH,
            height=PADDLE_HEIGHT,
            fillcolor = PADDLE_COLOR)
        self._clickdist = 0
        self._ball = Ball()  
        self._last = None
        self._tries = 2
        self._lostlife = False
    
    # DRAW METHOD TO DRAW THE PADDLES, BALL, AND BRICKS
    def draw(self, view):
        """Draws the game objects to the view.
        
        This is the draw method necessary for the objects to be drawn in breakout.
        This method draws the Brickwall, paddle (type: GRectangle) and Ball objects.
        
        Precondition: view is an instance of GView
        """
        self._wall.draw(view)
        self._paddle.draw(view)
        self._ball.draw(view)
    
    # UPDATE METHODS TO MOVE PADDLE, SERVE AND MOVE THE BALL
    def updatePaddle(self, touch):
        """
        Checks if the player has clicked and changes the paddle accordingly.
        
        If the player clicks the mouse, the horizontal distance between the
        mouse position and the position of the left edge of the paddle is
        recorded (as _clickdist). If the player holds the mouse down, the paddle
        moves according to how much the mouse as moved. Teleportation is
        prevented using _clickdist. The paddle can't extend past the left or
        right edges of the game container.
        
        Precondition: touch is a GPoint or None
        """
        #first click
        if (touch != None and self._last == None):
            self._clickdist = touch.x - self._paddle.x
        
        #click hold - paddle movement
        if (self._last != None and touch != None):
            self._paddle.x = touch.x - self._clickdist
            
            #prevent paddle from extending past right edge
            if self._paddle.x > (GAME_WIDTH - PADDLE_WIDTH):
                self._paddle.x = GAME_WIDTH - PADDLE_WIDTH
            
            #prevent paddle from extending past left edge
            if self._paddle.x < 0:
                self._paddle.x = 0
        self._last = touch
    
    def moveBall(self):
        """Moves the ball one step and checks for ball collisions.
        
        Collisions with bricks, the top of the paddle, or the top edge negates
        the vertical velocity of the ball. Collisions with the left/right edge
        negates the horizontal velocity of the ball."""
        
        #move ball one step
        vx = self._ball.get_vx()
        vy = self._ball.get_vy()
        self._ball.x = self._ball.x + vx
        self._ball.y = self._ball.y + vy
        
        #COLLISIONS
        if vy > 0:
            balltop = self._ball.y + BALL_DIAMETER
            if balltop >= GAME_HEIGHT:
                self._ball.set_vy(-vy)
            if (self._getCollidingObject() != None and
                self._getCollidingObject() != self._paddle):
                self._ball.set_vy(-vy)
                self._wall.removebrick(self._getCollidingObject())
        if vy < 0:
            ballbottom = self._ball.y
            if ballbottom <= 0:
                self._lostlife = True
            if self._getCollidingObject() == self._paddle:
                self._ball.set_vy(-vy)
            if (self._getCollidingObject() != None and
                self._getCollidingObject() != self._paddle):
                self._ball.set_vy(-vy)
                self._wall.removebrick(self._getCollidingObject())
        if vx > 0:
            ballright = self._ball.x + BALL_DIAMETER
            if ballright >= GAME_WIDTH:
                self._ball.set_vx(-vx)
        if vx < 0:
            ballleft = self._ball.x
            if ballleft <= 0:
                self._ball.set_vx(-vx)

    # HELPER METHODS FOR PHYSICS AND COLLISION DETECTION
    def _getCollidingObject(self):
        """Returns: GObject that has collided with the ball
        
        This method checks the four corners of the ball, one at a 
        time. If one of these points collides with either the paddle 
        or a brick, it stops the checking immediately and returns the 
        object involved in the collision. It returns None if no 
        collision occurred."""
        corners = [[self._ball.x,self._ball.y],
                [self._ball.x,self._ball.y+BALL_DIAMETER],
                [self._ball.x+BALL_DIAMETER,self._ball.y],
                [self._ball.x+BALL_DIAMETER,self._ball.y+BALL_DIAMETER]]
        
        for point in corners:
            if self._paddle.contains(point[0],point[1]):
                return self._paddle
            for brick in self._wall.getbricks():
                if brick.contains(point[0],point[1]):
                    return brick
        return None
    
    # ADD ANY ADDITIONAL METHODS (FULLY SPECIFIED) HERE
    def resetball(self):
        """Resets the ball object.
        
        This method is used in the Breakout class in the STATE_PAUSED_COUNTDOWN
        after the player has clicked in STATE_PAUSED"""
        self._ball = Ball()
        
    def wall_none(self):
        """Returns: True if the brickwall is empy, False otherwise.
        
        Used to check to see if the game has been won or not"""
        if self._wall.getbricks()==[]:
            return True
        else: return False
    
