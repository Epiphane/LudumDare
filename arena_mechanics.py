def changeArena(arenaNum):
    global currentArena        # Midpoint
    global camera
    
    currentArena = arenaNum
    camera.panCam(arenaNum)
    
class Arena():
    def __init__(self):
        self.timeRemaining = 10000 # 10 seconds
        self.drawRed = 0
        self.bignum = 9
        
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
        color = (self.drawRed,0,0)
        
        text = time_font_lg.render(str(self.bignum), True, color)
        text_sm = time_font_sm.render(str(self.timeRemaining % 1000), True, color)
        
        if(self.drawRed > 0):
            self.drawRed -= 8
        
        screen.blit(text, (330,0))
        screen.blit(text_sm, (400,0))
        
    def endMinigame(self):
        if(random.random() < 0.5): return 1
        else: return 2