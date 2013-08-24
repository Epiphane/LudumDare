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
exec(open('camera.py'))
exec(open('character_class.py'))

def init():
    global time_font_lg,time_font_sm                # Font
    global player1, player2    # Players
    global currentArena        # Midpoint
    global camera            # duh
    global Import_sprite,interface        # RenderPlains
    global shapes           # all the Box2D objects
    global world            # the Box2D world
    global arena            # Arena for minigame
    
    time_font_sm = pygame.font.Font("fonts/ka1.ttf", 30)
    time_font_lg = pygame.font.Font("fonts/ka1.ttf", 60)
    
    player1 = Player(1, 8)
    player2 = Player(-1, 9)
    currentArena = 8.5
    
    camera = Camera(currentArena)
    
    arena = Arena()
    
    # Init physics "world", defining gravity. doSleep means that if an object
    # comes to rest, it can "sleep" and be ignored by the physics engine for a bit.
    world = b2World(gravity=(0, -10), doSleep = True)
    
    # Initialize the ground. Will also need to initialize obstacles/arena
    # components here later on.
    ground = world.CreateStaticBody(
        position = (0, -200),
        shapes = b2PolygonShape(box = (50,10))
    )
    
    body = world.CreateDynamicBody(position = (20,4))
    box = body.CreatePolygonFixture(box = (5,5), density = 1, friction = 0.3)
    
    shapes = []
    shapes.append(box)
    shapes.append(ground.fixtures[0])
    
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                                  MAIN LOOP                             |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
init()
while 1:
    # USER INPUT
    sleeptime = 1000 / 30
    deltat = clock.tick(sleeptime)
    
    # Update a "tick" in physics land
    world.Step(deltat, 10, 10)
                
    # Update minigame. If it returns true, make a new minigame
    winner = arena.update(deltat)
    if  winner:
        if winner == 1: changeArena(currentArena + player1.direction)
        elif winner == 2: changeArena(currentArena + player2.direction)
        arena = Arena()
    
    # Reset forces for the next frame
    world.ClearForces()
        
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
    arena.draw(screen)
                        
    pygame.display.flip()