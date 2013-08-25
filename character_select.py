CHARACTER_HEIGHT = 278
CHARACTER_WIDTH = 196
# How much room between each button?
CHARACTER_PADDING = [100, 20]
CHARACTER_STEP = [4, 4]

characters = ["Lars", "Buster", "Ted", "SmithWickers", "Pate", "EricStrohm"]
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
    global arena, prepare, char1, char2
    
    if hasattr(event, 'key') and event.type is pygame.KEYDOWN:
        if event.key == K_SPACE or event.key == K_RETURN:
            char1, char2 = characters[p1choice], characters[p2choice]
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
