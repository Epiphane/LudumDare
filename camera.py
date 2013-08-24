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
    def __init__(self, centerX_in_meters):
        self.background = Back("background")
        self.centerX_in_meters = centerX_in_meters
        self.centerX_in_px = centerX_in_meters * PPM
        
        self.speed = 0
        self.delay = 0
        self.stopped = True
    
    def getOffset_in_meters(self):
        offsetX_in_meters = self.centerX_in_meters - SCREEN_WIDTH_M / 2
        offsetY_in_meters = 0
        return offsetX_in_meters, offsetY_in_meters
        
    def getOffset_in_px(self):
        offsetX_in_meters, offsetY_in_meters = self.getOffset_in_meters()
        return offsetX_in_meters * PPM, offsetY_in_meters * PPM
        
    def draw(self, screen):
        screen.blit(self.background.image, (self.panx * PPM, 0))
        
        if player1.display:
            for shapeToDraw in player1.shapes:
                if type(shapeToDraw.shape) is b2PolygonShape:
                    DrawPolygon(vertices(shapeToDraw), player1.color)
                elif type(shapeToDraw.shape) is b2CircleShape:
                    DrawCircle(shapeToDraw.body.position, shapeToDraw.shape.radius, player1.color)
        
        if player2.display:
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
            # Eventually, we could tell it to load "userData.png," if we're
            # planning to have an image for every body, and store the 
            # filename for the image in userData. In the meantime, just check
            # for the guys that we DO have images predefined for
            if not hasattr(shapeToDraw.body, 'userData'): continue
            if shapeToDraw.body.userData == "goal":
                screen.blit(images["goal"][0],vertices(shapeToDraw)[0])
            if type(shapeToDraw.shape) is b2PolygonShape:
                DrawPolygon(vertices(shapeToDraw), pygame.Color(0, 0, 0, 255))
            elif type(shapeToDraw.shape) is b2CircleShape:
                DrawCircle(shapeToDraw.body.position, shapeToDraw.shape.radius, pygame.Color(0, 0, 0, 255))
            
        
    def update(self, dt):
        if self.panx > self.goalx:
            self.speed = -0.5
            self.stopped = False
        elif self.panx < self.goalx:
            self.speed = 0.5
            self.stopped = False
        else:
            self.stop(dt)
            
        self.panx += self.speed
        if abs(self.panx - self.goalx) <= abs(self.speed) and self.speed != 0:
            self.stop(dt)
            
    def stop(self, dt):
        self.panx = self.goalx
        self.speed = 0
        if self.delay > 0:
            self.delay -= dt
        else:
            self.stopped = True
            if arena.paused: 
                arena.startGame(currentArena)
        
    def panCam(self, arena):
        self.goalx = (-ARENA_WIDTH * (arena - 0.5)) / PPM