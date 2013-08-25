import pygame, math, random, sys, os, hashlib
from Box2D import *
import Box2D
import time
from pygame.locals import *

STAGE_WIDTH_PX = 3200
STAGE_WIDTH_M = 200
SCREEN_WIDTH_PX = 800
SCREEN_WIDTH_M = 50
SCREEN_HEIGHT_PX = 600
SCREEN_HEIGHT_M = 37.5
PPM = 16

CAMERA_MAX_PAN_SPEED_PX = 48
CAMERA_MAX_PAN_SPEED_M = 3
CAMERA_PILLOW_SPACE_PX = 160
CAMERA_PILLOW_SPACE_M = 10
CAMERA_SPEEDUP_SPEED = 3

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
    
        goalLeft = self.checkContact(contact, "ball")
        if goalLeft is not None:
            # mass > 0 implies it's not a "Static" object
            if goalLeft[1].body.userData is not None or goalLeft[1].userData is not None:
                if goalLeft[1].userData == "goal left":
                    arena.score[0] += 1
                    if arena.score[0] >= 10:
                        winGame(1)
                    arena.player1.dead = True
                    arena.player2.dead = True
                    arena.toInit = (STAGE_WIDTH_M / 3, 2000)
                if goalLeft[1].userData == "goal right":
                    arena.score[1] += 1
                    if arena.score[1] >= 10:
                        winGame(2)
                    arena.player1.dead = True
                    arena.player2.dead = True
                    arena.toInit = (STAGE_WIDTH_M * 2 / 3, 2000)