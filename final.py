""" 
LUDUM DARE 27 ENTRY
8/23/2013 - 8/26/2013
THEME: 10 Seconds
BY: Thomas Steinke, Elliot Fiske, Eli Backer

May be uploaded to http://thomassteinke.net
or another domain later, if decided.

Bring it on, LD.

"""

# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                      INITIALIZE CLASSES AND GAME                       |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
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
                distResult = b2Distance(shapeA = shape.fixtures[0].shape, shapeB = blowUp[0].shape, transformA = shape.transform, transformB = blowUp[0].body.transform)
                pointA, pointB, distance, dummy = distResult
                
                # mass > 0 implies it's not a "Static" object
                if distance < 6 and shape.massData.mass > 0.1 and shape.userData != "particle":
                    xComp = int(random.random() * -5000 + 2500)
                    yComp = int(random.random() * -5000 + 2500)
                    print yComp
                    
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
                    arena.score[0] += 1
                    if arena.score[0] >= 5:
                        winGame(1)
                    arena.player1.dead = True
                    arena.player2.dead = True
                    arena.toInit = (STAGE_WIDTH_M / 3, 2000)
                    for shape in arena.shapes:
                        # mass > 0 implies it's not a "Static" object
                        if shape.userData == "crowd member":
                            shape.linearVelocity.y = random.random() * -15 - 5
                if goalLeft[1].body.userData == "goal right":
                    arena.score[1] += 1
                    if arena.score[1] >= 5:
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

BTN_HEIGHT = 81
BTN_WIDTH = 260
# How much room between each button?
BTN_STEP = 100

buttons = [ ["play",0], ["opt",0], ["quit",0]]
states =  ["des",  "sel", "cli" ]

angle = 0
lastButtonClicked = ""
app = gui.Desktop()

def initTitle():
    # Load all the menu buttons
    buttonY = SCREEN_HEIGHT_PX/2 - BTN_HEIGHT/2 - BTN_STEP
    buttonX = SCREEN_WIDTH_PX/2  - BTN_WIDTH/2
    for button in buttons:
        for state in states:
            imageName = button[0] + "-" + state
            images[imageName] = load_image(imageName + ".png")
            images[imageName][0].set_colorkey(pygame.Color("white"))
            # Change imagerect to where the image actually is on screen
            images[imageName][1].left = buttonX
            images[imageName][1].top  = buttonY
        
        buttonY += BTN_STEP
        
    global app
    app = gui.Desktop()
    
            
