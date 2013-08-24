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
exec(open('init.py'))
exec(open('ui_class.py'))
exec(open('arena_mechanics.py'))
exec(open('character_class.py'))

def init():
    global font                # Font
    global player1, player2    # Players
    global currentArena        # Midpoint
    global camera            # duh
    global Import_sprite,interface        # RenderPlains
    global shapes           # all the Box2D objects
    global world            # the Box2D world
    
    font = pygame.font.Font("fonts/ka1.ttf", 30)
    
    player1 = Player(1, 8)
    player2 = Player(1, 9)
    currentArena = 8.5
    
    camera = Camera(currentArena)
    # Init physics "world", defining gravity. doSleep means that if an object
    # comes to rest, it can "sleep" and be ignored by the physics engine for a bit.
    world = b2World(gravity=(0, -10), doSleep = True)
    
    # Initialize the ground. Will also need to initialize obstacles/arena
    # components here later on.
    ground = world.CreateStaticBody(
        position = (0, -10),
        shapes = b2PolygonShape(box = (50,10))
    )
    
    body = world.CreateDynamicBody(position = (0,4))
    box = body.CreatePolygonFixture(box = (1,1), density = 1, friction = 0.3)
    
    shapes = {}
    shapes["box"] = body
    shapes["ground"] = ground
    
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                                  MAIN LOOP                             |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
init()
while 1:
    # USER INPUT
    sleeptime = 1000 / 60
    deltat = clock.tick(sleeptime)
    
    # Update a "tick" in physics land
    world.Step(sleeptime, 10, 10)
    
    # Reset forces for the next frame
    world.ClearForces()
    
    # Draw dem boxes
    for shape in shapes:
        print("drawing shapes yo")
         
    
    # Check user input
    for event in pygame.event.get():
        if event.type is pygame.QUIT: sys.exit()
        if hasattr(event, 'key'):
            if event.key is K_ESCAPE: 
                if event.type is pygame.KEYDOWN: sys.exit()
            if event.key is K_a:
                if event.type is pygame.KEYDOWN: changeArena(currentArena - 1)
            if event.key is K_d:
                if event.type is pygame.KEYDOWN: changeArena(currentArena + 1)
                
    camera.update()
    camera.draw(screen)
                        
    pygame.display.flip()