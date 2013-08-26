def changeArena(arenaNum):
    global currentArena        # Midpoint
    global camera
    
    currentArena = arenaNum
    camera.panCam(arenaNum)
    camera.delay = 200

char1 = "Lars"
char2 = "Buster"
class Arena():
    def __init__(self):
        self.timeRemaining = 10000 # 10 seconds
        self.drawRed = 0
        self.bignum = 10
        self.shapes = []
        self.crowd = []
        
        self.modeName = "none"
        
        self.player1possession = 0
        self.player2possession = 0
        
        self.modifications = []
    
        # Initialize effects queue
        self.effects = []
    
        # Init physics "world", defining gravity. doSleep means that if an object
        # comes to rest, it can "sleep" and be ignored by the physics engine for a bit.
        self.world = b2World(gravity=(0, 25), doSleep = False)
        
        # Initialize the contact handler
        self.world.contactListener = ContactHandler()
        
        self.initWalls()
        self.ball = None
        self.startGame(STAGE_WIDTH_M / 2)
        
        self.camera = Camera(STAGE_WIDTH_M / 2)
        
        self.score = [0,0]
        
        self.toInit = False
        self.pauseTime = 0
        
        self.createCrowd(2, 24)
        self.createCrowd(227, 248)
        
        #self.bombDrop()
        #self.changeBall()
        #self.nogravity()
        #self.slowmo()
  
    def startGame(self, middle_x, delay=0):
        global char1, char2
        if delay > 0:
            self.toInit = (middle_x, delay)
            return
        resumeBackground()
        self.toInit = False
        self.pauseTime = delay
        
        if hasattr(self,'player2'):
            self.player1.materialize(middle_x - SCREEN_WIDTH_M / 4, self, 2)
            self.player2.materialize(middle_x + SCREEN_WIDTH_M / 4, self, 1)
        else:
            if char1 == "Lars":
                self.player1 = Lars(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "Buster":
                self.player1 = Buster(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "SmithWickers":
                self.player1 = SmithWickers(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "Pate":
                self.player1 = Pate(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            elif char1 == "EricStrohm":
                self.player1 = EricStrohm(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
            else: # char1 == "Ted":
                self.player1 = Ted(1, middle_x - SCREEN_WIDTH_M / 4, self, 1)
                
            if char2 == "Lars":
                self.player2 = Lars(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "Buster":
                self.player2 = Buster(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "SmithWickers":
                self.player2 = SmithWickers(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "Ted":
                self.player2 = Ted(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            elif char2 == "EricStrohm":
                self.player2 = EricStrohm(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
            else: # char2 == "Pate":
                self.player2 = Pate(-1, middle_x + SCREEN_WIDTH_M / 4, self, 2)
        
        if self.ball is not None: self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = (middle_x,28),
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1.3),
                density=1,
                restitution=0.5,
                friction = 50),
            userData="ball")
            
        self.ball.color = pygame.color.Color(128,128,128)
        self.shapes.append(self.ball)
        
        self.textAlpha = 255
        self.dispText = "Go!"
        
    def createCrowd(self, minx, maxx):
        numCrowd = int(math.ceil(random.random() * 10) + 10)
        width = maxx - minx
        
        for i in range(numCrowd):
            member = CrowdMember(0, minx + random.random() * width, (int(random.random()*255),int(random.random()*255),int(random.random()*255)), self)
            self.crowd.append(member)
            self.shapes.append(member.shapes[0])
        
    def initWalls(self):
        ground = self.world.CreateStaticBody(
            position = (0, 37.5),
            shapes = b2PolygonShape(box = (STAGE_WIDTH_M,1)),
            userData = "ground"
        )
        ground.color = pygame.color.Color(0,128,0)
        self.shapes.append(ground)
        
        ceiling = self.world.CreateStaticBody(
            position = (0, -1),
            shapes = b2PolygonShape(box = (STAGE_WIDTH_M,1)),
            userData = "ceiling"
        )
        self.shapes.append(ceiling)
        
        leftWall = self.world.CreateStaticBody(
            position = (25, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        #self.shapes.append(leftWall)
        
        rightWall = self.world.CreateStaticBody(
            position = (225, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
        #self.shapes.append(rightWall)
        
        leftWall = self.world.CreateStaticBody(
            position = (0, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        #self.shapes.append(leftWall)
        
        rightWall = self.world.CreateStaticBody(
            position = (250, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
        
        goal_left = self.world.CreateStaticBody(
            position = (223, 37),
            shapes = b2PolygonShape(box = (2,8))
        )
        goal_left.fixtures[0].sensor = True
        goal_left.userData = "goal left"
        self.shapes.append(goal_left)
        
        goal_right = self.world.CreateStaticBody(
            position = (29, 37),
            shapes = b2PolygonShape(box = (2,8))
        )
        goal_right.fixtures[0].sensor = True
        goal_right.userData = "goal right"
        self.shapes.append(goal_right)
        
    # Detects if the player is off camera and draws an arrow to them
    def playerOffCamera(self):
        # A player is off camera if all 4 of their vertices don't intersect with the screen.
        SCREEN_RECT.left = self.camera.centerX_in_meters * PPM - SCREEN_WIDTH_PX / 2
        offsetX, offsetY = self.camera.getOffset_in_px()
        verts = vertices(self.player1.shapes[0].fixtures[0])
        inside = False
        for vert in verts:
            inside = inside or SCREEN_RECT.collidepoint( (vert.x, vert.y) )
            
        if not inside:
            self.drawArrow(self.player1)
            
        verts = vertices(self.player2.shapes[0].fixtures[0])
        inside = False
        for vert in verts:
            inside = inside or SCREEN_RECT.collidepoint( (vert.x, vert.y) )
                
        if not inside:
            self.drawArrow(self.player2)
            
    # Draw an arrow to the lost, lonely player.        
    def drawArrow(self, player):
        position = player.shapes[0].position
        arrowX, arrowY = 0, 0
        
        # Identify the x and y to draw the arrow in
        arrowY = position.y * PPM - 70
        if position.x < self.camera.centerX_in_meters:
            arrowX = 5
            arrowImg = pygame.transform.flip(images["red arrow"][0], True, False)
        else:
            arrowImg = images["red arrow"][0]
            arrowX = SCREEN_WIDTH_PX - (5 + images["red arrow"][1].width)
        
        screen.blit(arrowImg, (arrowX, arrowY))
        
    # Lets the arena know that a player has touched the ball recently
    def gotPossession(self, playerFixture):
        if playerFixture.body.userData == "player1":
            self.player1possession = 50
        elif playerFixture.body.userData == "player2":
            self.player2possession = 50
        else:
            print("wat")
        
    def update(self, dt):
        self.camera.update(self.ball)
        
        if self.toInit is not False:
            self.startGame(self.toInit[0], self.toInit[1] - dt)
                        
            # Update a "tick" in physics land
            self.world.Step(TIME_STEP*2, 10, 10)
            
            # Reset forces for the next frame
            self.world.ClearForces()
            
            if(self.player1.dead):
                self.player1.dead = False
                self.player1.destroy()
            if(self.player2.dead):
                self.player2.dead = False
                self.player2.destroy()
            return
    
        self.timeRemaining -= dt
        oldbignum = self.bignum
        self.bignum = math.trunc(self.timeRemaining / 1000)
        if self.bignum != oldbignum and self.bignum < 4: self.drawRed = 128
        if(self.timeRemaining <= 0):
            self.randomEvent()
            self.timeRemaining = 10000
            
        self.player1.update(self.world.gravity == b2Vec2(0,0))
        self.player2.update(self.world.gravity == b2Vec2(0,0))
        for member in self.crowd:
            member.update(dt, self.world.gravity == b2Vec2(0,0))
        
        # Murder things that need murdering
        for i, shape in enumerate(self.shapes):
            if shape.userData == "kill me":
                shape.DestroyFixture(shape)
                del self.shapes[i]
        
        for i, ef in enumerate(self.effects):
            ef.update()
            ef.draw(screen)
            if ef.done:
                del self.effects[i]
        
        self.ball.linearVelocity.x *= BALL_FRICTION
        
        # Check the "possession" status of each character and change friction as necessary
        #if self.player1possession > 0 and self.player1possession > self.player2possession:
        #    self.player1.shapes[0].friction = 10
        #    print("fraction", self.player1.shapes[0].friction)                    
        #else:                                    
        #    self.player1.shapes[0].friction = 0.3
        #                                         
        #if self.player2possession > 0 and self.player2possession > self.player1possession:
        #    self.player1.shapes[0].friction = 10
        #else: 
        #    self.player2.shapes[0].friction = 0.3
        
        # Decrement the possession timers
        self.player1possession -= 1
        if self.player1possession < 0: self.player1possession = 0
        self.player2possession -= 1
        if self.player2possession < 0: self.player2possession = 0
        
        # Update a "tick" in physics land
        self.world.Step(TIME_STEP*2, 10, 10)
        
        # Reset forces for the next frame
        self.world.ClearForces()
                
    def draw(self, screen, showTimer = True):
        
        self.camera.draw(screen)
        
        if showTimer:
            self.drawTimer(screen)
        
        offsetX, offsetY = self.camera.getOffset_in_px()
        self.player1.draw(screen, offsetX, offsetY)
        self.player2.draw(screen, offsetX, offsetY)
        for member in self.crowd: pass
            #DrawPolygon(vertices_with_offset(member.fixtures[0], offsetX, offsetY), (0,0,0), member.color)
        
        for shape in self.shapes:
            if isinstance(shape.fixtures[0].shape, b2CircleShape):
                pos = (int(shape.position.x * PPM - offsetX), int(shape.position.y * PPM + offsetY))
                if shape.userData == "ball":
                    DrawCircle(pos, shape.fixtures[0].shape.radius, shape.color)
                else:
                    DrawCircle(pos, shape.fixtures[0].shape.radius, (0,0,0))
            elif shape.userData is not None:
                if shape.userData == "goal left" or shape.userData == "goal right":
                    DrawImage(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), shape.userData)
                else:
                    if hasattr(shape, "color"):
                        DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0), shape.color)
                    else:
                        DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0))
            else:
                if hasattr(shape, "color"):
                    DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0), shape.color)
                else:
                    DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0))
            
        # Draw arrows if the player is off screen
        self.playerOffCamera()
    
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), False, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), False, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 2
        
        if(self.bignum == 10): screen.blit(text, (SCREEN_WIDTH_PX / 2 - 1100,0))
        else: screen.blit(text, (SCREEN_WIDTH_PX / 2 - 70,0))
        screen.blit(text_sm, (SCREEN_WIDTH_PX / 2,0))
        
        text_l = time_font_lg.render(str(self.score[0]), False, (0,0,0))
        text_r = time_font_lg.render(str(self.score[1]), False, (0,0,0))
        screen.blit(text_l, (0,0))
        screen.blit(text_r, (SCREEN_WIDTH_PX - 60,0))
        
        if self.textAlpha > 0:
            self.textAlpha -= 2.5
            
            text = time_font_giant.render(self.dispText, False, (0, 0, 0), (255,255,255, 0))
            if self.dispText == "SLOWWMOOOOO!":
                surface = pygame.Surface((text.get_width()+30, text.get_height()))
                surface.blit(text, (30,0))
                text = time_font_giant.render(self.dispText, False, (0, 0, 0), (255,255,255, 0))
                surface.blit(text, (0,0))
                surface.set_colorkey((255,255,255))
                surface.set_alpha(self.textAlpha)
                screen.blit(surface, (SCREEN_WIDTH_PX / 2 - text.get_width()/2,180))
            else:
                surface = pygame.Surface((text.get_width(), text.get_height()))
                surface.blit(text, (0,0))
                surface.set_colorkey((255,255,255))
                surface.set_alpha(self.textAlpha)
                screen.blit(surface, (SCREEN_WIDTH_PX / 2 - text.get_width()/2,180))

    def doAction(self, event):
        if event.key is K_a:
            self.player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            self.player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            self.player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            self.player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP:
            self.player2.input["up"] = (event.type is pygame.KEYDOWN)
            self.player2.jump(self.world.gravity)
        if event.key == K_DOWN:
            self.player2.input["down"] = (event.type is pygame.KEYDOWN)
            self.player2.dive()
        if event.key is K_w:
            self.player1.input["up"] = (event.type is pygame.KEYDOWN)
            self.player1.jump(self.world.gravity)
        if event.key is K_s:
            self.player1.input["down"] = (event.type is pygame.KEYDOWN)
            self.player1.dive()
            
    def changeBall(self):
        print "Changeball triggered"
        self.shapes.remove(self.ball)
        position = self.ball.position
        self.world.DestroyBody(self.ball)
        self.ball = self.world.CreateDynamicBody(position = position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(vertices=[(-0.33,1  ),
                                                (-1  ,0.33),
                                                (-1  ,-0.33),
                                                (-0.33 ,-1 ),
                                                (0.33 ,-1 ),
                                                (1   ,-0.33),
                                                (1   ,0.33),
                                                (-0.33 ,1  )]),
                density=10,
                restitution=0.5,
                friction = 50),
            userData="ball")
        self.ball.color = pygame.color.Color(128,128,128)
        self.shapes.append(self.ball)
        
        self.textAlpha = 255
        self.dispText = "ROCK BALLSTER!"
    
    def changeBall_revert(self):
        print "Changeball reverted"
        self.shapes.remove(self.ball)
        position = self.ball.position
        self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = position,
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1.3),
                density=1,
                restitution=0.5,
                friction = 50),
            userData="ball")
            
        self.ball.color = pygame.color.Color(128,128,128)
        self.shapes.append(self.ball)
     
    def slowmo(self):
        print "slow mo!"
        global TIME_STEP
        TIME_STEP /= 4
        
        self.textAlpha = 255
        self.dispText = "SLOWWMOOOOO!"
     
    def slowmo_revert(self):
        print "slow mo reverted"
        global TIME_STEP
        TIME_STEP *= 4
        
    def giantMode(self):
        self.player1.toExpand = True
        self.player2.toExpand = True
    
    def giantMode_revert(self):
        self.player1.toNormalSize = True
        self.player2.toNormalSize = True
        
    def cleanUp(self):
        self.crowd = []
        while len(self.shapes) > 0:
            shape = self.shapes[0]
            self.world.DestroyBody(shape)
            self.shapes.remove(shape)
        
    def bombDrop(self):
        print "bomb droppin time!"
        bombs = BombDrop()
        effects.append(bombs)
        
        self.textAlpha = 255
        self.dispText = "Bombs!"
        
    def bombDrop_revert(self):
        print "bomb droppin reversion!"
        # Find the bomb drop and PUT A STOP TO THE MADNESS
        for ef in effects:
            if ef.__class__.__name__ == "BombDrop":
                ef.finish()
        
    def randomEvent(self):
        randomEvents = [ [self.bombDrop, self.bombDrop_revert],
                         [self.changeBall, self.changeBall_revert],
                         [self.giantMode, self.giantMode_revert],
                         [self.slowmo, self.slowmo_revert]]
                         
        while len(self.modifications) > 0:
            mod = self.modifications[0]
            mod[1]()
            del self.modifications[0]
            
        event = math.floor(random.random() * len(randomEvents))
        
        # Grab the function from the list of events and run it
        mod = randomEvents[int(event)]
        mod[0]()
        self.modifications.append(mod)
        
        # Stop all inferior sounds
        pygame.mixer.stop()
        # Play the "woopwoopwoop" transition sound
        playSound("transition")
        # Put on a new backtrack, DJ!
        playSound("background")
            
            
