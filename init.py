import pygame, math, random, sys, os, hashlib
from Box2D import *
import time
from pygame.locals import *


pygame.init()

screen = pygame.display.set_mode((800,600), DOUBLEBUF)
pygame.display.set_caption("Project Hiatus")
clock = pygame.time.Clock()

# Get x and y of shape objects
getx = lambda shape: shape.GetWorldPoint(localPoint = (0, 0)).x
gety = lambda shape: shape.GetWorldPoint(localPoint = (0, 0)).y

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
    

    

    