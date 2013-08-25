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
exec(open('title.py'))
exec(open('effects.py'))
exec(open('ui_class.py'))
exec(open('arena_mechanics.py'))
exec(open('camera.py'))
exec(open('gameOver.py'))
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
    
    effects = []
    
    time_font_sm = pygame.font.Font("fonts/ka1.ttf", 30)
    time_font_lg = pygame.font.Font("fonts/ka1.ttf", 60)
    
    arena = Arena()
    gameState = "Title"
    
    # Load some images
    images = {}
    images["bomb"] = load_image("da bomb.png")
    images["goal left"] = load_image("GOOOAL.png", (255,255,255))
    images["goal right"] = [pygame.transform.flip(images["goal left"][0], True, False), images["goal left"][1]]
    
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
        if event.type is pygame.QUIT: sys.exit()
        if hasattr(event, 'key'):
            if event.key is K_ESCAPE: 
                if event.type is pygame.KEYDOWN: sys.exit()
            if gameState == "Arena":
                arena.doAction(event)
    
    if gameState == "Title":
        drawTitle(screen)
    if gameState == "Arena":
        arena.update(dt)
        arena.draw(screen)
                        
    for i, ef in enumerate(effects):
        ef.update()
        ef.draw(screen)
        if ef.done:
            del effects[i]
            
    pygame.display.flip()
    
