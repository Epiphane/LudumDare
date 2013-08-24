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
        position = (200, 37.5),
        shapes = b2PolygonShape(box = (400,1))
    )
    
    ground.name = "ground"
    
    ceiling = world.CreateStaticBody(
        position = (200, -1),
        shapes = b2PolygonShape(box = (400,1))
    )
    
    ceiling.name = "ceiling"
    
    landMineTest = world.CreateStaticBody(
                position = (225,37.5),
                fixtures = b2FixtureDef(
                    shape = b2CircleShape(radius=2),
                    isSensor = True))
    landMineTest.name = "land mine"
    
    body = world.CreateDynamicBody(position = (200, 10))
    box = body.CreatePolygonFixture(box = (5,5), density = 1, friction = 0.3)
    box.name = "old box"
    
   # body2 = world.CreateDynamicBody(position = (218,-2))
   # box2 = body.CreatePolygonFixture(box = (5,5), density = 1, friction = 0.3)
    
    shapes = []
    shapes.append(box)
   # shapes.append(box2)
    shapes.append(ceiling.fixtures[0])
    shapes.append(ground.fixtures[0])
    shapes.append(landMineTest.fixtures[0])
    
    player1 = Player(1, 8, (255,0,0))
    player2 = Player(-1, 9, (0,0,255))
    
    player1.name = "p1"
    player2.name = "p2"
    
    currentArena = 8.5
    
    camera = Camera(currentArena)
    
    arena = SoccerArena()
    
    # Initialize the contact handler
    contactHandler = ContactHandler()

    
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
                player1.input["left"] = (event.type is pygame.KEYDOWN)
            if event.key is K_d:
                player1.input["right"] = (event.type is pygame.KEYDOWN)
            if event.key == K_LEFT:
                player2.input["left"] = (event.type is pygame.KEYDOWN)
            if event.key == K_RIGHT:
                player2.input["right"] = (event.type is pygame.KEYDOWN)
            if event.key == K_UP:
                player2.shapes[0].body.ApplyForce(force=(500,0), point=(0,3), wake=True)
            if event.key is K_w:
                player1.shapes[0].body.ApplyForce(force=(-500,0), point=(0,3), wake=True)
                        
    player1.update()    
    player2.update()
                    
    # Update a "tick" in physics land
    world.Step(TIME_STEP*2, 10, 10)
    
    camera.update()
    camera.draw(screen)
    arena.draw(screen)
                        
    pygame.display.flip()