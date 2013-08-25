import pygame, math, random, sys, os, hashlib
from Box2D import *
import Box2D
import time
from pygame.locals import *

PPM = 16
STAGE_WIDTH_PX = 4000
STAGE_WIDTH_M = STAGE_WIDTH_PX / PPM
SCREEN_WIDTH_PX = 1400
SCREEN_WIDTH_M = SCREEN_WIDTH_PX / PPM
SCREEN_HEIGHT_PX = 600
SCREEN_HEIGHT_M = SCREEN_HEIGHT_PX / PPM

SCREEN_RECT = pygame.Rect(0, 0, SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX)

CAMERA_MAX_PAN_SPEED_PX = 48
CAMERA_MAX_PAN_SPEED_M = 3
CAMERA_PILLOW_SPACE_PX = 160
CAMERA_PILLOW_SPACE_M = 10
CAMERA_SPEEDUP_SPEED = 3

##### VARIABLES FOR GAME BALANCE ######
BALL_DENSITY = 4
BALL_CHANGE_DENSITY = 10
CHAR_DENSITY = 25
BALL_FRICTION = 0.9
CHAR_FRICTION = 100000
CHAR_DENSITY = 5
BALL_FRICTION = 0.95



TARGET_FPS = 60
TIME_STEP = 1.0/TARGET_FPS

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX), DOUBLEBUF, 32)
pygame.display.set_caption("LD 27")
clock = pygame.time.Clock()

def load_image(name, colorkey=None):
    fullname = os.path.join('img', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()
  
def vertices(shapeIn):
    # Grab the old vertices from the shape
    olds = shapeIn.shape.vertices
    # Convert them (with magic) using the body.transform thing
    result = [(shapeIn.body.transform*v)*PPM for v in olds]
    
    return result
  
def vertices_with_offset(shapeIn, offsetX, offsetY):
    # Grab the old vertices from the shape
    olds = shapeIn.shape.vertices
    # Convert them (with magic) using the body.transform thing
    result = [(shapeIn.body.transform*v)*PPM for v in olds]
    # Fix the coordinates
    result = [(v[0] - offsetX,  v[1] - offsetY) for v in result]
    
    return result
    
class ContactHandler(b2ContactListener):
    """Extends the contact listener and can override the sexy, sexy event handling
    methods with its own jazz."""
    
    def __init__(self):
        # The nonsense that's required to extend classes in Python
        super(ContactHandler, self).__init__()
        
    def __del__(self):
        pass
        
    def checkContact(self, contact, desiredName):
        """Checks to see if one of the fixtures named by "contact" is a 
        "desiredName." Returns (desiredFixture, otherFixture) if there's a match"""
        if contact.fixtureA.body.userData == desiredName:
            return (contact.fixtureA, contact.fixtureB)
        if contact.fixtureB.body.userData == desiredName:
            return (contact.fixtureB, contact.fixtureA)
            
        return None
        
    def BeginContact(self, contact):
    
        blowUp = self.checkContact(contact, "bomb")
        if blowUp is not None and blowUp[1].body.userData != "ceiling":
            # Since you can't call DestroyFixture while the physics is iterating,
            # flag it for destruction by setting userData to "kill me"
            blowUp[0].body.userData = "kill me"
            for shape in arena.shapes + [arena.player1.shapes[0], arena.player2.shapes[0]]:
                # See how far everyone is from the 'splosion
                distResult = b2Distance(shapeA = shape.fixtures[0].shape, shapeB = blowUp[0].shape, transformA = shape.fixtures[0].body.transform, transformB = blowUp[0].body.transform)
                pointA, pointB, distance, dummy = distResult
                
                # mass > 0 implies it's not a "Static" object
                if distance < 6 and shape.massData.mass > 0.1:
                    xComp = int(random.random() * -5000 + 2500)
                    yComp = int(random.random() * -5000 + 2500)
                    
                    print xComp, yComp
                    
                    shape.linearVelocity.x = xComp
                    shape.linearVelocity.y = yComp
            
            offsetX, offsetY = arena.camera.getOffset_in_px()
            explos = Explosion(blowUp[0].body.position.x * PPM - offsetX, 37 * PPM - offsetY)
            effects.append(explos)
        
        goalLeft = self.checkContact(contact, "ball")
        if goalLeft is not None:
            # mass > 0 implies it's not a "Static" object
            if goalLeft[1].body.userData is not None or goalLeft[1].userData is not None:
                if goalLeft[1].body.userData == "goal left":
                    arena.score[0] += 1
                    if arena.score[0] >= 10:
                        winGame(1)
                    arena.player1.dead = True
                    arena.player2.dead = True
                    arena.toInit = (STAGE_WIDTH_M / 3, 2000)
                if goalLeft[1].body.userData == "goal right":
                    arena.score[1] += 1
                    if arena.score[1] >= 10:
                        winGame(2)
                    arena.player1.dead = True
                    arena.player2.dead = True
                    arena.toInit = (STAGE_WIDTH_M * 2 / 3, 2000)
                    
        kick = self.checkContact(contact, "player1")
        if kick is None:
            kick = self.checkContact(contact, "player2")
            
        hmm = self.checkContact(contact, "player")
        if hmm is not None:
            print "problematic..."
            
        if kick is not None:
            # Punt the ball a little ways kick[1] is ball, kick[0] is player.
            if kick[1].body.userData == "ball":
                if len(kick[0].body.contacts) < 3:
                    p = kick[1].body.GetWorldPoint(localPoint = (0,0))
                    if kick[0].body.position.x < kick[1].body.position.x:
                        # kick right
                        kick[1].body.linearVelocity.y -= 100
                        kick[1].body.linearVelocity.x =  200
                        print("kick right")
                    else:
                        # kick left
                        kick[1].body.linearVelocity.y -= 100
                        kick[1].body.linearVelocity.x =  -350
                        print("kick left")
                        
            # If the player has touched the ball recently, they're considered
            # "in possession," and have their run speed limited slightly,
            # giving a chance for the chaser to catch up
            arena.gotPossession(kick[0])
