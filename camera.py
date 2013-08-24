ARENA_WIDTH = 400
CAMERA_MAX_PAN_SPEED = 75

def DrawPolygon(vertices, color = (0,0,0)):
    """ Draw a wireframe polygon given the screen vertices with the specified color."""
    if not vertices:
        return

    if len(vertices) == 2:
        pygame.draw.aaline(screen, color, vertices[0], vertices)
    else:
        pygame.draw.polygon(screen, color, vertices, 1)

def DrawCircle(center, radius, color = (0,0,0)):
    """ Draw a wireframe polygon given the screen vertices with the specified color."""
    if not center or not radius:
        return

    pygame.draw.circle(screen, color, (int((center.x + camera.panx) * PPM), int(center.y * PPM)), int(radius*PPM))
            
class Camera():
    def __init__(self, arena):
        self.background = Back("background")
        self.arena = arena
        self.panx = (-ARENA_WIDTH * (arena - 0.5)) / PPM
        self.goalx = (-ARENA_WIDTH * (arena - 0.5)) / PPM
        
        self.speed = 0
        self.stopped = True
        
    def draw(self, screen):
        screen.blit(self.background.image, (self.panx * PPM, 0))
        
        for shapeToDraw in player1.shapes:
            if type(shapeToDraw.shape) is b2PolygonShape:
                DrawPolygon(vertices(shapeToDraw), player1.color)
            elif type(shapeToDraw.shape) is b2CircleShape:
                DrawCircle(shapeToDraw.body.position, shapeToDraw.shape.radius, player1.color)
        
        for shapeToDraw in player2.shapes:
            if type(shapeToDraw.shape) is b2PolygonShape:
                DrawPolygon(vertices(shapeToDraw), player2.color)
            elif type(shapeToDraw.shape) is b2CircleShape:
                DrawCircle(shapeToDraw.body.position, shapeToDraw.shape.radius, player2.color)
        
        for shapeToDraw in shapes:
            if type(shapeToDraw.shape) is b2PolygonShape:
                DrawPolygon(vertices(shapeToDraw), pygame.Color(0, 0, 0, 255))
            elif type(shapeToDraw.shape) is b2CircleShape:
                DrawCircle(shapeToDraw.body.position, shapeToDraw.shape.radius, pygame.Color(0, 0, 0, 255))
        
        for shapeToDraw in arena.shapes:
            if type(shapeToDraw.shape) is b2PolygonShape:
                DrawPolygon(vertices(shapeToDraw), pygame.Color(0, 0, 0, 255))
            elif type(shapeToDraw.shape) is b2CircleShape:
                DrawCircle(shapeToDraw.body.position, shapeToDraw.shape.radius, pygame.Color(0, 0, 0, 255))
        
    def update(self):
        if self.panx > self.goalx:
            self.speed = -0.5
            self.stopped = False
        elif self.panx < self.goalx:
            self.speed = 0.5
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
        if arena.paused: 
            arena.startGame(currentArena)
        
    def panCam(self, arena):
        self.goalx = (-ARENA_WIDTH * (arena - 0.5)) / PPM