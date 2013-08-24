class Explosion:
    size = 5
    alpha = 255
    x = 0
    y = 0
    done = False
    def __init__(self, ex, ey):
        self.x, self.y = int(ex), int(ey)
    def draw(self, screen):
        print(self.alpha)
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