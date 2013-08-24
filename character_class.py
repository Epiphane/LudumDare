class Player(pygame.sprite.Sprite):
    def __init__(self, direction, arena, color):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.create(arena, color)
    
    def update(self):
        self.shapes[0].body.awake = True
        self.shapes[0].body.linearVelocity.x = 0
        if self.input["left"]:
            self.shapes[0].body.linearVelocity.x -= 7
        if self.input["right"]:
            self.shapes[0].body.linearVelocity.x += 7
    
    def destroy(self):
        destructionShapes = []
        for i in range(1,5):
            # Grab the old vertices from the shape
            olds = self.shapes[i].shape.vertices
            # Convert them (with magic) using the body.transform thing
            result = [(self.shapes[i].body.transform*v) for v in olds]
            for v in result:
                body = world.CreateDynamicBody(position = v)
                shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                destructionShapes.append(shape)
                
        # Grab the old vertices from the shape
        olds = self.shapes[0].shape.vertices
        for i in range(10):
            # Convert them (with magic) using the body.transform thing
            result = [(self.shapes[0].body.transform*v) for v in olds]
            for v in result:
                body = world.CreateDynamicBody(position = (v.x + random.random()*4 - 2, v.y + random.random()*4-2))
                shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                destructionShapes.append(shape)
                
        for shape in self.shapes:
            shape.body.DestroyFixture(shape)
        self.shapes = destructionShapes
                
    def create(self, arena, color):
        self.shapes = []
        for shape in self.shapes:
            shape.body.DestroyFixture(shape)
            
        self.arena = arena
        
        self.display = True
        
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
        
        leg1 = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM - 0.65, 32.5))
        box = leg1.CreatePolygonFixture(box = (.4,.5), density = 4, friction = 0.3)
        #self.shapes.append(box)
        
        leg2 = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM + 0.65, 32.5))
        box = leg2.CreatePolygonFixture(box = (.4,.5), density = 4, friction = 0.3)
        #self.shapes.append(box)
        
        world.CreateDistanceJoint(bodyA=body, bodyB=arm1, anchorA=b2Vec2(body.worldCenter.x, body.worldCenter.y - 0.5), anchorB = arm1.worldCenter, collideConnected=True)
        world.CreateDistanceJoint(bodyA=body, bodyB=arm2, anchorA=b2Vec2(body.worldCenter.x, body.worldCenter.y - 0.5), anchorB = arm2.worldCenter, collideConnected=True)
        world.CreateDistanceJoint(bodyA=body, bodyB=leg1, anchorA=b2Vec2(body.worldCenter.x - 0.75, body.worldCenter.y + 0.5), anchorB = leg1.worldCenter, collideConnected=True)
        world.CreateDistanceJoint(bodyA=body, bodyB=leg2, anchorA=b2Vec2(body.worldCenter.x + 0.75, body.worldCenter.y + 0.5), anchorB = leg2.worldCenter, collideConnected=True)
        
    def kick(self): pass
        #self.shapes[3].body.ApplyForce(force=(500,0), point=(0,3), wake=True)
        #self.shapes[4].body.ApplyForce(force=(-500,0), point=(0,3), wake=True)