def titleInput(event):
    # Grab mouse coords
    mousePos = pygame.mouse.get_pos()
        
    global lastButtonClicked
    global gameState
    
    # Is it just a mousemove?
    if event.type == pygame.MOUSEMOTION:
        for i, button in enumerate(buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                # Tell the button to highlight
                buttons[i][1] = 1
            else:
                # Deselect button
                buttons[i][1] = 0
    
    # Is it a new mouseclick?
    if event.type == pygame.MOUSEBUTTONDOWN:
        for i, button in enumerate(buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                lastButtonClicked = button[0]
                buttons[i][1] = 2
                
    # Is it a mouse up?
    if event.type == pygame.MOUSEBUTTONUP:
        for i, button in enumerate(buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                buttons[i][1] = 1
                if lastButtonClicked == button[0]:
                    # Positive match! Rejoice!
                    if button[0] == "play":
                        global arena, prepare            # Arena for minigame
                        initCharSelect()
                        gameState = "CharSelect"
                    elif button[0] == "opt":
                        makeOptions()
                    elif button[0] == "quit":
                        sys.exit()
                else:
                    # Make sure we wipe the last button clicked
                    lastButtonClicked = ""
    
def drawTitle(screen):
    # TODO: put an image here?
    screen.fill(pygame.Color("white"))
    
    for button in buttons:
        imageName = button[0] + "-" + states[button[1]]
        screen.blit(images[imageName][0], images[imageName][1])
        
# Make the Options menu out of pgu
def endItAll(what):
    sys.exit()
    
def makeOptions():
    app = gui.Desktop()
    # make sure the game closes when you hit X
    app.connect(gui.QUIT,endItAll,None)
    c = gui.Table()
    
    c.tr()
    c.td(gui.Label("MUSIC VOLUME:"))
    
    c.tr()
    c.td(gui.HSlider(value=23,min=0,max=100,size=20,width=120),colspan=3)
    
    c.tr()
    c.td(gui.Label("SOUND VOLUME:"))
    
    c.tr()
    c.td(gui.HSlider(value=23,min=0,max=100,size=20,width=120),colspan=3)
    
    c.tr()
    c.td(gui.Label("SCREEN RESOLUTION"))
    
    c.tr()
    btn = gui.Button("BACK")
    btn.connect(gui.CLICK, app.quit)
    c.td(btn,colspan=3)
    app.run(c)
    

class BombDrop():
    done = False
    bombCooldown = 20
    bombs = []
    def draw(self, screen):
        # Draw the bombas
        for i,bomb in enumerate(self.bombs):
            rotAngle = bomb.body.angle
            offsetX, offsetY = arena.camera.getOffset_in_px()
            verts = vertices_with_offset(bomb, offsetX, offsetY)
            # The "vertices" method will return a rotated square of vertices.
            # As it turns out, if we grab the leftmost, topmost, rightmost and
            # bottommost values from these vertices, we end up with the right
            # bounding box for pygame to draw the image. Huh.
            xvals = [ x[0] for x in verts ]
            yvals = [ y[1] for y in verts ]
            left = min(xvals)
            right = max(xvals)
            top = min(yvals)
            bottom = max(yvals)
            finalRect = pygame.Rect(left, top, (right - left), (bottom - top))
            imgRot = pygame.Surface.convert_alpha(pygame.transform.rotate(images["bomb"][0], rotAngle))
            screen.blit(imgRot, finalRect)
            if bomb.body.userData == "kill me":
                bomb.body.DestroyFixture(bomb)
                del self.bombs[i]
            
    def update(self):
        # Iterate the cooldown on bombs. If it's been long enough, drop another one!
        self.bombCooldown -= 1
        if self.bombCooldown <= 0:
            self.bombCooldown = 20
            # drop da bomb
            # Choose a random spot between 0 -> Stage Width meters
            bombX = int(random.random() * STAGE_WIDTH_M)
            # Choose a random spot in the upper half of the map to drop the bomb
            bombY = int(random.random() * SCREEN_HEIGHT_M/2 + SCREEN_HEIGHT_M)
            
            newBomb = arena.world.CreateDynamicBody(
                userData = "bomb",
                position = (bombX, 10),
                fixtures = b2FixtureDef(density = 5.0, shape = b2PolygonShape(box = (1,1)),
                    isSensor = True))
                    
            # Start with a li'l spin
            newBomb.angularVelocity = 2 - random.random() * 4
            
            self.bombs.append(newBomb.fixtures[0])
            
    def finish(self):
        self.done = True
        bombs = []

class Explosion:
    size = 5
    alpha = 255
    x = 0
    y = 0
    done = False
    def __init__(self, ex, ey):
        self.x, self.y = int(ex), int(ey)
    def draw(self, screen):
        # Transparency sucks. Make a new surface then draw the splosion onto it,
        # then draw that new surface on to the old surface.
        s = pygame.Surface((SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX), HWSURFACE)
        s.set_alpha(self.alpha)
        s.set_colorkey(pygame.Color(0, 0, 0))
        pygame.draw.circle(s, pygame.Color(237, 211, 17),
                            (self.x, self.y), self.size)
        
        screen.blit(s, (0,0))
    def update(self):
        self.size += 6
        self.alpha -= 15
        if self.alpha <= 0:
            self.done = True
            
# Back is used for the scrolling image...
class Back(pygame.sprite.Sprite):
	def __init__(self,name):
		pygame.sprite.Sprite.__init__(self)
		self.tendency = 0
		self.image, self.rect = load_image(name+'.jpg')
def changeArena(arenaNum):
    global currentArena        # Midpoint
    global camera
    
    currentArena = arenaNum
    camera.panCam(arenaNum)
    camera.delay = 200

char1 = "Lars"
char2 = "Buster"
class Arena():
    def __init__(self):
        self.timeRemaining = 10000 # 10 seconds
        self.drawRed = 0
        self.bignum = 10
        self.shapes = []
        self.crowd = []
        
        self.player1possession = 0
        self.player2possession = 0
        
        self.modifications = []
    
        # Initialize effects queue
        self.effects = []
    
        # Init physics "world", defining gravity. doSleep means that if an object
        # comes to rest, it can "sleep" and be ignored by the physics engine for a bit.
        self.world = b2World(gravity=(0, 25), doSleep = False)
        
        # Initialize the contact handler
        self.world.contactListener = ContactHandler()
        
        self.initWalls()
        self.ball = None
        self.startGame(STAGE_WIDTH_M / 2)
        
        self.camera = Camera(STAGE_WIDTH_M / 2)
        
        self.score = [0,0]
        
        self.toInit = False
        self.pauseTime = 0
        
        self.createCrowd(2, 24)
        self.createCrowd(227, 248)
        
        #self.bombDrop()
        #self.changeBall()
        #self.nogravity()
        #self.slowmo()
  
    def startGame(self, middle_x, delay=0):
        global char1, char2
        if delay > 0:
            self.toInit = (middle_x, delay)
            return
            
        self.toInit = False
        self.pauseTime = delay
        
        if hasattr(self,'player2'):
            self.player1.materialize(middle_x - SCREEN_WIDTH_M / 4, self, 2)
            self.player2.materialize(middle_x + SCREEN_WIDTH_M / 4, self, 1)
        else:
            if char1 == "Lars":
                self.player1 = Lars(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "Buster":
                self.player1 = Buster(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "SmithWickers":
                self.player1 = SmithWickers(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "Pate":
                self.player1 = Pate(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "EricStrohm":
                self.player1 = EricStrohm(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            else: # char1 == "Ted":
                self.player1 = Ted(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
                
            if char2 == "Lars":
                self.player2 = Lars(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "Buster":
                self.player2 = Buster(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "SmithWickers":
                self.player2 = SmithWickers(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "Ted":
                self.player2 = Ted(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "EricStrohm":
                self.player2 = EricStrohm(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            else: # char2 == "Pate":
                self.player2 = Pate(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
        
        if self.ball is not None: self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = (middle_x,28),
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1.3),
                density=1,
                restitution=0.5,
                friction = 50),
            userData="ball")
            
        self.ball.color = pygame.color.Color(128,128,128)
        self.shapes.append(self.ball)
        
        self.textAlpha = 255
        self.dispText = "Go!"
        
    def createCrowd(self, minx, maxx):
        numCrowd = int(math.ceil(random.random() * 10) + 10)
        width = maxx - minx
        
        for i in range(numCrowd):
            member = CrowdMember(0, minx + random.random() * width, (int(random.random()*255),int(random.random()*255),int(random.random()*255)), self)
            self.crowd.append(member)
            self.shapes.append(member.shapes[0])
        
    def initWalls(self):
        ground = self.world.CreateStaticBody(
            position = (0, 37.5),
            shapes = b2PolygonShape(box = (STAGE_WIDTH_M,1)),
            userData = "ground"
        )
        ground.color = pygame.color.Color(0,128,0)
        self.shapes.append(ground)
        
        ceiling = self.world.CreateStaticBody(
            position = (0, -1),
            shapes = b2PolygonShape(box = (STAGE_WIDTH_M,1)),
            userData = "ceiling"
        )
        self.shapes.append(ceiling)
        
        leftWall = self.world.CreateStaticBody(
            position = (25, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        #self.shapes.append(leftWall)
        
        rightWall = self.world.CreateStaticBody(
            position = (225, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
        #self.shapes.append(rightWall)
        
        leftWall = self.world.CreateStaticBody(
            position = (0, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        #self.shapes.append(leftWall)
        
        rightWall = self.world.CreateStaticBody(
            position = (250, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
        
        goal_left = self.world.CreateStaticBody(
            position = (223, 37),
            shapes = b2PolygonShape(box = (2,8))
        )
        goal_left.fixtures[0].sensor = True
        goal_left.userData = "goal left"
        self.shapes.append(goal_left)
        
        goal_right = self.world.CreateStaticBody(
            position = (29, 37),
            shapes = b2PolygonShape(box = (2,8))
        )
        goal_right.fixtures[0].sensor = True
        goal_right.userData = "goal right"
        self.shapes.append(goal_right)
        
    # Detects if the player is off camera and draws an arrow to them
    def playerOffCamera(self):
        # A player is off camera if all 4 of their vertices don't intersect with the screen.
        SCREEN_RECT.left = self.camera.centerX_in_meters * PPM - SCREEN_WIDTH_PX / 2
        offsetX, offsetY = self.camera.getOffset_in_px()
        verts = vertices(self.player1.shapes[0].fixtures[0])
        inside = False
        for vert in verts:
            inside = inside or SCREEN_RECT.collidepoint( (vert.x, vert.y) )
            
        if not inside:
            self.drawArrow(self.player1)
            
        verts = vertices(self.player2.shapes[0].fixtures[0])
        inside = False
        for vert in verts:
            inside = inside or SCREEN_RECT.collidepoint( (vert.x, vert.y) )
                
        if not inside:
            self.drawArrow(self.player2)
            
    # Draw an arrow to the lost, lonely player.        
    def drawArrow(self, player):
        position = player.shapes[0].position
        arrowX, arrowY = 0, 0
        
        # Identify the x and y to draw the arrow in
        arrowY = position.y * PPM - 70
        if position.x < self.camera.centerX_in_meters:
            arrowX = 5
            arrowImg = pygame.transform.flip(images["red arrow"][0], True, False)
        else:
            arrowImg = images["red arrow"][0]
            arrowX = SCREEN_WIDTH_PX - (5 + images["red arrow"][1].width)
        
        screen.blit(arrowImg, (arrowX, arrowY))
        
    # Lets the arena know that a player has touched the ball recently
    def gotPossession(self, playerFixture):
        if playerFixture.body.userData == "player1":
            self.player1possession = 50
        elif playerFixture.body.userData == "player2":
            self.player2possession = 50
        else:
            print("wat")
        
    def update(self, dt):
        self.camera.update(self.ball)
        
        if self.toInit is not False:
            self.startGame(self.toInit[0], self.toInit[1] - dt)
                        
            # Update a "tick" in physics land
            self.world.Step(TIME_STEP*2, 10, 10)
            
            # Reset forces for the next frame
            self.world.ClearForces()
            
            if(self.player1.dead):
                self.player1.dead = False
                self.player1.destroy()
            if(self.player2.dead):
                self.player2.dead = False
                self.player2.destroy()
            return
    
        self.timeRemaining -= dt
        oldbignum = self.bignum
        self.bignum = math.trunc(self.timeRemaining / 1000)
        if self.bignum != oldbignum and self.bignum < 4: self.drawRed = 128
        if(self.timeRemaining <= 0):
            self.randomEvent()
            self.timeRemaining = 10000
            
        self.player1.update(self.world.gravity == b2Vec2(0,0))
        self.player2.update(self.world.gravity == b2Vec2(0,0))
        for member in self.crowd:
            member.update(dt, self.world.gravity == b2Vec2(0,0))
        
        # Murder things that need murdering
        for i, shape in enumerate(self.shapes):
            if shape.userData == "kill me":
                shape.DestroyFixture(shape)
                del self.shapes[i]
        
        for i, ef in enumerate(self.effects):
            ef.update()
            ef.draw(screen)
            if ef.done:
                del self.effects[i]
        
        self.ball.linearVelocity.x *= BALL_FRICTION
        
        # Check the "possession" status of each character and change friction as necessary
        #if self.player1possession > 0 and self.player1possession > self.player2possession:
        #    self.player1.shapes[0].friction = 10
        #    print("fraction", self.player1.shapes[0].friction)                    
        #else:                                    
        #    self.player1.shapes[0].friction = 0.3
        #                                         
        #if self.player2possession > 0 and self.player2possession > self.player1possession:
        #    self.player1.shapes[0].friction = 10
        #else: 
        #    self.player2.shapes[0].friction = 0.3
        
        # Decrement the possession timers
        self.player1possession -= 1
        if self.player1possession < 0: self.player1possession = 0
        self.player2possession -= 1
        if self.player2possession < 0: self.player2possession = 0
        
        # Update a "tick" in physics land
        self.world.Step(TIME_STEP*2, 10, 10)
        
        # Reset forces for the next frame
        self.world.ClearForces()
                
    def draw(self, screen, showTimer = True):
        
        self.camera.draw(screen)
        
        if showTimer:
            self.drawTimer(screen)
        
        offsetX, offsetY = self.camera.getOffset_in_px()
        self.player1.draw(screen, offsetX, offsetY)
        self.player2.draw(screen, offsetX, offsetY)
        for member in self.crowd: pass
            #DrawPolygon(vertices_with_offset(member.fixtures[0], offsetX, offsetY), (0,0,0), member.color)
        
        for shape in self.shapes:
            if isinstance(shape.fixtures[0].shape, b2CircleShape):
                pos = (int(shape.position.x * PPM - offsetX), int(shape.position.y * PPM + offsetY))
                if shape.userData == "ball":
                    DrawCircle(pos, shape.fixtures[0].shape.radius, shape.color)
                else:
                    DrawCircle(pos, shape.fixtures[0].shape.radius, (0,0,0))
            elif shape.userData is not None:
                if shape.userData == "goal left" or shape.userData == "goal right":
                    DrawImage(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), shape.userData)
                else:
                    if hasattr(shape, "color"):
                        DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0), shape.color)
                    else:
                        DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0))
            else:
                if hasattr(shape, "color"):
                    DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0), shape.color)
                else:
                    DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0))
            
        # Draw arrows if the player is off screen
        self.playerOffCamera()
    
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), False, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), False, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 2
        
        if(self.bignum == 10): screen.blit(text, (SCREEN_WIDTH_PX / 2 - 1100,0))
        else: screen.blit(text, (SCREEN_WIDTH_PX / 2 - 70,0))
        screen.blit(text_sm, (SCREEN_WIDTH_PX / 2,0))
        
        text_l = time_font_lg.render(str(self.score[0]), False, (0,0,0))
        text_r = time_font_lg.render(str(self.score[1]), False, (0,0,0))
        screen.blit(text_l, (0,0))
        screen.blit(text_r, (SCREEN_WIDTH_PX - 60,0))
        
        if self.textAlpha > 0:
            self.textAlpha -= 2.5
            
            text = time_font_giant.render(self.dispText, False, (0, 0, 0), (255,255,255, 0))
            if self.dispText == "SLOWWMOOOOO!":
                surface = pygame.Surface((text.get_width()+30, text.get_height()))
                surface.blit(text, (30,0))
                text = time_font_giant.render(self.dispText, False, (0, 0, 0), (255,255,255, 0))
                surface.blit(text, (0,0))
                surface.set_colorkey((255,255,255))
                surface.set_alpha(self.textAlpha)
                screen.blit(surface, (SCREEN_WIDTH_PX / 2 - text.get_width()/2,180))
            else:
                surface = pygame.Surface((text.get_width(), text.get_height()))
                surface.blit(text, (0,0))
                surface.set_colorkey((255,255,255))
                surface.set_alpha(self.textAlpha)
                screen.blit(surface, (SCREEN_WIDTH_PX / 2 - text.get_width()/2,180))

    def doAction(self, event):
        if event.key is K_a:
            self.player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            self.player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            self.player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            self.player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP:
            self.player2.input["up"] = (event.type is pygame.KEYDOWN)
            self.player2.jump(self.world.gravity)
        if event.key == K_DOWN:
            self.player2.input["down"] = (event.type is pygame.KEYDOWN)
            self.player2.dive()
        if event.key is K_w:
            self.player1.input["up"] = (event.type is pygame.KEYDOWN)
            self.player1.jump(self.world.gravity)
        if event.key is K_s:
            self.player1.input["down"] = (event.type is pygame.KEYDOWN)
            self.player1.dive()
            
    def changeBall(self):
        print "Changeball triggered"
        self.shapes.remove(self.ball)
        position = self.ball.position
        self.world.DestroyBody(self.ball)
        self.ball = self.world.CreateDynamicBody(position = position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(vertices=[(-0.33,1  ),
                                                (-1  ,0.33),
                                                (-1  ,-0.33),
                                                (-0.33 ,-1 ),
                                                (0.33 ,-1 ),
                                                (1   ,-0.33),
                                                (1   ,0.33),
                                                (-0.33 ,1  )]),
                density=10,
                restitution=0.5,
                friction = 50),
            userData="ball")
        self.ball.color = pygame.color.Color(128,128,128)
        self.shapes.append(self.ball)
        
        self.textAlpha = 255
        self.dispText = "ROCK BALLSTER!"
    
    def changeBall_revert(self):
        print "Changeball reverted"
        self.shapes.remove(self.ball)
        position = self.ball.position
        self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = position,
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1.3),
                density=1,
                restitution=0.5,
                friction = 50),
            userData="ball")
            
        self.ball.color = pygame.color.Color(128,128,128)
        self.shapes.append(self.ball)
     
    def slowmo(self):
        print "slow mo!"
        global TIME_STEP
        TIME_STEP /= 4
        
        self.textAlpha = 255
        self.dispText = "SLOWWMOOOOO!"
     
    def slowmo_revert(self):
        print "slow mo reverted"
        global TIME_STEP
        TIME_STEP *= 4
        
    def giantMode(self):
        self.player1.toExpand = True
        self.player2.toExpand = True
    
    def giantMode_revert(self):
        self.player1.toNormalSize = True
        self.player2.toNormalSize = True
        
    def cleanUp(self):
        self.crowd = []
        while len(self.shapes) > 0:
            shape = self.shapes[0]
            self.world.DestroyBody(shape)
            self.shapes.remove(shape)
        
    def bombDrop(self):
        print "bomb droppin time!"
        bombs = BombDrop()
        effects.append(bombs)
        
        self.textAlpha = 255
        self.dispText = "Bombs!"
        
    def bombDrop_revert(self):
        print "bomb droppin reversion!"
        # Find the bomb drop and PUT A STOP TO THE MADNESS
        for ef in effects:
            if ef.__class__.__name__ == "BombDrop":
                ef.finish()
        
    def randomEvent(self):
        randomEvents = [ [self.bombDrop, self.bombDrop_revert],
                         [self.changeBall, self.changeBall_revert],
                         [self.giantMode, self.giantMode_revert],
                         [self.slowmo, self.slowmo_revert]]
                         
        while len(self.modifications) > 0:
            mod = self.modifications[0]
            mod[1]()
            del self.modifications[0]
            
        event = math.floor(random.random() * len(randomEvents))
        
        # Grab the function from the list of events and run it
        mod = randomEvents[int(event)]
        mod[0]()
        self.modifications.append(mod)
            
            
class PrepareForBattle(Arena):
    def __init__(self):
        self.timeRemaining = 3000
        self.bignum = 3
        
    def draw(self, screen):
        arena.draw(screen, False)
        
        self.drawTimer(screen)
        
        text = (time_font_lg.render("PREPARE", False, (0, 0, 0)), time_font_lg.render("YOURSELF", False, (0, 0, 0)))
        screen.blit(text[0], (SCREEN_WIDTH_PX / 2 - 210,180))
        screen.blit(text[1], (SCREEN_WIDTH_PX / 2 - 220,260))
        
        
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), False, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), False, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 2
        
        screen.blit(text, (SCREEN_WIDTH_PX / 2 - 70,0))
        screen.blit(text_sm, (SCREEN_WIDTH_PX / 2,0))
        
    def update(self, dt):
        self.timeRemaining -= dt
        oldbignum = self.bignum
        self.bignum = math.trunc(self.timeRemaining / 1000)
        if self.bignum != oldbignum and self.bignum < 4: self.drawRed = 128
        if(self.timeRemaining <= 0):
            global arena, gameState
            gameState = "Arena"

    def doAction(self, event):
        if event.key is K_a:
            arena.player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            arena.player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            arena.player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            arena.player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP:
            arena.player2.input["up"] = (event.type is pygame.KEYDOWN)
        if event.key == K_DOWN:
            arena.player2.input["down"] = (event.type is pygame.KEYDOWN)
        if event.key is K_w:
            arena.player1.input["up"] = (event.type is pygame.KEYDOWN)
        if event.key is K_s:
            arena.player1.input["down"] = (event.type is pygame.KEYDOWN)


def DrawPolygon(vertices, color = (0,0,0), color_2 = None):
    """ Draw a wireframe polygon given the screen vertices with the specified color."""
    if not vertices:
        print("no vertices, brotha")
        return
        

    if len(vertices) == 2:
        pygame.draw.aaline(screen, color, vertices[0], vertices)
    else:
        if color_2 is not None:
            pygame.draw.polygon(screen, color_2, vertices, 0)
        pygame.draw.polygon(screen, color, vertices, 2)

def DrawCircle(center, radius, color = (0,0,0), color_2 = (0,0,0)):
    """ Draw a wireframe polygon given the screen vertices with the specified color."""
    if not center or not radius:
        return
        
    pygame.draw.circle(screen, color, center, int(radius*PPM))
    pygame.draw.circle(screen, color_2, center, int(radius*PPM), 2)
            
def DrawImage(vertices, userData):
    screen.blit(images[userData][0], (vertices[0], vertices[1]))
           
class Camera():
    def __init__(self, centerX_in_meters):
        self.background = Back("background")
        self.centerX_in_meters = centerX_in_meters
        self.centerX_in_px = centerX_in_meters * PPM
        
        self.dx = 0
    
    def getOffset_in_meters(self):
        offsetX_in_meters = self.centerX_in_meters - SCREEN_WIDTH_M / 2
        offsetY_in_meters = 0
        return offsetX_in_meters, offsetY_in_meters
        
    def getOffset_in_px(self):
        offsetX_in_meters, offsetY_in_meters = self.getOffset_in_meters()
        return offsetX_in_meters * PPM, offsetY_in_meters * PPM
        
    def draw(self, screen):
        offsetX_in_meters = self.centerX_in_meters - SCREEN_WIDTH_M / 2
        screen.blit(self.background.image, (-1 * offsetX_in_meters * PPM - 200, 0))
        
    def update(self, ball):
        if abs(ball.position.x - self.centerX_in_meters) > CAMERA_PILLOW_SPACE_M:
            if abs(self.dx) + CAMERA_SPEEDUP_SPEED <= CAMERA_MAX_PAN_SPEED_PX:
                if ball.position.x - self.centerX_in_meters > 0:
                    self.dx += CAMERA_SPEEDUP_SPEED
                else:
                    self.dx -= CAMERA_SPEEDUP_SPEED
            
        if abs(ball.position.x - self.centerX_in_meters) <= CAMERA_MAX_PAN_SPEED_M:
            self.dx = (ball.position.x - self.centerX_in_meters) * PPM
            
        self.centerX_in_px += self.dx
        self.centerX_in_meters = self.centerX_in_px / PPM
        
        if self.centerX_in_meters < SCREEN_WIDTH_M / 2:
            self.dx = 0
            self.centerX_in_meters = SCREEN_WIDTH_M / 2
            self.centerX_in_px = self.centerX_in_meters * PPM
        if self.centerX_in_meters > STAGE_WIDTH_M - SCREEN_WIDTH_M / 2:
            self.dx = 0
            self.centerX_in_meters = STAGE_WIDTH_M - SCREEN_WIDTH_M / 2
            self.centerX_in_px = self.centerX_in_meters * PPM
            
    def stop(self): pass
def winGame(winner):
    global gameWinner, gameLoser, gameState
    global gameWinnerColor, gameLoserColor
    gameState = "GameOver"
    if winner == 1:
        gameWinner = char1
        gameWinnerColor = char1color
        gameLoser = char2
        gameLoserColor = char2color
    else:
        gameWinner = char2
        gameWinnerColor = char2color
        gameLoser = char1
        gameLoserColor = char1color
    
    #arena.cleanUp()
    initGameOver()

game_over_buttons = [ ["menu",0], ["quit",0]]

def initGameOver():
    # Load all the menu buttons
    buttonY = SCREEN_HEIGHT_PX/2 - BTN_HEIGHT/2 - BTN_STEP
    buttonX = SCREEN_WIDTH_PX/2  - BTN_WIDTH/2
    for button in game_over_buttons:
        for state in states:
            imageName = button[0] + "-" + state
            images[imageName] = load_image(imageName + ".png")
            images[imageName][0].set_colorkey(pygame.Color("white"))
            # Change imagerect to where the image actually is on screen
            images[imageName][1].left = buttonX
            images[imageName][1].top  = buttonY
        
        buttonY += BTN_STEP
            
def gameOverInput(event):
    # Grab mouse coords
    mousePos = pygame.mouse.get_pos()
        
    global lastButtonClicked
    global gameState
    
    # Is it just a mousemove?
    if event.type == pygame.MOUSEMOTION:
        for i, button in enumerate(game_over_buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                # Tell the button to highlight
                game_over_buttons[i][1] = 1
            else:
                # Deselect button
                game_over_buttons[i][1] = 0
    
    # Is it a new mouseclick?
    if event.type == pygame.MOUSEBUTTONDOWN:
        for i, button in enumerate(game_over_buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                lastButtonClicked = button[0]
                game_over_buttons[i][1] = 2
                
    # Is it a mouse up?
    if event.type == pygame.MOUSEBUTTONUP:
        for i, button in enumerate(game_over_buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                game_over_buttons[i][1] = 1
                if lastButtonClicked == button[0]:
                    # Positive match! Rejoice!
                    if button[0] == "menu":
                        gameState = "Title"
                    elif button[0] == "quit":
                        sys.exit()
                else:
                    # Make sure we wipe the last button clicked
                    lastButtonClicked = ""
    
def drawGameOver(screen):
    screen.fill(gameWinnerColor, (0,0,SCREEN_WIDTH_PX/2,SCREEN_HEIGHT_PX))
    screen.fill(gameLoserColor, (SCREEN_WIDTH_PX/2,0,SCREEN_WIDTH_PX/2,SCREEN_HEIGHT_PX))
    # TODO: put an image here?
    screen.blit(images[gameLoser+"_loser"][0], ((SCREEN_WIDTH_PX/2 - 400),0))
    screen.blit(images[gameWinner+"_winner"][0], ((SCREEN_WIDTH_PX/2 - 400),0))
        
    for button in game_over_buttons:
        imageName = button[0] + "-" + states[button[1]]
        screen.blit(images[imageName][0], images[imageName][1])

class Player(pygame.sprite.Sprite):
        
    def __init__(self, direction, start_x, color, color_2, arena, playerNum):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.color = color
        self.color_2 = color_2
        self.shapes = []
        self.arena = arena
        
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
        
        self.toExpand = False
        self.toNormalSize = False
        
        self.speed = 10
        self.airspeed = 14
        self.moving = None
        
        self.dead = False
        self.materialize(start_x, arena, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes(arena)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction=CHAR_FRICTION,
                restitution=0
            ),
            userData = "player"+str(playerNum)
        )
        block.color = self.color_2
        self.shapes.append(block)
        
        w = self.size[0]
        h = self.size[1]
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1*w-.6,-1*h-.1),(w+.6,-1*h-.1),(w+.6,h+.1),(-1*w-.6,h+.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False
        self.dx = 0
        
    def draw(self, screen, offsetX, offsetY):
        for shape in self.shapes:
            DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0), shape.color)
    
    def destroy(self):
        destructionShapes = []
        if len(self.shapes) > 1:
            for i in range(1,len(self.shapes)):
                # Grab the old vertices from the shape
                olds = self.shapes[i].fixtures[0].shape.vertices
                # Convert them (with magic) using the body.transform thing
                result = [(self.shapes[i].transform*v) for v in olds]
                for v in result:
                    body = arena.world.CreateDynamicBody(position = v, userData = "particle")
                    shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                    body.color = self.shapes[i].color
                    body.linearVelocity.y = -15
                    body.linearVelocity.x = random.random() * 6 - 3
                    destructionShapes.append(body)
                
        # Grab the old vertices from the shape
        olds = self.shapes[0].fixtures[0].shape.vertices
        for i in range(20):
            # Convert them (with magic) using the body.transform thing
            result = [(self.shapes[0].transform*v) for v in olds]
            for v in result:
                body = arena.world.CreateDynamicBody(position = (v.x + random.random()*4 - 2, v.y + random.random()*4-2), userData = "particle")
                shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                body.color = self.shapes[0].color
                body.linearVelocity.y = -15
                body.linearVelocity.x = random.random() * 16 - 8
                destructionShapes.append(body)
                
        self.clearShapes()
        self.shapes = destructionShapes
                
    def create(self, color):
        self.clearShapes(arena, color)
    
        body = arena.world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 34))
        box = body.CreatePolygonFixture(box = (1,2), density = CHAR_DENSITY, friction = 0.3)
        self.shapes.append(body)
         
    def clearShapes(self, a = None):
        if a is not None:
            for shape in self.shapes:
                a.world.DestroyBody(shape)
        else:
            for shape in self.shapes:
                arena.world.DestroyBody(shape)
        self.shapes = []
      
    def update(self, nogravity = False):
        if self.toExpand:
            self.expand()
            self.toExpand = False
        if self.toNormalSize:
            self.normal()
            self.toNormalSize = False
        if(self.dead):
            self.destroy()
            return
            
        self.shapes[0].awake = True
        if nogravity:
            if self.input["up"]:
                self.shapes[0].linearVelocity.y -= 3
            if self.input["down"]:
                self.shapes[0].linearVelocity.y += 3
            if self.input["left"]:
                self.shapes[0].linearVelocity.x -= 4
            if self.input["right"]:
                self.shapes[0].linearVelocity.x += 4
                
            if self.shapes[0].linearVelocity.y > 20: self.shapes[0].linearVelocity.y = 20
            if self.shapes[0].linearVelocity.y < -20: self.shapes[0].linearVelocity.y = -20
            if self.shapes[0].linearVelocity.x > 20: self.shapes[0].linearVelocity.x = 20
            if self.shapes[0].linearVelocity.x < -20: self.shapes[0].linearVelocity.x = -20
        else:
            if self.moving is not None: 
                if self.moving == "l": 
                    self.shapes[0].linearVelocity.x += self.speed
                if self.moving == "r":
                    self.shapes[0].linearVelocity.x -= self.speed
            
            if len(self.shapes[0].contacts) > 0: maxspeed = self.speed
            else: maxspeed = self.speed + self.airspeed
            if self.input["left"]:
                self.shapes[0].linearVelocity.x -= maxspeed
            if self.input["right"]:
                self.shapes[0].linearVelocity.x += maxspeed
                
            if self.shapes[0].linearVelocity.x > 20: self.shapes[0].linearVelocity.x = 20
            if self.shapes[0].linearVelocity.x < -20: self.shapes[0].linearVelocity.x = -20
            
    def jump(self):
        if len(self.shapes[0].contacts) > 0:
            self.shapes[0].linearVelocity.y = -15
            self.shapes[0].angularVelocity = 5.4
                
    def dive(self):
        if self.shapes[0].linearVelocity.x > 0:
            dir = "l"
        else:
            dir = "r"
            
        if len(self.shapes[0].contacts) == 0:
            self.shapes[0].linearVelocity.y = 25
            self.shapes[0].linearVelocity.x *= 2
            if dir == "l":
                if self.shapes[0].angle < math.pi / 4:
                    self.shapes[0].angularVelocity = 0.5
                else:
                    self.shapes[0].angularVelocity = -0.5
            if dir == "r":
                if self.shapes[0].angle < - math.pi / 4:
                    self.shapes[0].angularVelocity = 0.5
                else:
                    self.shapes[0].angularVelocity = -0.5
            
    def jump(self, gravity):
        if gravity == b2Vec2(0,0): pass
        else:
            if len(self.shapes[0].contacts) > 0:
                self.shapes[0].linearVelocity.y = -20 * gravity[1] / 25
                self.shapes[0].angularVelocity = -5.4 * self.direction
                
    def makeNewBlock(self, size):
        i = 0
        shape = self.shapes[i]
        s = shape.fixtures[0].shape
        
        newshape = arena.world.CreateDynamicBody(
            position = shape.position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = size),
                density=shape.fixtures[0].density,
                friction = shape.fixtures[0].friction,
                restitution=shape.fixtures[0].restitution
            ),
            userData = shape.userData
        )
        newshape.color = shape.color
        arena.world.DestroyBody(self.shapes[i])
        self.shapes[i] = newshape
    
    def expand(self):
        self.makeNewBlock(self.large)
    
    def normal(self):
        self.makeNewBlock(self.size)
    
    def shrink(self):
        self.makeNewBlock(self.small)

