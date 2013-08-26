def winGame(winner):
    global gameWinner, gameLoser, gameState
    global gameWinnerColor, gameLoserColor
    gameState = "GameOver"
    if winner == 1:
        gameWinner = char1
        gameWinnerColor = char1color
        gameLoser = char2
        gameLoserColor = char2color
    else:
        gameWinner = char2
        gameWinnerColor = char2color
        gameLoser = char1
        gameLoserColor = char1color
    
    #arena.cleanUp()
    # Find the bomb drop and PUT A STOP TO THE MADNESS
    for ef in effects:
        if ef.__class__.__name__ == "BombDrop":
            ef.finish()
            
    initGameOver()

game_over_buttons = [ ["menu",0], ["quit",0]]

def initGameOver():
    # Load all the menu buttons
    buttonY = SCREEN_HEIGHT_PX/2 - BTN_HEIGHT/2 - BTN_STEP
    buttonX = SCREEN_WIDTH_PX/2  - BTN_WIDTH/2
    for button in game_over_buttons:
        for state in states:
            imageName = button[0] + "-" + state
            images[imageName] = load_image(imageName + ".png")
            images[imageName][0].set_colorkey(pygame.Color("white"))
            # Change imagerect to where the image actually is on screen
            images[imageName][1].left = buttonX
            images[imageName][1].top  = buttonY
        
        buttonY += BTN_STEP
            
def gameOverInput(event):
    # Grab mouse coords
    mousePos = pygame.mouse.get_pos()
        
    global lastButtonClicked
    global gameState
    
    # Is it just a mousemove?
    if event.type == pygame.MOUSEMOTION:
        for i, button in enumerate(game_over_buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                # Tell the button to highlight
                game_over_buttons[i][1] = 1
            else:
                # Deselect button
                game_over_buttons[i][1] = 0
    
    # Is it a new mouseclick?
    if event.type == pygame.MOUSEBUTTONDOWN:
        for i, button in enumerate(game_over_buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                lastButtonClicked = button[0]
                game_over_buttons[i][1] = 2
                
    # Is it a mouse up?
    if event.type == pygame.MOUSEBUTTONUP:
        for i, button in enumerate(game_over_buttons):
            if images[button[0] + "-des"][1].collidepoint(mousePos):
                game_over_buttons[i][1] = 1
                if lastButtonClicked == button[0]:
                    # Positive match! Rejoice!
                    if button[0] == "menu":
                        gameState = "Title"
                    elif button[0] == "quit":
                        sys.exit()
                else:
                    # Make sure we wipe the last button clicked
                    lastButtonClicked = ""
    
def drawGameOver(screen):
    screen.fill(gameWinnerColor, (0,0,SCREEN_WIDTH_PX/2,SCREEN_HEIGHT_PX))
    screen.fill(gameLoserColor, (SCREEN_WIDTH_PX/2,0,SCREEN_WIDTH_PX/2,SCREEN_HEIGHT_PX))
    # TODO: put an image here?
    screen.blit(images[gameLoser+"_loser"][0], ((SCREEN_WIDTH_PX/2 - 400),0))
    screen.blit(images[gameWinner+"_winner"][0], ((SCREEN_WIDTH_PX/2 - 400),0))
        
    for button in game_over_buttons:
        imageName = button[0] + "-" + states[button[1]]
        screen.blit(images[imageName][0], images[imageName][1])