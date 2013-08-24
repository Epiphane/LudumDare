def changeArena(arenaNum):
    global currentArena        # Midpoint
    global camera
    
    currentArena = arenaNum
    camera.panCam(arenaNum)
    
class Arena():
    def __init__(self):
        self.timeRemaining = 5000 # 10 seconds
        self.drawRed = 0
        self.bignum = 10
        self.shapes = []
        
        self.paused = True
        
    def startGame(self, arena):
        self.paused = False
        self.initGame((ARENA_WIDTH * (arena - 0.5)) / PPM, (ARENA_WIDTH * (arena + 1.5)) / PPM)
        
    def initGame(self, minx, maxx): pass
        
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
        
class PrepareForBattle(Arena):
    def __init__(self, arena):
        self.timeRemaining = 3000
        self.bignum = 3
        
    def draw(self, screen):
        self.drawTimer(screen)
        
        text = (time_font_lg.render("PREPARE", True, (0, 30, 0)), time_font_lg.render("YOURSELF", True, (0, 30, 0)))
        screen.blit(text[0], (190,180))
        screen.blit(text[1], (180,260))
        
    def endMinigame(self):
        return -1
        
class SoccerArena(Arena):
    def initGame(self, minx, maxx):
        body = world.CreateDynamicBody(position = ((minx + maxx) / 2,24),
            fixtures = b2FixtureDef(
                shape = b2CircleShape(radius=1),
                density=5,
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
