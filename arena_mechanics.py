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
                pos = (int(shape.body.position.x * PPM + offsetX), int(shape.body.position.y * PPM + offsetY))
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
        
    def randomEvent(self):
        print "Something exciting happens!"

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
        if event.key == K_DOWN:pass
        if event.key is K_w:
            self.player1.jump()
        if event.key is K_s: pass
  
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