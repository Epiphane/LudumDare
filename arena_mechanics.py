def changeArena(arenaNum):
    global currentArena        # Midpoint
    global camera
    
    currentArena = arenaNum
    camera.panCam(arenaNum)
    camera.delay = 200

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
        self.world = b2World(gravity=(0, 25), doSleep = True)
        
        # Initialize the contact handler
        self.world.contactListener = ContactHandler()
        
        self.initWalls()
        self.ball = None
        self.startGame(STAGE_WIDTH_M / 2)
        
        self.camera = Camera(STAGE_WIDTH_M / 2)
        
        self.score = [0,0]
        
        self.toInit = False
  
    def startGame(self, middle_x, delay=0):
        self.toInit = False
        
        if hasattr(self,'player2'):
            self.player1.materialize(middle_x - SCREEN_WIDTH_M / 4, self)
            self.player2.materialize(middle_x + SCREEN_WIDTH_M / 4, self)
        else:
            self.player1 = Player(1, middle_x - SCREEN_WIDTH_M / 4, (255,0,0), self)
            self.player2 = Player(-1, middle_x + SCREEN_WIDTH_M / 4, (0,0,255), self)
        
        if self.ball is not None: self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = (middle_x,27),
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1),
                density=10,
                restitution=0.5,
                friction = 0.5),
            userData="ball")
        
        self.shapes.append(self.ball.fixtures[0])
        
    def initWalls(self):
        ground = self.world.CreateStaticBody(
            position = (200, 37.5),
            shapes = b2PolygonShape(box = (800,1)),
            userData = "ground"
        )
        self.shapes.append(ground.fixtures[0])
        
        ceiling = self.world.CreateStaticBody(
            position = (200, -1),
            shapes = b2PolygonShape(box = (800,1)),
            userData = "ceiling"
        )
        self.shapes.append(ceiling.fixtures[0])
        
        leftWall = self.world.CreateStaticBody(
            position = (0, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        self.shapes.append(leftWall.fixtures[0])
        
        rightWall = self.world.CreateStaticBody(
            position = (200, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
        self.shapes.append(rightWall.fixtures[0])
        
        goal_left = self.world.CreateStaticBody(
            position = (200, 37),
            shapes = b2PolygonShape(box = (5,8))
        )
        goal_left.fixtures[0].sensor = True
        goal_left.fixtures[0].userData = "goal left"
        self.shapes.append(goal_left.fixtures[0])
        
        goal_right = self.world.CreateStaticBody(
            position = (6, 37),
            shapes = b2PolygonShape(box = (5,8))
        )
        goal_right.fixtures[0].sensor = True
        goal_right.fixtures[0].userData = "goal right"
        self.shapes.append(goal_right.fixtures[0])
        
    def update(self, dt):
        if self.toInit is not False: self.startGame(self.toInit[0], self.toInit[1])
    
        self.timeRemaining -= dt
        oldbignum = self.bignum
        self.bignum = math.trunc(self.timeRemaining / 1000)
        if self.bignum != oldbignum and self.bignum < 4: self.drawRed = 128
        if(self.timeRemaining <= 0):
            self.randomEvent()
            self.timeRemaining = 10000
            
        self.player1.update(self.world.gravity == (0,0))
        self.player2.update(self.world.gravity == (0,0))
        
        self.camera.update(self.ball)
        
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
                        
        # Update a "tick" in physics land
        self.world.Step(TIME_STEP*2, 10, 10)
        
        # Reset forces for the next frame
        self.world.ClearForces()
                
    def draw(self, screen):
        self.drawTimer(screen)
        
        offsetX, offsetY = self.camera.getOffset_in_px()
        self.player1.draw(screen, offsetX, offsetY)
        self.player2.draw(screen, offsetX, offsetY)
        
        for shape in self.shapes:
            if isinstance(shape.shape, b2CircleShape):
                pos = (int(shape.body.position.x * PPM - offsetX), int(shape.body.position.y * PPM + offsetY))
                DrawCircle(pos, shape.shape.radius, (0,0,0))
            elif hasattr(shape, "userData") and shape.userData is not None:
                if shape.userData.index("goal") == 0:
                    DrawImage(vertices_with_offset(shape, offsetX, offsetY), shape.userData)
                else:
                    DrawPolygon(vertices_with_offset(shape, offsetX, offsetY), (0,0,0))
            else:
                DrawPolygon(vertices_with_offset(shape, offsetX, offsetY), (0,0,0))
                
    
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), True, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), True, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 2
        
        if(self.bignum == 10): screen.blit(text, (290,0))
        else: screen.blit(text, (330,0))
        screen.blit(text_sm, (400,0))
        
        text_l = time_font_lg.render(str(self.score[0]), True, (0,0,0))
        text_r = time_font_lg.render(str(self.score[1]), True, (0,0,0))
        screen.blit(text_l, (0,0))
        screen.blit(text_r, (740,0))

    def doAction(self, event):
        if event.key is K_a:
            self.player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            self.player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            self.player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            self.player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP:]
            self.player2.input["up"] = (event.type is pygame.KEYDOWN)
            self.player2.jump(self.world.gravity)
        if event.key == K_DOWN:
            self.player2.input["down"] = (event.type is pygame.KEYDOWN)
        if event.key is K_w:
            self.player1.input["up"] = (event.type is pygame.KEYDOWN)
            self.player1.jump(self.world.gravity)
        if event.key is K_s:
            self.player1.input["down"] = (event.type is pygame.KEYDOWN)
        
    def randomEvent(self):
        while len(self.modifications) > 0:
            mod = self.modifications[0]
            if(mod == "changeBall"): self.changeBall_revert()
            elif(mod == "nogravity"): self.nogravity_revert()
            elif(mod == "slowmo"): self.slowmo_revert()
            del self.modifications[0]
            
        event = math.floor(random.random() * 4)
        
        if(event == 0):
            self.changeBall()
            self.modifications.append("changeBall")
        elif(event == 1):
            self.nogravity()
            self.modifications.append("nogravity")
        elif(event == 2):
            self.slowmo()
            self.modifications.append("slowmo")
        elif(event == 3):
            self.fastmo()
            self.modifications.append("fastmo")
        
    def changeBall(self):
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
                density=1,
                restitution=0.5,
                friction = 0.5),
            userData="ball")
        self.shapes.append(self.ball.fixtures[0])
    
    def changeBall_revert(self):
        self.shapes.remove(self.ball.fixtures[0])
        position = self.ball.position
        self.world.DestroyBody(self.ball)
        
        self.ball = self.world.CreateDynamicBody(position = position,
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1),
                density=10,
                restitution=0.5,
                friction = 0.5),
            userData="ball")
            
        self.shapes.append(self.ball.fixtures[0])
     
    def nogravity(self):
        self.world.gravity = (0,0)
     
    def nogravity_revert(self):
        self.world.gravity = (0,25)
     
    def reversegravity(self):
        self.world.gravity = (0,-25)
     
    def slowmo(self):
        global TIME_STEP
        TIME_STEP /= 4
     
    def slowmo_revert(self):
        global TIME_STEP
        TIME_STEP *= 4
     
    def fastmo(self):
        global TIME_STEP
        TIME_STEP *= 4
     
    def fastmo_revert(self):
        global TIME_STEP
        TIME_STEP /= 4
        
    def cleanUp(self):
        while len(self.shapes) > 0:
            shape = self.shapes[0]
            aelf.world.DestroyBody(shape.body)
            self.shapes.remove(shape)
        
    def bombDrop(self):
        bombs = BombDrop()
        effects.append(bombs)
        
    def bombDrop_revert(self):
        # Find the bomb drop and PUT A STOP TO THE MADNESS
        for ef in effects:
            if ef.__class__.__name__ == "BombDrop":
                ef.finish()
        
    def randomEvent(self):
        randomEvents = [ [self.bombDrop, self.bombDrop_revert] ]
        
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
    def initGame(self, minx, maxx):
        self.timeRemaining = 3000
        self.bignum = 3
        
    def startGame(self, arena):
        self.paused = False
        player1.display = False
        player2.display = False
        self.initGame((ARENA_WIDTH * (arena - 0.5)) / PPM, (ARENA_WIDTH * (arena + 1.5)) / PPM)
        
    def draw(self, screen):
        self.drawTimer(screen)
        
        text = (time_font_lg.render("PREPARE", True, (0, 70, 0)), time_font_lg.render("YOURSELF", True, (0, 70, 0)))
        screen.blit(text[0], (190,180))
        screen.blit(text[1], (180,260))
        
    def endMinigame(self):
        changePlayers = False
        return -1