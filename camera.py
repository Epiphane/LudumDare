ARENA_WIDTH = 400
CAMERA_MAX_PAN_SPEED = 75

def DrawPolygon(vertices, color):
        """ Draw a wireframe polygon given the screen vertices with the specified color."""
        if not vertices:
            return

        if len(vertices) == 2:
            pygame.draw.aaline(screen, color, vertices[0], vertices)
        else:
            pygame.draw.polygon(screen, color, vertices, 1)

class Camera():
    def __init__(self, arena):
        self.background = Back("background")
        self.arena = arena
        self.panx = -ARENA_WIDTH * (arena - 0.5)
        self.goalx = -ARENA_WIDTH * (arena - 0.5)
        
        self.speed = 0
        
    def draw(self, screen):
        screen.blit(self.background.image, (self.panx, 0))
        
        for body in shapes:
            DrawPolygon(body.shape.vertices, pygame.Color(255, 0, 0, 255))
        
    def update(self):
        if self.speed > CAMERA_MAX_PAN_SPEED: self.speed = CAMERA_MAX_PAN_SPEED
        if self.speed < CAMERA_MAX_PAN_SPEED * -1: self.speed = CAMERA_MAX_PAN_SPEED * -1
        if self.panx > self.goalx:
            self.speed = -10
        elif self.panx < self.goalx:
            self.speed = 10
        else:
            self.stop()
            
        self.panx += self.speed
        if abs(self.panx - self.goalx) <= abs(self.speed) and self.speed != 0:
            self.stop()
            
    def stop(self):
        self.panx = self.goalx
        self.speed = 0
        
    def panCam(self, arena):
        self.goalx = -ARENA_WIDTH * (arena - 0.5)