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
    def draw(self, screen):
        # Hoser doesn't inherently draw anything
        pass
    def update(self):
        # Failsafe against crashing the game w/ too many water molecules
        if len(self.waterMols) < 50:
            # Spawn a new water molecule at the front end of the hosehead
            # Use the midpoint between two vertices of the hosehead as a position
            hoseheadEdge = ((vertices(self.hosehead)[1][0] + vertices(self.hosehead)[2][0])/(2 * PPM),
                            (vertices(self.hosehead)[1][1] + vertices(self.hosehead)[2][1])/(2 * PPM))
            newWaterMol = world.CreateDynamicBody(
                position=hoseheadEdge,
                fixtures = b2FixtureDef(density = 1.0, shape = b2PolygonShape(
                    box=(0.2, 0.2))))
            newWaterMol.linearVelocity.x = 20
            print newWaterMol.position
            self.waterMols.append(newWaterMol.fixtures[0])
            arena.shapes.append(newWaterMol.fixtures[0])
        if len(self.hosehead.body.fixtures) == 0:
            done = True
            
            