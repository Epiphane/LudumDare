import pygame, math, random, sys, os, hashlib
from Box2D import *
import Box2D
import time
from pygame.locals import *


pygame.init()

screen = pygame.display.set_mode((800,600), DOUBLEBUF)
pygame.display.set_caption("Project Hiatus")
clock = pygame.time.Clock()

TARGET_FPS = 60
TIME_STEP = 1.0/TARGET_FPS

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
    olds = shapeIn.shape.vertices
    posx = shapeIn.body.position.x
    posy = shapeIn.body.position.y
    
    result = []
    
    # Translate the vertices by the position and multiply by like 3
    for vertex in olds:
        newx = (vertex[0] + posx) * 3
        newy = (vertex[1] + posy) * -3
        result.append( (newx, newy) )
        
    return result
    