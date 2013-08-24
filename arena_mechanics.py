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
        
        self.paused = True
        
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
        for shape in self.shapes:
            shape.body.DestroyFixture(shape)
            #world.DestroyBody(shape.body)
    
        player1.destroy()
        player2.destroy()
        if(random.random() < 0.5): return 1
        else: return 1
        
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
            
class GardenArena(Arena):
        
    def startGame(self, arena):
        self.paused = False
        player1.createGardener(currentArena - 0.5, (255,0,0))
        player2.createPlanter(currentArena + 0.5, (0,0,255))
        self.initGame((ARENA_WIDTH * (arena - 0.5)) / PPM, (ARENA_WIDTH * (arena + 1.5)) / PPM)

    def doAction(self, event):
        if event.key is K_a:
            player1.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key is K_d:
            player1.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_LEFT:
            player2.input["left"] = (event.type is pygame.KEYDOWN)
        if event.key == K_RIGHT:
            player2.input["right"] = (event.type is pygame.KEYDOWN)
        if event.key == K_UP: pass
        if event.key == K_DOWN:pass
        if event.key is K_w and event.type is pygame.KEYDOWN:
            player2.growPlant()
            #player1.aimUp()
        if event.key is K_s:
            player2.growPlant()
            #player1.aimDown()
