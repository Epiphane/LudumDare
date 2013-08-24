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
        self.startGame(STAGE_WIDTH_M / 2)
        
        self.camera = Camera(STAGE_WIDTH_M / 2)
        
        self.player1 = Player(1, STAGE_WIDTH_M / 2 - SCREEN_WIDTH_M / 4, (255,0,0), self)
        self.player2 = Player(-1, STAGE_WIDTH_M / 2 + SCREEN_WIDTH_M / 4, (0,0,255), self)
        
    def initWalls(self):
        ground = self.world.CreateStaticBody(
            position = (200, 37.5),
            shapes = b2PolygonShape(box = (800,1)),
            userData = "ground"
        )
        self.shapes.append(ground.fixtures[0])
        
        ceiling = self.world.CreateStaticBody(
            position = (200, -15),
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
        
    def update(self, dt):
        self.timeRemaining -= dt
        oldbignum = self.bignum
        self.bignum = math.trunc(self.timeRemaining / 1000)
        if self.bignum != oldbignum and self.bignum < 4: self.drawRed = 128
        if(self.timeRemaining <= 0):
            self.randomEvent()
            self.timeRemaining = 10000
            
        self.player1.update()
        self.player2.update()
        
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
            self.player2.jump()
        if event.key is K_w:
            self.player1.jump()
        if event.key is K_s and self.player1.input["right"]:
            self.player1.slideTackle("r")
        if event.key is K_s and self.player1.input["left"]:
            self.player1.slideTackle("l")
        if event.key == K_DOWN and self.player2.input["right"]:
            self.player2.slideTackle("r")
        if event.key == K_DOWN and self.player2.input["left"]:
            self.player2.slideTackle("l")
            
    def startGame(self, middle_x):
        self.ball = self.world.CreateDynamicBody(position = (middle_x,27),
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1),
                density=1,
                restitution=0.5),
            userData="soccer ball")
        
        self.shapes.append(self.ball.fixtures[0])
        
        #goal = world.CreateStaticBody(
        #    position = (maxx + 2, 45),
        #    shapes = b2PolygonShape(box = (12.5,18)),
        #    userData = "goal"
        #)
        
        #goal.fixtures[0].sensor = True
        
        #self.shapes.append(goal.fixtures[0])
  
        #while len(self.shapes) > 0:
         #   shape = self.shapes[0]
        #    world.DestroyBody(shape.body)
        #    arena.shapes.remove(shape)
 
    
        #player1.destroy()
        #player2.destroy()
        
    def randomEvent(self):
        while len(self.modifications) > 0:
            mod = self.modifications[0]
            if(mod == "changeBall"): self.changeBall_revert()
            del self.modifications[0]
        event = math.floor(random.random())
        
        if(event == 0):
            self.changeBall()
            self.modifications.append("changeBall")
        
    def changeBall(self):
        self.oldBall = self.ball
        self.shapes.remove(self.ball.fixtures[0])
        self.ball = self.world.CreateDynamicBody(position = self.ball.position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(vertices=[(-1+random.random(),-1+random.random()),(-1+random.random(),0.25+random.random()),(-0.5+random.random(),0.25+random.random()),(-0.5+random.random(),1+random.random()),(0.5+random.random(),0.5+random.random()),(1+random.random(),0.2+random.random()),(0+random.random(),0.5+random.random())]),
                density=1,
                restitution=0.5),
            userData="soccer ball")
        self.shapes.append(self.ball.fixtures[0])
    
    def changeBall_revert(self):
        self.shapes.remove(self.ball.fixtures[0])
        self.oldBall.position = self.ball.position
        self.ball = self.oldBall
        self.shapes.append(self.ball.fixtures[0])
        
            
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