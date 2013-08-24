import pygame, math, random, sys, os, hashlib
from Box2D import *
import Box2D
import time
from pygame.locals import *


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
pygame.display.set_caption("LD 27")
clock = pygame.time.Clock()

TARGET_FPS = 60
TIME_STEP = 1.0/TARGET_FPS
PPM = 16

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
    # Fix the coordinates (flip y upside down)
    result = [(v[0] + camera.panx * PPM,  v[1]) for v in result]
    
    return result
    
class ContactHandler(b2ContactListener):
    """Extends the contact listener and can override the sexy, sexy event handling
    methods with its own jazz."""
    
    def __init__(self):
        # The nonsense that's required to extend classes in Python
        super(ContactHandler, self).__init__()
        
        # Tell the world that this is who gets contact events
        world.contactListener = self
        
    def __del__(self):
        pass
        
    def BeginContact(self, contact):
        print(contact.fixtureA, contact.fixtureB)
        
    
    
    