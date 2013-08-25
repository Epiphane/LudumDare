class BombDrop():
    done = False
    bombCooldown = 20
    bombs = []
    def draw(self, screen):
        # Draw the bombas
        for i,bomb in enumerate(self.bombs):
            rotAngle = bomb.body.angle
            offsetX, offsetY = arena.camera.getOffset_in_px()
            verts = vertices_with_offset(bomb, offsetX, offsetY)
            # The "vertices" method will return a rotated square of vertices.
            # As it turns out, if we grab the leftmost, topmost, rightmost and
            # bottommost values from these vertices, we end up with the right
            # bounding box for pygame to draw the image. Huh.
            xvals = [ x[0] for x in verts ]
            yvals = [ y[1] for y in verts ]
            left = min(xvals)
            right = max(xvals)
            top = min(yvals)
            bottom = max(yvals)
            finalRect = pygame.Rect(left, top, (right - left), (bottom - top))
            imgRot = pygame.Surface.convert_alpha(pygame.transform.rotate(images["bomb"][0], rotAngle))
            screen.blit(imgRot, finalRect)
            if bomb.body.userData == "kill me":
                bomb.body.DestroyFixture(bomb)
                del self.bombs[i]
            
    def update(self):
        # Iterate the cooldown on bombs. If it's been long enough, drop another one!
        self.bombCooldown -= 1
        if self.bombCooldown <= 0:
            self.bombCooldown = 20
            # drop da bomb
            # Choose a random spot between 0 -> Stage Width meters
            bombX = int(random.random() * STAGE_WIDTH_M)
            # Choose a random spot in the upper half of the map to drop the bomb
            bombY = int(random.random() * SCREEN_HEIGHT_M/2 + SCREEN_HEIGHT_M)
            
            newBomb = arena.world.CreateDynamicBody(
                userData = "bomb",
                position = (bombX, 10),
                fixtures = b2FixtureDef(density = 5.0, shape = b2PolygonShape(box = (1,1)),
                    isSensor = True))
                    
            # Start with a li'l spin
            newBomb.angularVelocity = 2 - random.random() * 4
            
            self.bombs.append(newBomb.fixtures[0])
            
    def finish(self):
        self.done = True
        bombs = []

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
        s = pygame.Surface((SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX), HWSURFACE)
        s.set_alpha(self.alpha)
        s.set_colorkey(pygame.Color(0, 0, 0))
        pygame.draw.circle(s, pygame.Color(237, 211, 17),
                            (self.x, self.y), self.size)
        
        screen.blit(s, (0,0))
    def update(self):
        self.size += 6
        self.alpha -= 15
        if self.alpha <= 0:
            self.done = True
            