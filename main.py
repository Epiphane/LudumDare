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
exec(open('effects.py'))
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
    global effects          # Sort of like AwesomeRogue!
    global images           # Dict of all the images we have to draw
    
    time_font_sm = pygame.font.Font("fonts/ka1.ttf", 30)
    time_font_lg = pygame.font.Font("fonts/ka1.ttf", 60)
    
    # Init physics "world", defining gravity. doSleep means that if an object
    # comes to rest, it can "sleep" and be ignored by the physics engine for a bit.
    world = b2World(gravity=(0, 25), doSleep = True)
    
    # Initialize the ground. Will also need to initialize obstacles/arena
    # components here later on.
    ground = world.CreateStaticBody(
        position = (200, 37.5),
        shapes = b2PolygonShape(box = (800,1)),
        userData = "ground"
    )
    
    ceiling = world.CreateStaticBody(
        position = (200, -1),
        shapes = b2PolygonShape(box = (400,1)),
        userData = "ceiling"
    )
    
    landMineTest = world.CreateStaticBody(
                position = (25,37.5),
                fixtures = b2FixtureDef(
                    shape = b2CircleShape(radius=2),
                    isSensor = True),
                userData = "land mine")
    
    body = world.CreateDynamicBody(position = (200, 10))
    box = body.CreatePolygonFixture(box = (5,5), density = 1, friction = 0.3)
    
    shapes = []
    #shapes.append(box)
   # shapes.append(box2)
    shapes.append(ceiling.fixtures[0])
    shapes.append(ground.fixtures[0])
    shapes.append(landMineTest.fixtures[0])
    currentArena = 0.5
    
    camera = Camera(currentArena)
    
    player1 = Player(1, currentArena - 0.5, (255,0,0))
    player2 = Player(-1, currentArena + 0.5, (0,0,255))
    
    arena = PrepareForBattle()
    arena.startGame(currentArena)
    
    # Initialize the contact handler
    contactHandler = ContactHandler()

    # Initialize effects queue
    effects = []
    
    # Load some images
    images = {}
    images["goal"] = load_image("GOOOAL.png")
    
    # Make sure alpha will properly render
    for key in images:
        images[key] = (images[key][0].convert_alpha(), images[key][1])
        
    
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
#                                  MAIN LOOP                             |
# -----------------------------------------------------------------------|
# -----------------------------------------------------------------------|
init()
while 1:
    # Reset forces for the next frame
    world.ClearForces()
    
    deltat = clock.tick(TARGET_FPS)
    
    camera.update(deltat)
    camera.draw(screen)
    if camera.stopped:
    
        # Update minigame. If it returns true, make a new minigame
        winner = arena.update(deltat)
        if  winner:
            if winner == 1: changeArena(currentArena + 1)
            elif winner == 2: changeArena(currentArena - 1)
            else: changeArena(currentArena)
            arena = SoccerArena()
        
        # Check user input
        for event in pygame.event.get():
            if event.type is pygame.QUIT: sys.exit()
            if hasattr(event, 'key'):
                if event.key is K_ESCAPE: 
                    if event.type is pygame.KEYDOWN: sys.exit()
                arena.doAction(event)
                            
        player1.update()
        player2.update()
                        
    # Update a "tick" in physics land
    world.Step(TIME_STEP*1.5, 10, 10)
        
    # Murder things that need murdering
    for i, shape in enumerate(shapes):
        if shape.body.userData == "kill me":
            shape.body.DestroyFixture(shape)
            del shapes[i]
        
    arena.draw(screen)
    
    for i, ef in enumerate(effects):
        ef.update()
        ef.draw(screen)
        if ef.done:
            del effects[i]
                        
    pygame.display.flip()