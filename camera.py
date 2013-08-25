
def DrawPolygon(vertices, color = (0,0,0), color_2 = None):
    """ Draw a wireframe polygon given the screen vertices with the specified color."""
    if not vertices:
        print("no vertices, brotha")
        return
        

    if len(vertices) == 2:
        pygame.draw.aaline(screen, color, vertices[0], vertices)
    else:
        if color_2 is not None:
            pygame.draw.polygon(screen, color_2, vertices, 0)
        pygame.draw.polygon(screen, color, vertices, 2)

def DrawCircle(center, radius, color = (0,0,0)):
    """ Draw a wireframe polygon given the screen vertices with the specified color."""
    if not center or not radius:
        return
        
    pygame.draw.circle(screen, color, center, int(radius*PPM))
            
def DrawImage(vertices, userData):
    screen.blit(images[userData][0], (vertices[0], vertices[1]))
           
class Camera():
    def __init__(self, centerX_in_meters):
        self.background = Back("background")
        self.centerX_in_meters = centerX_in_meters
        self.centerX_in_px = centerX_in_meters * PPM
        
        self.dx = 0
    
    def getOffset_in_meters(self):
        offsetX_in_meters = self.centerX_in_meters - SCREEN_WIDTH_M / 2
        offsetY_in_meters = 0
        return offsetX_in_meters, offsetY_in_meters
        
    def getOffset_in_px(self):
        offsetX_in_meters, offsetY_in_meters = self.getOffset_in_meters()
        return offsetX_in_meters * PPM, offsetY_in_meters * PPM
        
    def draw(self, screen):
        offsetX_in_meters = self.centerX_in_meters - SCREEN_WIDTH_M / 2
        screen.blit(self.background.image, (-1 * offsetX_in_meters * PPM - 200, 0))
        
    def update(self, ball):
        if abs(ball.position.x - self.centerX_in_meters) > CAMERA_PILLOW_SPACE_M:
            if abs(self.dx) + CAMERA_SPEEDUP_SPEED <= CAMERA_MAX_PAN_SPEED_PX:
                if ball.position.x - self.centerX_in_meters > 0:
                    self.dx += CAMERA_SPEEDUP_SPEED
                else:
                    self.dx -= CAMERA_SPEEDUP_SPEED
            
        if abs(ball.position.x - self.centerX_in_meters) <= CAMERA_MAX_PAN_SPEED_M:
            self.dx = (ball.position.x - self.centerX_in_meters) * PPM
            
        self.centerX_in_px += self.dx
        self.centerX_in_meters = self.centerX_in_px / PPM
        
        if self.centerX_in_meters < SCREEN_WIDTH_M / 2:
            self.dx = 0
            self.centerX_in_meters = SCREEN_WIDTH_M / 2
            self.centerX_in_px = self.centerX_in_meters * PPM
        if self.centerX_in_meters > STAGE_WIDTH_M - SCREEN_WIDTH_M / 2:
            self.dx = 0
            self.centerX_in_meters = STAGE_WIDTH_M - SCREEN_WIDTH_M / 2
            self.centerX_in_px = self.centerX_in_meters * PPM
            
    def stop(self): pass