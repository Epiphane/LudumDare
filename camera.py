
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
        
    pygame.draw.circle(screen, color, center, int(radius*PPM))
            
class Camera():
    def __init__(self, centerX_in_meters):
        self.background = Back("background")
        self.centerX_in_meters = centerX_in_meters
        self.centerX_in_px = centerX_in_meters * PPM
        
        self.dx = 0
        self.panning = False
    
    def getOffset_in_meters(self):
        offsetX_in_meters = self.centerX_in_meters - SCREEN_WIDTH_M / 2
        offsetY_in_meters = 0
        return offsetX_in_meters, offsetY_in_meters
        
    def getOffset_in_px(self):
        offsetX_in_meters, offsetY_in_meters = self.getOffset_in_meters()
        return offsetX_in_meters * PPM, offsetY_in_meters * PPM
        
    def draw(self, screen):
        screen.blit(self.background.image, (self.panx * PPM, 0))
        
    def update(self, ball):
        if abs(ball.position.x - self.centerX_in_meters) > CAMERA_PILLOW_SPACE_M:
            self.panning = True
            if abs(self.dx) + CAMERA_SPEEDUP_SPEED <= CAMERA_MAX_PAN_SPEED:
                if ball.position.x - self.centerX_in_meters > 0:
                    self.dx += CAMERA_SPEEDUP_SPEED
                else:
                    self.dx -= CAMERA_SPEEDUP_SPEED
            
        if abs(ball.position.x - self.centerX_in_meters) <= CAMERA_MAX_PAN_SPEED_M and self.panning:
            self.dx = (ball.position.x - self.centerX_in_meters) * PPM
            
        self.centerX_in_px += self.dx
        self.centerX_in_meters = self.centerX_in_px / PPM
            
    def stop(self): pass