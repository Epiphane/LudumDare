class Player(pygame.sprite.Sprite):
    def __init__(self, direction, start_x, color):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.color = color
        self.shapes = []
        
    def materialize(self, start_x):
        block = world.CreateDynamicBody(
            position = (start_x, 34),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1,2)),
                density=10,
                restitution=0)
            )
        self.shapes.append(block.fixtures[0])
        
    def draw(self, screen, offsetX, offsetY):
        pass
    
    def destroy(self):
        destructionShapes = []
        if len(self.shapes) > 1:
            for i in range(1,len(self.shapes)):
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
                
    def create(self, color):
        self.clearShapes(arena, color)
    
        body = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 34))
        box = body.CreatePolygonFixture(box = (1,2), density = 2, friction = 0.3)
        self.shapes.append(box)
         
    def clearShapes(self, arena, color):
        for shape in self.shapes:
            world.DestroyBody(shape.body)
        self.shapes = []
        
        self.arena = arena
        
        self.display = True
        
        self.color = color  
      
    def update(self):
        self.shapes[0].body.awake = True
        self.shapes[0].body.linearVelocity.x = 0
        if self.input["left"]:
            self.shapes[0].body.linearVelocity.x -= 10
        if self.input["right"]:
            self.shapes[0].body.linearVelocity.x += 10
            
        if self.gottaGrow:
            self.growPlant()
            
    def jump(self):
        self.shapes[0].body.linearVelocity.y == -15
