
class Player(pygame.sprite.Sprite):
        
    def __init__(self, direction, start_x, color, color_2, arena, playerNum):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.color = color
        self.color_2 = color_2
        self.shapes = []
        self.arena = arena
        
        self.speed = 10
        self.airspeed = 14
        self.moving = None
        
        self.dead = False
        self.materialize(start_x, arena, 0, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        while len(self.shapes) > 0:
            shape = self.shapes[0]
            arena.world.DestroyBody(shape.body)
            self.shapes.remove(shape)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1,2)),
                density=10,
                restitution=0),
            userData = "player" + str(playerNum)
            )
        self.shapes.append(block.fixtures[0])
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False
        
    def draw(self, screen, offsetX, offsetY):
        if len(self.shapes) > 0:
            DrawPolygon(vertices_with_offset(self.shapes[0], offsetX, offsetY), self.color, self.color_2)
        if len(self.shapes) > 1:
            DrawPolygon(vertices_with_offset(self.shapes[1], offsetX, offsetY), self.alt_color, self.alt_color_2)
    
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
         
    def clearShapes(self):
        for shape in self.shapes:
            arena.world.DestroyBody(shape.body)
        self.shapes = []
      
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
            if self.moving is not None: 
                if self.moving == "l": 
                    self.shapes[0].body.linearVelocity.x += self.speed
                if self.moving == "r":
                    self.shapes[0].body.linearVelocity.x -= self.speed
            
            if len(self.foot.body.contacts) > 0: maxspeed = self.speed
            else: maxspeed = self.speed + self.airspeed
            if self.input["left"]:
                self.shapes[0].body.linearVelocity.x -= maxspeed
            if self.input["right"]:
                self.shapes[0].body.linearVelocity.x += maxspeed
                
            if self.shapes[0].body.linearVelocity.x > 20: self.shapes[0].body.linearVelocity.x = 20
            if self.shapes[0].body.linearVelocity.x < -20: self.shapes[0].body.linearVelocity.x = -20
            
    def jump(self):
        if len(self.foot.body.contacts) > 0:
            self.shapes[0].body.linearVelocity.y = -15
            self.shapes[0].body.angularVelocity = 5.4
                
    def dive(self):
        if self.shapes[0].body.linearVelocity.x > 0:
            dir = "l"
        else:
            dir = "r"
            
        if len(self.foot.body.contacts) == 0:
            self.shapes[0].body.linearVelocity.y = 25
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
    def __init__(self, direction, start_x, arena, playerNum):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 255, 0), arena, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes()
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1,2)),
                density=10,
                restitution=0),
                userData = "player" + str(playerNum)
            )
            
        print "userdata: ", block.userData
        self.shapes.append(block.fixtures[0])
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False

class Pate(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (0, 255, 255), arena)
        
    def materialize(self, start_x, arena):
        self.clearShapes()
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (0.8,2)),
                density=10,
                restitution=0),
                userData = "player"
            )
        self.shapes.append(block.fixtures[0])
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False

class Buster(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (153, 255, 0), arena)
        
    def materialize(self, start_x, arena):
        self.clearShapes()
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1,1.8)),
                density=10,
                restitution=0),
                userData = "player"
            )
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.shapes.append(block.fixtures[0])
        
        self.dead = False

class EricStrohm(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (30, 30, 30), arena)
        
    def materialize(self, start_x, arena):
        self.clearShapes()
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1,2)),
                density=10,
                restitution=0),
                userData = "player"
            )
        self.shapes.append(block.fixtures[0])
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False

class Ted(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 0), arena)
        
    def materialize(self, start_x, arena):
        self.clearShapes()
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = (1.4,1.5)),
                density=10,
                restitution=0)
            )
        self.shapes.append(block.fixtures[0])
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False

class SmithWickers(Player):
    def __init__(self, direction, start_x, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 255), arena)
        
        self.alt_color =  pygame.color.Color(255, 102, 0)
        self.alt_color_2 =  pygame.color.Color(102, 51, 102)
        
    def materialize(self, start_x, arena):
        self.clearShapes()
            
        size = (0.7, 1.8)
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = size),
                density=10,
                restitution=0),
                userData = "player"
            )
        self.shapes.append(block.fixtures[0])
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
            
        block2 = arena.world.CreateDynamicBody(
            position = (start_x - 3, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = size),
                density=10,
                restitution=0),
                userData = "player"
            )
        self.shapes.append(block2.fixtures[0])
        
        arena.world.CreateDistanceJoint(bodyA = block, bodyB = block2, anchorA = block.worldCenter, anchorB = block2.worldCenter, collideConnected = True)
        
        self.dead = False
