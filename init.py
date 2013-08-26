import pygame, math, random, sys, os, hashlib
from Box2D import *
import Box2D
import time
from pygame.locals import *
from pgu import gui

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
CHAR_FRICTION = 1
CHAR_DENSITY = 5
BALL_FRICTION = 0.95

TARGET_FPS = 60
TIME_STEP = 1.0/TARGET_FPS

pygame.mixer.pre_init(22050,-16, 2, 1024)
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX), DOUBLEBUF, 32)
pygame.display.set_caption("LD 27: Kickbox")
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
  
def loadSounds():
    result = {}
    
    ## Note- if you add a new sound, make sure to put a number at the end. The parser relies on that.
    
    # Sound effects
    sfxPath = os.path.join("sounds", "sfx")
    result["boom1"] = pygame.mixer.Sound(os.path.join(sfxPath, "boom1.wav"))
    result["boom2"] = pygame.mixer.Sound(os.path.join(sfxPath, "boom2.wav"))
    result["hop1"] = pygame.mixer.Sound(os.path.join(sfxPath, "hop1.wav"))
    result["hop2"] = pygame.mixer.Sound(os.path.join(sfxPath, "hop2.wav"))
    result["hop3"] = pygame.mixer.Sound(os.path.join(sfxPath, "hop3.wav"))
    result["kick1"] = pygame.mixer.Sound(os.path.join(sfxPath, "kick1.wav"))
    result["kick2"] = pygame.mixer.Sound(os.path.join(sfxPath, "kick2.wav"))
    result["transition1"] = pygame.mixer.Sound(os.path.join(sfxPath, "transition1.wav"))
    result["transition2"] = pygame.mixer.Sound(os.path.join(sfxPath, "transition2.wav"))
    result["transition3"] = pygame.mixer.Sound(os.path.join(sfxPath, "transition3.wav"))
    result["start1"] = pygame.mixer.Sound(os.path.join(sfxPath, "start1.wav"))
    result["score1"] = pygame.mixer.Sound(os.path.join(sfxPath, "score1.wav"))
    result["score2"] = pygame.mixer.Sound(os.path.join(sfxPath, "score2.wav"))
    result["score3"] = pygame.mixer.Sound(os.path.join(sfxPath, "score3.wav"))
    
    # 10 second themes
    musicPath = os.path.join("sounds", "music")
    result["background1"] = pygame.mixer.Sound(os.path.join(musicPath, "antigravity1.wav"))
    result["background2"] = pygame.mixer.Sound(os.path.join(musicPath, "chill1.wav"))
    result["background3"] = pygame.mixer.Sound(os.path.join(musicPath, "chill2.wav"))
    result["background4"] = pygame.mixer.Sound(os.path.join(musicPath, "chill3.wav"))
    result["background5"] = pygame.mixer.Sound(os.path.join(musicPath, "chill4.wav"))
    result["background6"] = pygame.mixer.Sound(os.path.join(musicPath, "chill5.wav"))
    result["background7"] = pygame.mixer.Sound(os.path.join(musicPath, "chill6.wav"))
    result["background8"] = pygame.mixer.Sound(os.path.join(musicPath, "chill7.wav"))
    result["background9"] = pygame.mixer.Sound(os.path.join(musicPath, "lowkey1.wav"))
    result["backgroundA"] = pygame.mixer.Sound(os.path.join(musicPath, "upbeat1.wav"))
    result["backgroundB"] = pygame.mixer.Sound(os.path.join(musicPath, "whee1.wav"))
    
    for sound in result.values():
        sound.set_volume(0.3)
    
    return result
    
def playSound(soundName, volume = 1):
    global sounds, backgroundplayer
    # Get all the sounds with the name beginning in "soundName"
    choices = []
    for key in sounds.keys():
        if key[:-1] == soundName:
            choices.append(sounds[key])
    
    if volume < 0:
        volume = 0
    if not volume == 1:
        print("volume" + str(volume) )
    
    # dang python you sexy. Choose a random sound to play.
    soundToPlay = random.choice(choices)
    soundToPlay.set_volume(0.3 * volume)
    if soundName == "background":
        backgroundPlayer.play(soundToPlay)
    else:
        soundToPlay.play(loops=0, maxtime=0, fade_ms=0)
    
