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
exec(open('character_select.py'))


def init():
    global time_font_lg,time_font_sm,time_font_giant                # Font
    global player1, player2    # Players
    global currentArena        # Midpoint
    global gameState            # duh
    global world            # the Box2D world
    global arena, prepare            # Arena for minigame
    global effects          # Sort of like AwesomeRogue!
    global images           # Dict of all the images we have to draw
    global sounds           # Music to my ears
    global musicVolume
    global soundVolume      # Shhhh
    global backgroundPlayer
    
    backgroundPlayer = pygame.mixer.Channel(7)
    
    musicVolume = soundVolume = 25
    
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
        
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    pygame.mixer.set_num_channels(20)
    sounds = loadSounds()
        
    
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
