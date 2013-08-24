import pygame, math, random, sys, os, hashlib
from Box2D import *
import Box2D
import time
from pygame.locals import *


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF, 32)
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
        
    def checkContact(self, contact, desiredName):
        """Checks to see if one of the fixtures named by "contact" is a 
        "desiredName." Returns (desiredFixture, otherFixture) if there's a match"""
        if contact.fixtureA.body.userData == desiredName:
            return (contact.fixtureA, contact.fixtureB)
        if contact.fixtureB.body.userData == desiredName:
            return (contact.fixtureB, contact.fixtureA)
            
        return None
        
    def BeginContact(self, contact):
        
        blowUp = self.checkContact(contact, "land mine")
        if blowUp is not None:
            # mass > 0 implies it's not a "Static" object
            if blowUp[1].massData.mass > 0:
                # Destroy the land mine and apply a HUGE force to the other guy
                # Since you can't call DestroyFixture while the physics is iterating,
                # flag it for destruction by setting userData to "kill me"
                blowUp[0].body.userData = "kill me"
                blowUp[1].body.ApplyForce(force=(50000, 0), point=(0, 0), wake=True)
                explos = Explosion(blowUp[0].body.position.x * PPM,
                                    blowUp[0].body.position.y * PPM)
                effects.append(explos)  
                   
        # "Soccer" game win condition
        goooal = self.checkContact(contact, "goal")
        if goooal is not None:
            # Verify that the soccer ball is the thing in the goal
            if goooal[1].body.userData == "soccer ball":
                print("GOOOOAL YOU DID IT SUCCESS AND STUFF")
                
        kick = self.checkContact(contact, "soccer ball")
        if kick is not None:
            # mass > 0 implies it's not a "Static" object
            if kick[1].massData.mass > 0:
                if(kick[0].body.position.x > kick[1].body.position.x):
                    kick[0].body.ApplyForce(force=(3000,-1000),point=(0,0), wake=True)
                else:
                    kick[0].body.ApplyForce(force=(-3000,-1000),point=(0,0), wake=True)
