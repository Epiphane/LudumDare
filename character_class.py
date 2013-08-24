class Player(pygame.sprite.Sprite):
    def __init__(self, direction, arena, color):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.arena = arena
        self.shapes = []
        
        self.color = color
    
        body = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 30))
        box = body.CreatePolygonFixture(box = (1,2), density = 10, friction = 0.3)
        self.shapes.append(box)
        
        arm1 = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM - 0.5, 31))
        box = arm1.CreatePolygonFixture(box = (.2,.5), density = 4, friction = 0.3)
        self.shapes.append(box)
        
        arm2 = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM + 0.5, 31))
        box = arm2.CreatePolygonFixture(box = (.2,.5), density = 4, friction = 0.3)
        self.shapes.append(box)
        
        #head = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 27),
        #    fixtures = b2FixtureDef(
        #        shape = b2CircleShape(radius=1),
        #        density=1,
        #        restitution=0),
        #        )
        # 
        #self.shapes.append(head.fixtures[0])
        
        #self.shapes.append(box)
        
        world.CreateDistanceJoint(bodyA=body, bodyB=arm1, anchorA=b2Vec2(body.worldCenter.x, body.worldCenter.y - 0.5), anchorB = arm1.worldCenter, collideConnected=True)
        world.CreateDistanceJoint(bodyA=body, bodyB=arm2, anchorA=b2Vec2(body.worldCenter.x, body.worldCenter.y - 0.5), anchorB = arm2.worldCenter, collideConnected=True)
    
    def update(self):
        self.shapes[0].body.awake = True
        self.shapes[0].body.linearVelocity.x = 0
        if self.input["left"]:
            self.shapes[0].body.linearVelocity.x -= 7
        if self.input["right"]:
            self.shapes[0].body.linearVelocity.x += 7
    
    def destroy(self): pass