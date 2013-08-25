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
        
        self.createCrowd()
  
    def startGame(self, middle_x, delay=0):
        global char1, char2
        if delay > 0:
            self.toInit = (middle_x, delay)
            return
            
        self.toInit = False
        self.pauseTime = delay
        
        if hasattr(self,'player2'):
            self.player1.materialize(middle_x - SCREEN_WIDTH_M / 4, self)
            self.player2.materialize(middle_x + SCREEN_WIDTH_M / 4, self)
        else:
            if char1 == "Lars":
                self.player1 = Lars(1, middle_x - SCREEN_WIDTH_M / 4, self)
            elif char1 == "Buster":
                self.player1 = Buster(1, middle_x - SCREEN_WIDTH_M / 4, self)
            elif char1 == "SmithWickers":
                self.player1 = SmithWickers(1, middle_x - SCREEN_WIDTH_M / 4, self)
            elif char1 == "Pate":
                self.player1 = Pate(1, middle_x - SCREEN_WIDTH_M / 4, self)
            elif char1 == "EricStrohm":
                self.player1 = EricStrohm(1, middle_x - SCREEN_WIDTH_M / 4, self)
            else: # char1 == "Ted":
                self.player1 = Ted(1, middle_x - SCREEN_WIDTH_M / 4, self)
                
            if char2 == "Lars":
                self.player2 = Lars(-1, middle_x + SCREEN_WIDTH_M / 4, self)
            elif char2 == "Buster":
                self.player2 = Buster(-1, middle_x + SCREEN_WIDTH_M / 4, self)
            elif char2 == "SmithWickers":
                self.player2 = SmithWickers(-1, middle_x + SCREEN_WIDTH_M / 4, self)
            elif char2 == "Ted":
                self.player2 = Ted(-1, middle_x + SCREEN_WIDTH_M / 4, self)
            elif char2 == "EricStrohm":
                self.player2 = EricStrohm(-1, middle_x + SCREEN_WIDTH_M / 4, self)
            else: # char2 == "Pate":
                self.player2 = Pate(-1, middle_x + SCREEN_WIDTH_M / 4, self)
        
        if self.ball is not None: self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = (middle_x,27),
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1.3),
                density=1,
                restitution=0.5,
                friction = 50),
            userData="ball")
            
        self.ball.color = pygame.color.Color(128,128,128)
        self.shapes.append(self.ball.fixtures[0])
        
    def createCrowd(self):
        block = self.world.CreateDynamicBody(
            position = (2, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1,2)),
                density=CHAR_DENSITY,
                restitution=0,
                friction = CHAR_FRICTION),
            userData = "crowd"
            )
        block.color = pygame.color.Color(0,0,0)
        self.shapes.append(block.fixtures[0])
        
    def initWalls(self):
        ground = self.world.CreateStaticBody(
            position = (0, 37.5),
            shapes = b2PolygonShape(box = (STAGE_WIDTH_M,1)),
            userData = "ground"
        )
        ground.color = pygame.color.Color(0,128,0)
        self.shapes.append(ground.fixtures[0])
        
        ceiling = self.world.CreateStaticBody(
            position = (0, -1),
            shapes = b2PolygonShape(box = (STAGE_WIDTH_M,1)),
            userData = "ceiling"
        )
        self.shapes.append(ceiling.fixtures[0])
        
        leftWall = self.world.CreateStaticBody(
            position = (25, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        #self.shapes.append(leftWall.fixtures[0])
        
        rightWall = self.world.CreateStaticBody(
            position = (225, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
        #self.shapes.append(rightWall.fixtures[0])
        
        goal_left = self.world.CreateStaticBody(
            position = (223, 37),
            shapes = b2PolygonShape(box = (2,8))
        )
        goal_left.fixtures[0].sensor = True
        goal_left.fixtures[0].userData = "goal left"
        self.shapes.append(goal_left.fixtures[0])
        
        goal_right = self.world.CreateStaticBody(
            position = (29, 37),
            shapes = b2PolygonShape(box = (2,8))
        )
        goal_right.fixtures[0].sensor = True
        goal_right.fixtures[0].userData = "goal right"
        self.shapes.append(goal_right.fixtures[0])
        
    # Detects if the player is off camera and draws an arrow to them
    def playerOffCamera(self):
        # A player is off camera if all 4 of their vertices don't intersect with the screen.
        SCREEN_RECT.left = self.camera.centerX_in_meters * PPM - SCREEN_WIDTH_PX / 2
        offsetX, offsetY = self.camera.getOffset_in_px()
        verts = vertices(self.player1.shapes[0])
        inside = False
        for vert in verts:
            inside = inside or SCREEN_RECT.collidepoint( (vert.x, vert.y) )
            
        if not inside:
            self.drawArrow(self.player1)
            
        verts = vertices(self.player2.shapes[0])
        inside = False
        for vert in verts:
            inside = inside or SCREEN_RECT.collidepoint( (vert.x, vert.y) )
                
        if not inside:
            self.drawArrow(self.player2)
            
    # Draw an arrow to the lost, lonely player.        
    def drawArrow(self, player):
        position = player.shapes[0].body.position
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
        
        # Murder things that need murdering
        for i, shape in enumerate(self.shapes):
            if shape.body.userData == "kill me":
                shape.body.DestroyFixture(shape)
                del self.shapes[i]
        
        for i, ef in enumerate(self.effects):
            ef.update()
            ef.draw(screen)
            if ef.done:
                del self.effects[i]
        
        self.ball.linearVelocity.x *= BALL_FRICTION
                        
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
        
        for shape in self.shapes:
            if isinstance(shape.shape, b2CircleShape):
                pos = (int(shape.body.position.x * PPM - offsetX), int(shape.body.position.y * PPM + offsetY))
                if shape.body.userData == "ball":
                    DrawCircle(pos, shape.shape.radius, self.ball.color)
                else:
                    DrawCircle(pos, shape.shape.radius, (0,0,0))
            elif hasattr(shape, "userData") and shape.userData is not None:
                if shape.userData.index("goal") == 0:
                    DrawImage(vertices_with_offset(shape, offsetX, offsetY), shape.userData)
                else:
                    DrawPolygon(vertices_with_offset(shape, offsetX, offsetY), (0,0,0))
            else:
                DrawPolygon(vertices_with_offset(shape, offsetX, offsetY), (0,0,0))        
            
        # Draw arrows if the player is off screen
        self.playerOffCamera()
    
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), True, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), True, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 2
        
        if(self.bignum == 10): screen.blit(text, (SCREEN_WIDTH_PX / 2 - 1100,0))
        else: screen.blit(text, (SCREEN_WIDTH_PX / 2 - 70,0))
        screen.blit(text_sm, (SCREEN_WIDTH_PX / 2,0))
        
        text_l = time_font_lg.render(str(self.score[0]), True, (0,0,0))
        text_r = time_font_lg.render(str(self.score[1]), True, (0,0,0))
        screen.blit(text_l, (0,0))
        screen.blit(text_r, (SCREEN_WIDTH_PX - 60,0))

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
        self.shapes.remove(self.ball.fixtures[0])
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
            userData="ball rock")
        self.shapes.append(self.ball.fixtures[0])
    
    def changeBall_revert(self):
        print "Changeball reverted"
        self.shapes.remove(self.ball.fixtures[0])
        position = self.ball.position
        self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = position,
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1.3),
                density=1,
                restitution=0.5,
                friction = 0.5),
            userData="ball")
            
        self.ball.color = pygame.color.Color(0,0,0)
        self.shapes.append(self.ball.fixtures[0])
     
    def nogravity(self):
        BALL_FRICTION = 1
        print "no gravity!"
        self.world.gravity = (0,0)
     
    def nogravity_revert(self):
        BALL_FRICTION = 0.9
        print "no gravity reverted"
        self.world.gravity = (0,25)
     
    def reversegravity(self):
        print "gravty reversed..."
        self.world.gravity = (0,-25)
     
    def slowmo(self):
        print "slow mo!"
        global TIME_STEP
        TIME_STEP /= 4
     
    def slowmo_revert(self):
        print "slow mo reverted"
        global TIME_STEP
        TIME_STEP *= 4
     
    def fastmo(self):
        print "fast mo!"
        global TIME_STEP
        TIME_STEP *= 2
     
    def fastmo_revert(self):
        print "fast mo reverted"
        global TIME_STEP
        TIME_STEP /= 2
        
    def cleanUp(self):
        while len(self.shapes) > 0:
            shape = self.shapes[0]
            self.world.DestroyBody(shape.body)
            self.shapes.remove(shape)
        
    def bombDrop(self):
        print "bomb droppin time!"
        bombs = BombDrop()
        effects.append(bombs)
        
    def bombDrop_revert(self):
        print "bomb droppin reversion!"
        # Find the bomb drop and PUT A STOP TO THE MADNESS
        for ef in effects:
            if ef.__class__.__name__ == "BombDrop":
                ef.finish()
        
    def randomEvent(self):
        randomEvents = [ [self.bombDrop, self.bombDrop_revert],
                         [self.changeBall, self.changeBall_revert],
                         [self.nogravity, self.nogravity_revert],
                         [self.slowmo, self.slowmo_revert],
                         [self.fastmo, self.fastmo_revert] ]
                         
        while len(self.modifications) > 0:
            mod = self.modifications[0]
            mod[1]()
            del self.modifications[0]
            
        event = math.floor(random.random() * len(randomEvents))
        
        # Grab the function from the list of events and run it
        mod = randomEvents[int(event)]
        mod[0]()
        self.modifications.append(mod)
            
            
class PrepareForBattle(Arena):
    def __init__(self):
        self.timeRemaining = 3000
        self.bignum = 3
        
    def draw(self, screen):
        arena.draw(screen, False)
        
        self.drawTimer(screen)
        
        text = (time_font_lg.render("PREPARE", True, (0, 70, 0)), time_font_lg.render("YOURSELF", True, (0, 70, 0)))
        screen.blit(text[0], (SCREEN_WIDTH_PX / 2 - 210,180))
        screen.blit(text[1], (SCREEN_WIDTH_PX / 2 - 220,260))
        
        
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), True, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), True, color)
        
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
