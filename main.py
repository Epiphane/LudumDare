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
    global gameState            # duh
    global world            # the Box2D world
    global arena            # Arena for minigame
    global effects          # Sort of like AwesomeRogue!
    global images           # Dict of all the images we have to draw
    
    time_font_sm = pygame.font.Font("fonts/ka1.ttf", 30)
    time_font_lg = pygame.font.Font("fonts/ka1.ttf", 60)
    
    arena = Arena()
    
    

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
    
    # Check user input
    for event in pygame.event.get():
        if event.type is pygame.QUIT: sys.exit()
        if hasattr(event, 'key'):
            if event.key is K_ESCAPE: 
                if event.type is pygame.KEYDOWN: sys.exit()
            arena.doAction(event)
                        
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
    
def initWalls():