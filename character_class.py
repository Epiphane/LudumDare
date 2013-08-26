
class Player(pygame.sprite.Sprite):
        
    def __init__(self, direction, start_x, color, color_2, arena, playerNum):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.color = color
        self.color_2 = color_2
        self.shapes = []
        self.arena = arena
        
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
        
        self.toExpand = False
        self.toNormalSize = False
        
        self.speed = 10
        self.airspeed = 14
        self.moving = None
        
        self.dead = False
        self.materialize(start_x, arena, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes(arena)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction=CHAR_FRICTION,
                restitution=0
            ),
            userData = "player"+str(playerNum)
        )
        block.color = self.color_2
        self.shapes.append(block)
        
        w = self.size[0]
        h = self.size[1]
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1*w-.6,-1*h-.1),(w+.6,-1*h-.1),(w+.6,h+.1),(-1*w-.6,h+.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False
        self.dx = 0
        
    def draw(self, screen, offsetX, offsetY):
        for shape in self.shapes:
            DrawPolygon(vertices_with_offset(shape.fixtures[0], offsetX, offsetY), (0,0,0), shape.color)
    
    def destroy(self):
        destructionShapes = []
        if len(self.shapes) > 1:
            for i in range(1,len(self.shapes)):
                # Grab the old vertices from the shape
                olds = self.shapes[i].fixtures[0].shape.vertices
                # Convert them (with magic) using the body.transform thing
                result = [(self.shapes[i].transform*v) for v in olds]
                for v in result:
                    body = arena.world.CreateDynamicBody(position = v, userData = "particle")
                    shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                    body.color = self.shapes[i].color
                    body.linearVelocity.y = -15
                    body.linearVelocity.x = random.random() * 6 - 3
                    destructionShapes.append(body)
                
        # Grab the old vertices from the shape
        olds = self.shapes[0].fixtures[0].shape.vertices
        for i in range(20):
            # Convert them (with magic) using the body.transform thing
            result = [(self.shapes[0].transform*v) for v in olds]
            for v in result:
                body = arena.world.CreateDynamicBody(position = (v.x + random.random()*4 - 2, v.y + random.random()*4-2), userData = "particle")
                shape = body.CreatePolygonFixture(box = (.2,.2), density = 1, isSensor = True)
                body.color = self.shapes[0].color
                body.linearVelocity.y = -15
                body.linearVelocity.x = random.random() * 16 - 8
                destructionShapes.append(body)
                
        self.clearShapes()
        self.shapes = destructionShapes
                
    def create(self, color):
        self.clearShapes(arena, color)
    
        body = arena.world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 34))
        box = body.CreatePolygonFixture(box = (1,2), density = CHAR_DENSITY, friction = 0.3)
        self.shapes.append(body)
         
    def clearShapes(self, a = None):
        if a is not None:
            for shape in self.shapes:
                a.world.DestroyBody(shape)
        else:
            for shape in self.shapes:
                arena.world.DestroyBody(shape)
        self.shapes = []
      
    def update(self, nogravity = False):
        if self.toExpand:
            self.expand()
            self.toExpand = False
        if self.toNormalSize:
            self.normal()
            self.toNormalSize = False
        if(self.dead):
            self.destroy()
            return
            
        self.shapes[0].awake = True
        if nogravity:
            if self.input["up"]:
                self.shapes[0].linearVelocity.y -= 3
            if self.input["down"]:
                self.shapes[0].linearVelocity.y += 3
            if self.input["left"]:
                self.shapes[0].linearVelocity.x -= 4
            if self.input["right"]:
                self.shapes[0].linearVelocity.x += 4
                
            if self.shapes[0].linearVelocity.y > 20: self.shapes[0].linearVelocity.y = 20
            if self.shapes[0].linearVelocity.y < -20: self.shapes[0].linearVelocity.y = -20
            if self.shapes[0].linearVelocity.x > 20: self.shapes[0].linearVelocity.x = 20
            if self.shapes[0].linearVelocity.x < -20: self.shapes[0].linearVelocity.x = -20
        else:
            if self.moving is not None: 
                if self.moving == "l": 
                    self.shapes[0].linearVelocity.x += self.speed
                if self.moving == "r":
                    self.shapes[0].linearVelocity.x -= self.speed
            
            if len(self.shapes[0].contacts) > 0: maxspeed = self.speed
            else: maxspeed = self.speed + self.airspeed
            if self.input["left"]:
                self.shapes[0].linearVelocity.x -= maxspeed
            if self.input["right"]:
                self.shapes[0].linearVelocity.x += maxspeed
                
            if self.shapes[0].linearVelocity.x > 20: self.shapes[0].linearVelocity.x = 20
            if self.shapes[0].linearVelocity.x < -20: self.shapes[0].linearVelocity.x = -20
            
    def jump(self):
        if len(self.shapes[0].contacts) > 0:
            self.shapes[0].linearVelocity.y = -15
            self.shapes[0].angularVelocity = 5.4
                
    def dive(self):
        if self.shapes[0].linearVelocity.x > 0:
            dir = "l"
        else:
            dir = "r"
            
        if len(self.shapes[0].contacts) == 0:
            self.shapes[0].linearVelocity.y = 25
            self.shapes[0].linearVelocity.x *= 2
            if dir == "l":
                if self.shapes[0].angle < math.pi / 4:
                    self.shapes[0].angularVelocity = 0.5
                else:
                    self.shapes[0].angularVelocity = -0.5
            if dir == "r":
                if self.shapes[0].angle < - math.pi / 4:
                    self.shapes[0].angularVelocity = 0.5
                else:
                    self.shapes[0].angularVelocity = -0.5
            
    def jump(self, gravity):
        if gravity == b2Vec2(0,0): pass
        else:
            if len(self.shapes[0].contacts) > 0:
                self.shapes[0].linearVelocity.y = -20 * gravity[1] / 25
                self.shapes[0].angularVelocity = -5.4 * self.direction
                
    def makeNewBlock(self, size):
        i = 0
        shape = self.shapes[i]
        s = shape.fixtures[0].shape
        
        newshape = arena.world.CreateDynamicBody(
            position = shape.position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = size),
                density=shape.fixtures[0].density,
                friction = shape.fixtures[0].friction,
                restitution=shape.fixtures[0].restitution
            ),
            userData = shape.userData
        )
        arena.world.DestroyBody(self.shapes[i])
        self.shapes[i] = newshape
    
    def expand(self):
        self.makeNewBlock(self.large)
    
    def normal(self):
        self.makeNewBlock(self.size)
    
    def shrink(self):
        self.makeNewBlock(self.small)

