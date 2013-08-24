ARENA_WIDTH = 400
CAMERA_MAX_PAN_SPEED = 75
class Camera():
    def __init__(self, arena):
        self.background = Back("background")
        self.arena = arena
        self.panx = -ARENA_WIDTH * (arena - 0.5)
        self.goalx = -ARENA_WIDTH * (arena - 0.5)
        
        self.speed = 0
        self.stopped = True
        
    def draw(self, screen):
        screen.blit(self.background.image, (self.panx, 0))
        
    def update(self):
        if self.speed > CAMERA_MAX_PAN_SPEED: self.speed = CAMERA_MAX_PAN_SPEED
        if self.speed < CAMERA_MAX_PAN_SPEED * -1: self.speed = CAMERA_MAX_PAN_SPEED * -1
        if self.panx > self.goalx:
            self.speed = -20
            self.stopped = False
        elif self.panx < self.goalx:
            self.speed = 20
            self.stopped = False
        else:
            self.stop()
            
        self.panx += self.speed
        if abs(self.panx - self.goalx) <= abs(self.speed) and self.speed != 0:
            self.stop()
            
    def stop(self):
        self.panx = self.goalx
        self.speed = 0
        self.stopped = True
        
    def panCam(self, arena):
        self.goalx = -ARENA_WIDTH * (arena - 0.5)