def pauseBackground():
    global backgroundPlayer
    backgroundPlayer.pause()
    
def resumeBackground():
    global backgroundPlayer
    backgroundPlayer.unpause()
  
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
            
            # Figure out how far away it is
            explosDistance = abs(blowUp[0].body.position.x - arena.camera.centerX_in_meters)
            
            # Play a splosion sound w/ an appropriate volume
            playSound("boom", (1 - explosDistance / 50) * 0.5)
            
            for shape in arena.shapes + [arena.player1.shapes[0], arena.player2.shapes[0]]:
                # See how far everyone is from the 'splosion
                distResult = b2Distance(shapeA = shape.fixtures[0].shape, shapeB = blowUp[0].shape, transformA = shape.transform, transformB = blowUp[0].body.transform)
                pointA, pointB, distance, dummy = distResult
                
                # mass > 0 implies it's not a "Static" object
                if distance < 6 and shape.massData.mass > 0.1 and shape.userData != "particle":
                    xComp = int(random.random() * -5000 + 2500)
                    yComp = int(random.random() * -5000 + 2500)
                    
                    shape.linearVelocity.x = xComp
                    shape.linearVelocity.y = yComp
                    shape.angularVelocity = random.random() * 5 + 5
                    shape.awake = True
            
            offsetX, offsetY = arena.camera.getOffset_in_px()
            explos = Explosion(blowUp[0].body.position.x * PPM - offsetX, 37 * PPM - offsetY)
            effects.append(explos)
        
        goalLeft = self.checkContact(contact, "ball")
        if goalLeft is not None:
            # mass > 0 implies it's not a "Static" object
            if goalLeft[1].body.userData is not None or goalLeft[1].userData is not None:
            
                if goalLeft[1].body.userData == "goal left":
                    # Pause background music
                    pauseBackground()
                    # Play the happy score sound
                    playSound("score")
                    arena.score[0] += 1
                    if arena.score[0] >= 7:
                        winGame(1)
                    arena.player1.dead = True
                    arena.player2.dead = True
                    arena.toInit = (STAGE_WIDTH_M / 3, 2000)
                    for shape in arena.shapes:
                        # mass > 0 implies it's not a "Static" object
                        if shape.userData == "crowd member":
                            shape.linearVelocity.y = random.random() * -15 - 5
                if goalLeft[1].body.userData == "goal right":
                    # Pause background music
                    pauseBackground()
                    # Play the happy score sound
                    playSound("score")

                    arena.score[1] += 1
                    if arena.score[1] >= 7:
                        winGame(2)
                    arena.player1.dead = True
                    arena.player2.dead = True
                    arena.toInit = (STAGE_WIDTH_M * 2 / 3, 2000)
                    for shape in arena.shapes:
                        # mass > 0 implies it's not a "Static" object
                        if shape.userData == "crowd member":
                            shape.linearVelocity.y = random.random() * -15 - 5
                
                    
        kick = self.checkContact(contact, "player1")
        if kick is None:
            kick = self.checkContact(contact, "player2")
            
        if kick is not None:
            
            # Punt the ball a little ways kick[1] is ball, kick[0] is player.
            if kick[1].body.userData == "ball":
                if len(kick[0].body.contacts) < 3:
                    kick[1].body.linearVelocity.x = kick[0].body.linearVelocity.x * 10
                    print kick[0].body.linearVelocity.x
                    if abs(kick[0].body.linearVelocity.x) > 10:
                        # Play kick sfx
                        playSound("kick", 2)
                    if arena.world.gravity == (0, 0):
                        kick[1].body.linearVelocity.y = kick[0].body.linearVelocity.y * 10
                    else:
                        kick[1].body.linearVelocity.y -= 100
            if kick[1].body.userData == "player1" or kick[1].body.userData == "player2":
                if kick[0].body.linearVelocity.y>= 25 or kick[1].body.linearVelocity.y >= 25:
                    kick[0].body.linearVelocity.y = -25
                    kick[1].body.linearVelocity.y = -25
                    
                    
                        
            # If the player has touched the ball recently, they're considered
            # "in possession," and have their run speed limited slightly,
            # giving a chance for the chaser to catch up
            arena.gotPossession(kick[0])