class Lars(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
        
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 255, 0), arena, playerNum)

class Pate(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        self.small = (0.4,1)
        self.size = (0.8,2.3)
        self.large = (1.6,4.2)
        
        Player.__init__(self, direction, start_x, (0, 0, 0), (0, 255, 255), arena, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes(arena)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction = 10000,
                restitution=0),
            userData = "player"+str(playerNum)
        )
        block.color = self.color_2
        self.shapes.append(block)
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False

class Buster(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        Player.__init__(self, direction, start_x, (0, 0, 0), (153, 255, 0), arena, playerNum)
        
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
        
        self.materialize(start_x, arena, playerNum)

class EricStrohm(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        Player.__init__(self, direction, start_x, (0, 0, 0), (30, 30, 30), arena, playerNum)
        
        self.speed = 12
        self.airspeed = 20

class Ted(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 0), arena, playerNum)
        
        self.small = (0.7,0.7)
        self.size = (1.3,1.3)
        self.large = (2.5,2.5)
        self.clearShapes(arena)        
        
        self.materialize(start_x, arena, playerNum)

class SmithWickers(Player):
    def __init__(self, direction, start_x, arena, playerNum):
        
        self.alt_color =  pygame.color.Color(255, 102, 0)
        self.alt_color_2 =  pygame.color.Color(102, 51, 102)
        
        Player.__init__(self, direction, start_x, (0, 0, 0), (255, 0, 255), arena, playerNum)
        
        self.small = (0.3,0.8)
        self.size = (0.75,1.7)
        self.large = (1.5,3.5)
        
        self.materialize(start_x, arena, playerNum)
        
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes(arena)
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction = CHAR_FRICTION,
                restitution=0),
            userData = "player"+str(playerNum)
        )
        block.color = self.alt_color
        self.shapes.append(block)
        
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1.6,-2.1),(1.6,-2.1),(1.6,2.1),(-1.6,2.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
            
        block2 = arena.world.CreateDynamicBody(
            position = (start_x - 3, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction=CHAR_FRICTION,
                restitution=0),
            userData = "player"+str(playerNum)
        )
        block2.color = self.alt_color_2
        self.shapes.append(block2)
        
        arena.world.CreateDistanceJoint(bodyA = block, bodyB = block2, anchorA = block.worldCenter, anchorB = block2.worldCenter, collideConnected = True)
        
        self.dead = False
                
    def expand(self):
        shape = self.shapes[0]
        s = shape.fixtures[0].shape
        block = arena.world.CreateDynamicBody(
            position = shape.position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.large),
                density=shape.fixtures[0].density,
                friction = shape.fixtures[0].friction,
                restitution=shape.fixtures[0].restitution
            ),
            userData = shape.userData
        )
        block.color = self.alt_color
        arena.world.DestroyBody(self.shapes[0])
        self.shapes[0] = block
        
        oldpos = shape.position
        shape2 = self.shapes[1]
        newpos = shape2.position
        s = shape2.fixtures[0].shape
        block2 = arena.world.CreateDynamicBody(
            position = (newpos.x + (newpos.x - oldpos.x) * 4/3, newpos.y + (newpos.y - oldpos.y) * 4/3),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.large),
                density=shape2.fixtures[0].density,
                friction = shape2.fixtures[0].friction,
                restitution=shape2.fixtures[0].restitution
            ),
            userData = shape2.userData
        )
        block2.color = self.alt_color_2
        arena.world.DestroyBody(self.shapes[1])
        self.shapes[1] = block2
        
        arena.world.CreateDistanceJoint(bodyA = block, bodyB = block2, anchorA = block.worldCenter, anchorB = block2.worldCenter, collideConnected = True)
                
    def normal(self):
        shape = self.shapes[0]
        s = shape.fixtures[0].shape
        block = arena.world.CreateDynamicBody(
            position = shape.position,
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=shape.fixtures[0].density,
                friction = shape.fixtures[0].friction,
                restitution=shape.fixtures[0].restitution
            ),
            userData = shape.userData
        )
        block.color = self.alt_color
        arena.world.DestroyBody(self.shapes[0])
        self.shapes[0] = block
        
        oldpos = shape.position
        shape2 = self.shapes[1]
        newpos = shape2.position
        s = shape2.fixtures[0].shape
        block2 = arena.world.CreateDynamicBody(
            position = (oldpos.x - 3, oldpos.y),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=shape2.fixtures[0].density,
                friction = shape2.fixtures[0].friction,
                restitution=shape2.fixtures[0].restitution
            ),
            userData = shape2.userData
        )
        block2.color = self.alt_color_2
        arena.world.DestroyBody(self.shapes[1])
        self.shapes[1] = block2
        
        arena.world.CreateDistanceJoint(bodyA = block, bodyB = block2, anchorA = block.worldCenter, anchorB = block2.worldCenter, collideConnected = True)

