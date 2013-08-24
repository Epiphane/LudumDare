class Explosion:
    size = 5
    alpha = 255
    x = 0
    y = 0
    done = False
    def __init__(self, ex, ey):
        self.x, self.y = int(ex), int(ey)
    def draw(self, screen):
        # Transparency sucks. Make a new surface then draw the splosion onto it,
        # then draw that new surface on to the old surface.
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE)
        s.set_alpha(self.alpha)
        s.set_colorkey(pygame.Color(0, 0, 0))
        pygame.draw.circle(s, pygame.Color(237, 211, 17),
                            (self.x,self.y), self.size)
        screen.blit(s, (0,0))
    def update(self):
        self.size += 6
        self.alpha -= 15
        if self.alpha <= 0:
            self.done = True
            
class Hoser:
    waterMols = []
    hosehead = None
    done = False
    def __init__(self, hosehead):
        self.hosehead = hosehead
        self.other = 0
    def draw(self, screen):
        for shapeToDraw in self.waterMols:
            DrawCircle(shapeToDraw.body.position, shapeToDraw.shape.radius, pygame.Color(0, 0, 0, 255))
        pass
    def update(self):
        # Failsafe against crashing the game w/ too many water molecules
        if self.hosehead.shape is None:
            done = True
            return
            
        #if self.other > 0:
        #    self.other -= 1
        #    return
        #self.other = 3
        
        # Spawn a new water molecule at the front end of the hosehead
        # Use the midpoint between two vertices of the hosehead as a position
        olds = self.hosehead.shape.vertices
        # Convert them (with magic) using the body.transform thing
        vertices = [(self.hosehead.body.transform*v) for v in olds]
        
        hoseheadEdge = ((vertices[1][0] + vertices[2][0])/2,
                        (vertices[1][1] + vertices[2][1])/2)
                        
        slope = -1 * (vertices[2][0] - vertices[1][0]) / (vertices[1][1] - vertices[2][1])
        newWaterMol = world.CreateDynamicBody(
            userData="WADAH",
            position=hoseheadEdge,
            fixtures = b2FixtureDef(density = 5, shape = b2CircleShape(
                radius=0.2)))
                
        speed = random.random() * 1600
        newWaterMol.linearVelocity.x = math.sqrt(speed / (slope*slope+1))
        newWaterMol.linearVelocity.y = -1 * math.sqrt(speed + 20 - newWaterMol.linearVelocity.x*newWaterMol.linearVelocity.x)
        self.waterMols.append(newWaterMol.fixtures[0])
        
        if len(self.waterMols) > 80:
            self.waterMols[0].body.DestroyFixture(self.waterMols[0])
            self.waterMols.remove(self.waterMols[0])
            
            