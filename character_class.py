
class Player(pygame.sprite.Sprite):
    def __init__(self, direction, color, color_2, arena):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.color = color
        self.color_2 = color_2
        self.shapes = []
        self.arena = arena
        
        self.dead = False
        
    def __init__(self, direction, start_x, color, color_2, arena):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.color = color
        self.color_2 = color_2
        self.shapes = []
        self.arena = arena
        
        self.dead = False
        
        self.materialize(start_x, arena)
        
    def materialize(self, start_x, arena):
        while len(self.shapes) > 0:
            shape = self.shapes[0]
            arena.world.DestroyBody(shape.body)
            self.shapes.remove(shape)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1,2)),
                density=10,
                restitution=0)
            )
        self.shapes.append(block.fixtures[0])
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-0.5,1.5),(-0.5,2.5),(0.5,2.5),(0.5,1.5)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False
        
    def draw(self, screen, offsetX, offsetY):
        if len(self.shapes) > 0:
            DrawPolygon(vertices_with_offset(self.shapes[0], offsetX, offsetY), self.color, self.color_2)
    
    def destroy(self):
        destructionShapes = []
        if len(self.shapes) > 1:
            for i in range(1,len(self.shapes)):
                # Grab the old vertices from the shape
                olds = self.shapes[i].shape.vertices
                # Convert them (with magic) using the body.transform thing
                result = [(self.shapes[i].body.transform*v) for v in olds]
                for v in result:
                    body = arena.world.CreateDynamicBody(position = v)
                    shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                    destructionShapes.append(shape)
                
        # Grab the old vertices from the shape
        olds = self.shapes[0].shape.vertices
        for i in range(10):
            # Convert them (with magic) using the body.transform thing
            result = [(self.shapes[0].body.transform*v) for v in olds]
            for v in result:
                body = arena.world.CreateDynamicBody(position = (v.x + random.random()*4 - 2, v.y + random.random()*4-2))
                shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                destructionShapes.append(shape)
                
        for shape in self.shapes:
            shape.body.DestroyFixture(shape)
        self.shapes = destructionShapes
                
    def create(self, color):
        self.clearShapes(arena, color)
    
        body = arena.world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 34))
        box = body.CreatePolygonFixture(box = (1,2), density = 2, friction = 0.3)
        self.shapes.append(box)
         
    def clearShapes(self, arena, color):
        for shape in self.shapes:
            world.DestroyBody(shape.body)
        self.shapes = []
        
        self.arena = arena
        
        self.display = True
        
        self.color = color  
      
    def update(self, nogravity = False):
        if(self.dead):
            self.destroy()
            return
            
        self.shapes[0].body.awake = True
        if nogravity:
            if self.input["up"]:
                self.shapes[0].body.linearVelocity.y -= 3
            if self.input["down"]:
                self.shapes[0].body.linearVelocity.y += 3
            if self.input["left"]:
                self.shapes[0].body.linearVelocity.x -= 4
            if self.input["right"]:
                self.shapes[0].body.linearVelocity.x += 4
                
            if self.shapes[0].body.linearVelocity.y > 20: self.shapes[0].body.linearVelocity.y = 20
            if self.shapes[0].body.linearVelocity.y < -20: self.shapes[0].body.linearVelocity.y = -20
            if self.shapes[0].body.linearVelocity.x > 20: self.shapes[0].body.linearVelocity.x = 20
            if self.shapes[0].body.linearVelocity.x < -20: self.shapes[0].body.linearVelocity.x = -20
        else:
            self.shapes[0].body.linearVelocity.x = 0
            
            if len(self.foot.body.contacts) > 0: maxspeed = 10
            else: maxspeed = 12
            if self.input["left"]:
                self.shapes[0].body.linearVelocity.x -= maxspeed
            if self.input["right"]:
                self.shapes[0].body.linearVelocity.x += maxspeed
            
    def jump(self):
        if len(self.foot.body.contacts) > 0:
            self.shapes[0].body.linearVelocity.y = -15
            self.shapes[0].body.angularVelocity = 5.4
                
    def dive(self):
        if self.shapes[0].body.linearVelocity.x > 0:
            self.dive("l")
        else:
            self.dive("r")
                
    def dive(self, dir):
        if len(self.foot.body.contacts) == 0:
            self.shapes[0].body.linearVelocity.y = 15
            self.shapes[0].body.linearVelocity.x *= 2
            if dir == "l":
                if self.shapes[0].body.angle < math.pi / 4:
                    self.shapes[0].angularVelocity = 0.5
                else:
                    self.shapes[0].angularVelocity = -0.5
            if dir == "r":
                if self.shapes[0].body.angle < - math.pi / 4:
                    self.shapes[0].angularVelocity = 0.5
                else:
                    self.shapes[0].angularVelocity = -0.5
            
    def jump(self, gravity):
        if gravity == b2Vec2(0,0): pass
        else:
            if len(self.foot.body.contacts) > 0:
                self.shapes[0].body.linearVelocity.y = -15 * gravity[1] / 25
                self.shapes[0].body.angularVelocity = -5.4 * self.direction

class Lars(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 255, 0), arena)

class Pate(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (0, 255, 255), arena)

class Buster(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (153, 255, 0), arena)

class EricStrohm(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (128, 128, 128), arena)

class Ted(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 0), arena)

class SmithWickers(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 255), arena)