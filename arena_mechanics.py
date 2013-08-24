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
        
        self.camera = Camera(STAGE_WIDTH_M / 2)
        
        self.player1 = Player(1, STAGE_WIDTH_M / 2 - SCREEN_WIDTH_M / 4, (255,0,0))
        self.player2 = Player(-1, STAGE_WIDTH_M / 2 + SCREEN_WIDTH_M / 4, (0,0,255))
        
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
        # Reset forces for the next frame
        self.world.ClearForces()
                        
        # Update a "tick" in physics land
        self.world.Step(TIME_STEP*1.5, 10, 10)
        
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
                
    def draw(self, screen):
        self.drawTimer(screen)
    
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), True, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), True, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 8
        
        if(self.bignum == 10): screen.blit(text, (290,0))
        else: screen.blit(text, (330,0))
        screen.blit(text_sm, (400,0))
        
    
class Arena2():
        
    def startGame(self, arena):
        self.paused = False
        player1.create(currentArena - 0.5, (255,0,0))
        player2.create(currentArena + 0.5, (0,0,255))
        self.initGame((ARENA_WIDTH * (arena - 0.5)) / PPM, (ARENA_WIDTH * (arena + 1.5)) / PPM)
        
    def initGame(self, minx, maxx):
        wall1 = world.CreateStaticBody(
            position = (minx, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        
        self.shapes.append(wall1.fixtures[0])
        
        wall2 = world.CreateStaticBody(
            position = (maxx, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
            
        self.shapes.append(wall2.fixtures[0])
        
    def update(self, dt):
        if not camera.stopped: return False
    
        self.timeRemaining -= dt
        oldbignum = self.bignum
        self.bignum = math.trunc(self.timeRemaining / 1000)
        if self.bignum != oldbignum and self.bignum < 4: self.drawRed = 128
        
        if(self.timeRemaining <= 0):
            return self.endMinigame()
        elif self.timeRemaining <= 6000:
            if self.lost or self.won:
                return self.endMinigame()
        return False
        
    def draw(self, screen):
        self.drawTimer(screen)
    
    def drawTimer(self, screen):
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), True, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), True, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 8
        
        if(self.bignum == 10): screen.blit(text, (290,0))
        else: screen.blit(text, (330,0))
        screen.blit(text_sm, (400,0))
        
    def endMinigame(self):
        self.paused = True
        print "ending"
        while len(self.shapes) > 0:
            shape = self.shapes[0]
            world.DestroyBody(shape.body)
            arena.shapes.remove(shape)
            print "destroyed a.shape -> ", len(arena.shapes),"left"
            
        print "Over"
        if self.lost:
            self.lost = False
            return 2
        if self.won:
            self.won = False
            return 1
    
        player1.destroy()
        player2.destroy()
        return 1
        
    def doAction(self, event):
        if event.key is K_a:
            player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP:
            player2.jump()
        if event.key is K_w:
            player1.jump()
            
    def loseMinigame(self):
        if self.timeRemaining >= 8000: return
        self.lost = True
            
    def wonMinigame(self):
        if self.timeRemaining >= 8000: return
        self.won = True
        
class SoccerArena(Arena):
    def initGame(self, minx, maxx):
    
        body = world.CreateDynamicBody(position = ((minx + maxx) / 2,24),
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1),
                density=1,
                restitution=0.5),
            userData="soccer ball")
        
        self.shapes.append(body.fixtures[0])
        
        wall1 = world.CreateStaticBody(
            position = (minx, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "left wall"
        )
        
        self.shapes.append(wall1.fixtures[0])
        
        wall2 = world.CreateStaticBody(
            position = (maxx, 0),
            shapes = b2PolygonShape(box = (1,37.5)),
            userData = "right wall"
        )
        
        self.shapes.append(wall2.fixtures[0])
        self.ball = body
        
        goal = world.CreateStaticBody(
            position = (maxx + 2, 45),
            shapes = b2PolygonShape(box = (12.5,18)),
            userData = "goal"
        )
        
        goal.fixtures[0].sensor = True
        
        self.shapes.append(goal.fixtures[0])

    def doAction(self, event):
        if event.key is K_a:
            player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP:
            player2.jump()
        if event.key == K_DOWN:pass
            #player2.kick(1)
        if event.key is K_w:
            player1.jump()
        if event.key is K_s: pass
            #player1.kick(-1)
            
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