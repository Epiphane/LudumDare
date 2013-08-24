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
    
    # Init physics "world", defining gravity. doSleep means that if an object
    # comes to rest, it can "sleep" and be ignored by the physics engine for a bit.
    world = b2World(gravity=(0, 10), doSleep = True)
    
    # Initialize the ground. Will also need to initialize obstacles/arena
    # components here later on.
    ground = world.CreateStaticBody(
        position = (0, 37.5),
        shapes = b2PolygonShape(box = (1,400))
    )
    
    body = world.CreateDynamicBody(position = (1052,20))
    box = body.CreatePolygonFixture(box = (5,5), density = 1, friction = 0.3)
    
   # body2 = world.CreateDynamicBody(position = (218,-2))
   # box2 = body.CreatePolygonFixture(box = (5,5), density = 1, friction = 0.3)
    
    shapes = []
    shapes.append(box)
   # shapes.append(box2)
    shapes.append(ground.fixtures[0])
    
    player1 = Player(1, 8)
    player2 = Player(-1, 9)
    currentArena = 8.5
    
    camera = Camera(currentArena)
    
    arena = SoccerArena()

    
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                                  MAIN LOOP                             |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
init()
while 1:
    # Reset forces for the next frame
    world.ClearForces()
        
    # Update a "tick" in physics land
    world.Step(TIME_STEP, 10, 10)
    
    deltat = clock.tick(TARGET_FPS)
    
    # Update minigame. If it returns true, make a new minigame
    winner = arena.update(deltat)
    if  winner:
        if winner == 1: changeArena(currentArena + player1.direction)
        elif winner == 2: changeArena(currentArena + player2.direction)
        else: changeArena(currentArena)
        arena = Arena()
    
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
            if event.key == K_LEFT:
                if event.type is pygame.KEYDOWN:
                    print("left trigger")
                    #shapes[0].body.ApplyForce( f, p, True )
                    shapes[0].body.ApplyLinearImpulse( b2Vec2(0, 50),
                        shapes[0].body.GetWorldPoint())
                    
    camera.update()
    camera.draw(screen)
    arena.draw(screen)
                        
    pygame.display.flip()