class Lars(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
        
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 255, 0), arena, playerNum)

class Pate(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        self.small = (0.4,1)
        self.size = (0.8,2.3)
        self.large = (1.6,4.2)
        
        Player.__init__(self, direction, start_x, (0, 0, 0), (0, 255, 255), arena, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes(arena)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction = 10000,
                restitution=0),
            userData = "player"+str(playerNum)
        )
        block.color = self.color_2
        self.shapes.append(block)
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False

class Buster(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        Player.__init__(self, direction, start_x, (0, 0, 0), (153, 255, 0), arena, playerNum)
        
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
        
        self.materialize(start_x, arena, playerNum)

class EricStrohm(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        Player.__init__(self, direction, start_x, (0, 0, 0), (30, 30, 30), arena, playerNum)
        
        self.speed = 12
        self.airspeed = 20

class Ted(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 0), arena, playerNum)
        
        self.small = (0.7,0.7)
        self.size = (1.3,1.3)
        self.large = (2.5,2.5)
        self.clearShapes(arena)        
        
        self.materialize(start_x, arena, playerNum)

class SmithWickers(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        
        self.alt_color =  pygame.color.Color(255, 102, 0)
        self.alt_color_2 =  pygame.color.Color(102, 51, 102)
        
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 255), arena, playerNum)
        
        self.small = (0.3,0.8)
        self.size = (0.75,1.7)
        self.large = (1.5,3.5)
        
        self.materialize(start_x, arena, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes(arena)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction = CHAR_FRICTION,
                restitution=0),
            userData = "player"+str(playerNum)
        )
        block.color = self.alt_color
        self.shapes.append(block)
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
            
        block2 = arena.world.CreateDynamicBody(
            position = (start_x - 3, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction=CHAR_FRICTION,
                restitution=0),
            userData = "player"+str(playerNum)
        )
        block2.color = self.alt_color_2
        self.shapes.append(block2)
        
        arena.world.CreateDistanceJoint(bodyA = block, bodyB = block2, anchorA = block.worldCenter, anchorB = block2.worldCenter, collideConnected = True)
        
        self.dead = False
                
    def expand(self):
        shape = self.shapes[0]
        s = shape.fixtures[0].shape
        block = arena.world.CreateDynamicBody(
            position = shape.position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.large),
                density=shape.fixtures[0].density,
                friction = shape.fixtures[0].friction,
                restitution=shape.fixtures[0].restitution
            ),
            userData = shape.userData
        )
        block.color = self.alt_color
        arena.world.DestroyBody(self.shapes[0])
        self.shapes[0] = block
        
        oldpos = shape.position
        shape2 = self.shapes[1]
        newpos = shape2.position
        s = shape2.fixtures[0].shape
        block2 = arena.world.CreateDynamicBody(
            position = (newpos.x + (newpos.x - oldpos.x) * 4/3, newpos.y + (newpos.y - oldpos.y) * 4/3),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.large),
                density=shape2.fixtures[0].density,
                friction = shape2.fixtures[0].friction,
                restitution=shape2.fixtures[0].restitution
            ),
            userData = shape2.userData
        )
        block2.color = self.alt_color_2
        arena.world.DestroyBody(self.shapes[1])
        self.shapes[1] = block2
        
        arena.world.CreateDistanceJoint(bodyA = block, bodyB = block2, anchorA = block.worldCenter, anchorB = block2.worldCenter, collideConnected = True)
                
    def normal(self):
        shape = self.shapes[0]
        s = shape.fixtures[0].shape
        block = arena.world.CreateDynamicBody(
            position = shape.position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=shape.fixtures[0].density,
                friction = shape.fixtures[0].friction,
                restitution=shape.fixtures[0].restitution
            ),
            userData = shape.userData
        )
        block.color = self.alt_color
        arena.world.DestroyBody(self.shapes[0])
        self.shapes[0] = block
        
        oldpos = shape.position
        shape2 = self.shapes[1]
        newpos = shape2.position
        s = shape2.fixtures[0].shape
        block2 = arena.world.CreateDynamicBody(
            position = (oldpos.x - 3, oldpos.y),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=shape2.fixtures[0].density,
                friction = shape2.fixtures[0].friction,
                restitution=shape2.fixtures[0].restitution
            ),
            userData = shape2.userData
        )
        block2.color = self.alt_color_2
        arena.world.DestroyBody(self.shapes[1])
        self.shapes[1] = block2
        
        arena.world.CreateDistanceJoint(bodyA = block, bodyB = block2, anchorA = block.worldCenter, anchorB = block2.worldCenter, collideConnected = True)