class CrowdMember(Player):
    def __init__(self, direction, start_x, color, arena):
        Player.__init__(self, direction, start_x, (0, 0, 0), color, arena, 0)
        self.timeToJump = random.random() * 10000 + 1000
        
        self.small = (0.5,1)
        self.size = (1,2)
        self.large = (2,4)
    
    def materialize(self, start_x, arena, playerNum):
        self.clearShapes()
            
        block = arena.world.CreateDynamicBody(
            position = (start_x, 30),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box = self.size),
                density=CHAR_DENSITY,
                friction=CHAR_FRICTION,
                restitution=0,
                filter = b2Filter(
                    categoryBits = 0x0010,
                    maskBits = 0xFFFF ^ 0x0010
                )
            ),
            userData = "crowd member"
        )

        block.color = self.color_2
        self.shapes.append(block)
        
        w = self.size[0]
        h = self.size[1]
        foot = block.CreateFixture(
                shape = b2PolygonShape(vertices = [(-1*w-.6,-1*h-.1),(w+.6,-1*h-.1),(w+.6,h+.1),(-1*w-.6,h+.1)]),
                isSensor=True
            )
        self.foot = block.fixtures[1]
        
        self.dead = False
        self.dx = 0
      
    def update(self, dt, nogravity = False):
        if(self.dead):
            self.dead = False
            return
            
        self.shapes[0].awake = True
        if nogravity: pass
        else:
            if abs(self.shapes[0].transform.angle) > 0.1  and abs(self.shapes[0].transform.angle - 180) > 0.1 and self.shapes[0].linearVelocity.y == 0:
                self.jumpBackUp()
        
            self.timeToJump -= dt
            if self.timeToJump <= 0 and self.shapes[0].linearVelocity.y == 0:
                self.jump()
                self.timeToJump = random.random() * 10000 + 1000
            maxspeed = 3
            
            if self.shapes[0].linearVelocity.x != 0 and random.random() > 0.7 and self.shapes[0].linearVelocity.y == 0:
                self.shapes[0].linearVelocity.x = 0
                
            if self.shapes[0].linearVelocity.x == 0 and random.random() > 0.7 and self.shapes[0].linearVelocity.y == 0:
                self.shapes[0].linearVelocity.x = 5 * (random.random() * 4 - 2)
            
    def jump(self):
        if len(self.shapes[0].contacts) > 0:
            self.shapes[0].linearVelocity.y -= 15
            
    def jumpBackUp(self):
        if len(self.shapes[0].contacts) > 0:
            self.shapes[0].linearVelocity.y = -10
            self.shapes[0].angularVelocity = 2