class PrepareForBattle(Arena):
    def __init__(self):
        self.timeRemaining = 3000
        self.bignum = 3
        playSound("start")
        
    def draw(self, screen):
        arena.draw(screen, False)
        
        self.drawTimer(screen)
        
        text = (time_font_lg.render("PREPARE", False, (0, 0, 0)), time_font_lg.render("YOURSELF", False, (0, 0, 0)))
        screen.blit(text[0], (SCREEN_WIDTH_PX / 2 - 210,180))
        screen.blit(text[1], (SCREEN_WIDTH_PX / 2 - 220,260))
        
        
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), False, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), False, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 2
        
        screen.blit(text, (SCREEN_WIDTH_PX / 2 - 70,0))
        screen.blit(text_sm, (SCREEN_WIDTH_PX / 2,0))
        
    def update(self, dt):
        self.timeRemaining -= dt
        oldbignum = self.bignum
        self.bignum = math.trunc(self.timeRemaining / 1000)
        if self.bignum != oldbignum and self.bignum < 4: self.drawRed = 128
        if(self.timeRemaining <= 0):
            global arena, gameState
            gameState = "Arena"
            # Play the first background
            playSound("background")

    def doAction(self, event):
        if event.key is K_a:
            arena.player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            arena.player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            arena.player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            arena.player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP:
            arena.player2.input["up"] = (event.type is pygame.KEYDOWN)
        if event.key == K_DOWN:
            arena.player2.input["down"] = (event.type is pygame.KEYDOWN)
        if event.key is K_w:
            arena.player1.input["up"] = (event.type is pygame.KEYDOWN)
        if event.key is K_s:
            arena.player1.input["down"] = (event.type is pygame.KEYDOWN)