class CrowdMember(Player):
    def __init__(self, direction, start_x, color, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), color, arena, 0)
        self.timeToJump = random.random() * 10000 + 1000
        
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
    
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes()
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction=CHAR_FRICTION,
                restitution=0,
                filter = b2Filter(
                    categoryBits = 0x0010,
                    maskBits = 0xFFFF ^ 0x0010
                )
            ),
            userData = "crowd member"
        )

        block.color = self.color_2
        self.shapes.append(block)
        
        w = self.size[0]
        h = self.size[1]
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1*w-.6,-1*h-.1),(w+.6,-1*h-.1),(w+.6,h+.1),(-1*w-.6,h+.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False
        self.dx = 0
      
    def update(self, dt, nogravity = False):
        if(self.dead):
            self.dead = False
            return
            
        self.shapes[0].awake = True
        if nogravity: pass
        else:
            if abs(self.shapes[0].transform.angle) > 0.1  and abs(self.shapes[0].transform.angle - 180) > 0.1 and self.shapes[0].linearVelocity.y == 0:
                self.jumpBackUp()
        
            self.timeToJump -= dt
            if self.timeToJump <= 0 and self.shapes[0].linearVelocity.y == 0:
                self.jump()
                self.timeToJump = random.random() * 10000 + 1000
            maxspeed = 3
            
            if self.shapes[0].linearVelocity.x != 0 and random.random() > 0.7 and self.shapes[0].linearVelocity.y == 0:
                self.shapes[0].linearVelocity.x = 0
                
            if self.shapes[0].linearVelocity.x == 0 and random.random() > 0.7 and self.shapes[0].linearVelocity.y == 0:
                self.shapes[0].linearVelocity.x = 5 * (random.random() * 4 - 2)
            
    def jump(self):
        if len(self.shapes[0].contacts) > 0:
            self.shapes[0].linearVelocity.y -= 15
            
    def jumpBackUp(self):
        if len(self.shapes[0].contacts) > 0:
            self.shapes[0].linearVelocity.y = -10
            self.shapes[0].angularVelocity = 2

CHARACTER_HEIGHT = 278
CHARACTER_WIDTH = 196
# How much room between each button?
CHARACTER_PADDING = [100, 20]
CHARACTER_STEP = [4, 4]

characters = ["Lars", "Buster", "Ted", "SmithWickers", "Pate", "EricStrohm"]
characterColors = [(255,255,0), (153,255,0), (166,0,0), (255,102,0), (0,51,255), (128,128,128)]
p1choice = 0
p2choice = 1

def initCharSelect():
    images["P1Select"] = load_image("P1Select.png", (255,191,255))
    images["P2Select"] = load_image("P2Select.png", (255,191,255))
    
    # Load all the menu buttons
    for i, character in enumerate(characters):
        images[character] = load_image(character + ".png")
        images[character][0].set_colorkey(pygame.Color("white"))
        # Change imagerect to where the image actually is on screen
        images[character][1].left = CHARACTER_PADDING[0] + (CHARACTER_STEP[0] + CHARACTER_WIDTH) * (i % 3)
        images[character][1].top  = CHARACTER_PADDING[1] + (CHARACTER_STEP[1] + CHARACTER_HEIGHT) * math.trunc(i / 3)
        
        images[character+"_winner"] = load_image(character + "_winner.png", (255,122,122))
        # Change imagerect to where the image actually is on screen
        images[character+"_winner"][1].left = (SCREEN_WIDTH_PX - 800) / 2
        images[character+"_winner"][1].top  = 0
        
        images[character+"_loser"] = load_image(character + "_loser.png", (255,122,122))
        # Change imagerect to where the image actually is on screen
        images[character+"_loser"][1].left = (SCREEN_WIDTH_PX - 800) / 2
        images[character+"_loser"][1].top  = 0
    
def drawCharSelect(screen):
    global gameState, p1choice, p2choice
    # TODO: put an image here?
    screen.fill(pygame.Color("white"))
    
    for character in characters:
        screen.blit(images[character][0], images[character][1])
        
    p1left = CHARACTER_PADDING[0] + (CHARACTER_STEP[0] + CHARACTER_WIDTH) * (p1choice % 3)
    p1top  = CHARACTER_PADDING[1] + (CHARACTER_STEP[1] + CHARACTER_HEIGHT) * math.trunc(p1choice / 3)
        
    p2left = CHARACTER_PADDING[0] + (CHARACTER_STEP[0] + CHARACTER_WIDTH) * (p2choice % 3)
    p2top  = CHARACTER_PADDING[1] + (CHARACTER_STEP[1] + CHARACTER_HEIGHT) * math.trunc(p2choice / 3)
    
    screen.blit(images["P1Select"][0], (p1left, p1top))
    screen.blit(images["P2Select"][0], (p2left, p2top))
        
def charSelectInput(event):
    global lastButtonClicked
    global gameState, p1choice, p2choice
    global arena, prepare, char1, char2, char1color, char2color
    
    if hasattr(event, 'key') and event.type is pygame.KEYDOWN:
        if event.key == K_SPACE or event.key == K_RETURN:
            char1, char2 = characters[p1choice], characters[p2choice]
            char1color, char2color = characterColors[p1choice], characterColors[p2choice]
            arena = Arena()
            prepare = PrepareForBattle()
            gameState = "Prepare"
            
        if event.key == K_UP:
            p2choice -= 3
            if p2choice < 0: p2choice += 6
        if event.key == K_DOWN: 
            p2choice += 3
            if p2choice > 5: p2choice -= 6
        if event.key == K_LEFT: 
            p2choice -= 1
            if p2choice < 0: p2choice = 5
        if event.key == K_RIGHT: 
            p2choice += 1
            if p2choice > 5: p2choice = 0
        
        if event.key is K_w: 
            p1choice -= 3
            if p1choice < 0: p1choice += 6
        if event.key is K_s: 
            p1choice += 3
            if p1choice > 5: p1choice -= 6
        if event.key is K_a: 
            p1choice -= 1
            if p1choice < 0: p1choice = 5
        if event.key is K_d: 
            p1choice += 1
            if p1choice > 5: p1choice = 0



def init():
    global time_font_lg,time_font_sm,time_font_giant                # Font
    global player1, player2    # Players
    global currentArena        # Midpoint
    global gameState            # duh
    global world            # the Box2D world
    global arena, prepare            # Arena for minigame
    global effects          # Sort of like AwesomeRogue!
    global images           # Dict of all the images we have to draw
    
    effects = []
    
    time_font_sm = pygame.font.Font("fonts/ka1.ttf", 30)
    time_font_lg = pygame.font.Font("fonts/ka1.ttf", 60)
    time_font_giant = pygame.font.Font("fonts/ka1.ttf", 120)
    
    #arena = Arena()
    #prepare = PrepareForBattle()
    gameState = "Title"
    
    # Load some images
    images = {}
    images["bomb"] = load_image("bomb.png", (255, 255, 255))
    images["goal left"] = load_image("GOOOAL.png", (255,255,255))
    images["goal right"] = [pygame.transform.flip(images["goal left"][0], True, False), images["goal left"][1]]
    images["red arrow"] = load_image("red_arrow.png", (255,255,255))
    images["blue arrow"] = load_image("blue_arrow.png", (255,255,255))
    
    # Make sure alpha will properly render
    for key in images:
        images[key] = (images[key][0].convert_alpha(), images[key][1])
        
    
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                                  MAIN LOOP                             |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
init()
initTitle()
while 1:
    dt = clock.tick(TARGET_FPS)
    screen.fill((255,255,255))
    
    # Check user input
    for event in pygame.event.get():
        if gameState == "Title":
            titleInput(event)
        if gameState == "CharSelect":
            charSelectInput(event)
        if gameState == "GameOver":
            gameOverInput(event)
        if event.type is pygame.QUIT: sys.exit()
        if hasattr(event, 'key'):
            if event.key is K_ESCAPE: 
                if event.type is pygame.KEYDOWN: sys.exit()
            if gameState == "Arena":
                arena.doAction(event)
            if gameState == "Prepare":
                prepare.doAction(event)
    
    if gameState == "Title":
        drawTitle(screen)
    if gameState == "CharSelect":
        drawCharSelect(screen)
    if gameState == "Prepare":
        prepare.update(dt)
        prepare.draw(screen)
    if gameState == "Arena":
        arena.update(dt)
        arena.draw(screen)

        for i, ef in enumerate(effects):
            ef.update()
            ef.draw(screen)
            if ef.done:
                del effects[i]
    if gameState == "GameOver":
        drawGameOver(screen)
            
    pygame.display.flip()
