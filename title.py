BTN_HEIGHT = 81
BTN_WIDTH = 260
# How much room between each button?
BTN_STEP = 100

buttons = [ ["play",0], ["quit",0]]
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
    screen.blit(images["title"][0], (SCREEN_WIDTH_PX / 2 - 500, 0))
    
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
    musicSlider = gui.HSlider(value=23,min=0,max=100,size=20,width=120)
    c.td(musicSlider)
    
    c.tr()
    c.td(gui.Label("SOUND VOLUME:"))
    
    c.tr()
    soundSlider = gui.HSlider(value=23,min=0,max=100,size=20,width=120)
    c.td(soundSlider)
    
    c.tr()
    c.td(gui.Label("SCREEN RESOLUTION"))
    
    c.tr()
    btn = gui.Button("BACK")
    btn.connect(gui.CLICK, app.quit)
    c.td(btn,colspan=3)
    app.run(c)
    
