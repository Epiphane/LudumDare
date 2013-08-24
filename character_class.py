class Player(pygame.sprite.Sprite):
    def __init__(self, direction, arena):
        self.inputs = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.arena = arena
    
    