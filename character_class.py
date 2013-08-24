class Player(pygame.sprite.Sprite):
    def __init__(self, direction, arena, color):
        self.input = {"up": False, "down": False, "left": False, "right": False}
        self.direction = direction
        self.shapes = []
        self.create(arena, color)
        self.gottaGrow = False
    
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
                
    def create(self, arena, color):
        self.clearShapes(arena, color)
    
        body = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 34))
        box = body.CreatePolygonFixture(box = (1,2), density = 2, friction = 0.3)
        self.shapes.append(box)
        
        #arm1 = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM - 0.5, 35))
        #box = arm1.CreatePolygonFixture(box = (.2,.5), density = 10, friction = 0.3)
        #self.shapes.append(box)
        
        #arm2 = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM + 0.5, 35))
        #box = arm2.CreatePolygonFixture(box = (.2,.5), density = 10, friction = 0.3)
        #self.shapes.append(box)
        
        #world.CreateDistanceJoint(bodyA=body, bodyB=arm1, anchorA=b2Vec2(body.worldCenter.x, body.worldCenter.y - 0.5), anchorB = arm1.worldCenter, collideConnected=True)
        #world.CreateDistanceJoint(bodyA=body, bodyB=arm2, anchorA=b2Vec2(body.worldCenter.x, body.worldCenter.y - 0.5), anchorB = arm2.worldCenter, collideConnected=True)
         
    def clearShapes(self, arena, color):
        for shape in self.shapes:
            shape.body.DestroyFixture(shape)
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
<<<<<<< HEAD
        self.shapes[0].body.linearVelocity.y == -15
                
=======
        self.shapes[0].body.ApplyForce(force=(0,-250),point=(0,0),wake=True)
    
>>>>>>> 4420f1d3367a230a4c1bf225d2f6e25ed63ab962
    def createGardener(self, arena, color, minx):
        self.clearShapes(arena, color)
        y = 30
        numPlanks = 20
    
        gardnerBody = world.CreateDynamicBody(position = (minx+numPlanks, 34))
        box = gardnerBody.CreatePolygonFixture(box = (1,2), density = 20, friction = 0.3)
        self.shapes.append(box)
        
        # Make hose
        # The ground
        ground = world.CreateBody(
                    position=(minx+0.5,31),
                    fixtures=b2FixtureDef(
                        shape=b2PolygonShape(box=(0.6,0.125))
                        )
                )

        plank=b2FixtureDef(
                    shape=b2PolygonShape(box=(0.6,0.125)),
                    density=2,
                    friction=0.2,
                )

        # Create one Chain (Only the left end is fixed)
        prevBody = ground
        self.shapes.append(ground.fixtures[0])
        for i in range(numPlanks):
            body = world.CreateDynamicBody(
                        position=(minx+0.5+i, y), 
                        fixtures=plank,
                    )

            world.CreateRevoluteJoint(
                bodyA=prevBody,
                bodyB=body,
                anchor=(minx+i, y),
                )

            prevBody = body
            self.shapes.append(body.fixtures[0])
        
        hosehead = world.CreateDynamicBody(position = (minx+0.5+numPlanks, y),
            fixtures = b2FixtureDef(
                shape = b2PolygonShape(box=(1,0.4)),
                density = 2),
            userData="hose head")
        
        self.shapes.append(hosehead.fixtures[0])
            
        world.CreateRevoluteJoint(
            bodyA=prevBody,
            bodyB=hosehead,
            anchor=(minx+numPlanks, y),
            )
        
        arm1 = world.CreateDynamicBody(position = (minx+0.5+numPlanks, 30.5))
        box = arm1.CreatePolygonFixture(box = (.2,1), density = 2, friction = 0.3)
        self.shapes.append(box)
        self.arm1 = arm1
        
        world.CreateWeldJoint(bodyA=arm1, bodyB=hosehead)
        
        world.CreateRevoluteJoint(
            bodyA=gardnerBody, 
            bodyB=arm1, 
            anchor=(minx+0.5+numPlanks, 34),
            lowerAngle = -0.01*b2_pi, upperAngle = 0.01*b2_pi, enableLimit = True)
        
        # Start the water hose effect
        waterEffect = Hoser(hosehead.fixtures[0])
        effects.append(waterEffect)
        
    def aimUp(self):
        self.arm1.ApplyTorque(100, wake=True)
    
    def aimDown(self):
        self.arm1.ApplyTorque(-100, wake=True)
                
    def createPlanter(self, arena, color):
        self.clearShapes(arena, color)
        self.leaves = []
    
        body = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 34))
        box = body.CreatePolygonFixture(vertices=[(-1,-1),(-1,1),(1,1),(1,-1)], density = 2, friction = 0.3)
        self.shapes.append(box)
        
        pot = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 32), userData = "pot")
        box = pot.CreatePolygonFixture(vertices=[(-1,0),(-1,0.25),(-0.75,1),(0.75,1),(1,0.25),(1,0)], density = 0.5, friction = 0.3)
        self.shapes.append(box)
        self.pot = pot
        
        world.CreateRevoluteJoint(bodyA=body, bodyB=pot, anchor=b2Vec2((ARENA_WIDTH * (arena + 0.5)) / PPM, 33), collideConnected=True)
        
    def growPlant(self):
        self.gottaGrow = False
        if len(self.leaves) <= 1:
            leaf = world.CreateDynamicBody(position = (self.pot.worldCenter.x + random.random()*2-1, 33))
            box = leaf.CreatePolygonFixture(vertices=[(-0.25,-0.25),(-0.25,0),(0,0.25),(0.25,0.25),(0.25,0),(0,-0.25)], density = 0.5, friction = 0.3)
            self.leaves.append(leaf)
            self.shapes.append(box)
            world.CreateRevoluteJoint(bodyA=leaf, bodyB=self.pot, anchor=b2Vec2(self.pot.worldCenter.x + random.random()*2-1, 33), collideConnected=True)
        else:
            index = int(random.random() * (len(self.leaves) - 2))
            oldleaf = self.leaves[int(index)]
            
            leaf = world.CreateDynamicBody(position = (oldleaf.worldCenter.x + random.random()*0.5-0.25, oldleaf.worldCenter.y - 0.2))
            box = leaf.CreatePolygonFixture(vertices=[(-0.25,-0.25),(-0.25,0),(0,0.25),(0.25,0.25),(0.25,0),(0,-0.25)], density = 0.5, friction = 0.3)
            self.leaves.append(leaf)
            self.shapes.append(box)
            world.CreateRevoluteJoint(bodyA=leaf, bodyB=oldleaf, anchor=oldleaf.worldCenter, collideConnected=True)
            
    def createFisher(self, currentArena, color, bait):
        self.clearShapes(currentArena, color)
    
        body = world.CreateDynamicBody(position = ((ARENA_WIDTH * (currentArena + 0.5)) / PPM, 20))
        box = body.CreatePolygonFixture(box = (1,2), density = 20, friction = 0.3)
        self.shapes.append(box)
        
        arm = world.CreateDynamicBody(position = (body.worldCenter.x + 8, body.worldCenter.y + 0.5))
        box = arm.CreatePolygonFixture(box = (12,0.2), density = 2)
        self.shapes.append(box)
        
        world.CreateRevoluteJoint(bodyA=body, bodyB=arm, anchor=body.worldCenter, collideConnected=False)

        shape=b2PolygonShape(box=(0.125,0.5))
        fd=b2FixtureDef(
                    shape=shape,
                    friction=0.2,
                    density=1,
                    categoryBits=0x0001,
                    maskBits=(0xFFFF & ~0x0002),
                    )
        
        N=10
        x=body.worldCenter.x + 20
        y=body.worldCenter.y + 0.5

        prevBody=arm
        for i in range(N):
            body = world.CreateDynamicBody(
                        position=(x, 0.5+i+y), 
                        fixtures=fd,
                        )
            
            world.CreateRevoluteJoint(
                bodyA=prevBody,
                bodyB=body,
                anchor=(x, i+y),
                collideConnected=False
                )
                
            self.shapes.append(body.fixtures[0])
            prevBody = body
        
        player2.clearShapes(currentArena, (0,0,255))
    
        body = world.CreateDynamicBody(position = (x, N+y+1))
        box = body.CreatePolygonFixture(box = (1,2), density = 2, friction = 0.3)
        player2.shapes.append(box)
            
        world.CreateRevoluteJoint(
                bodyA=prevBody,
                bodyB=body,
                anchor=(x, i+y),
                collideConnected=False
            )
        
    def reelInLine(self):
        self.shapes[1].body.ApplyForce(force=(-6000,0),point=(1,0), wake=True)
        
    def thrash(self):
        self.shapes[0].body.ApplyLinearImpulse(impulse=(10,0),point=(0,0), wake=True)
    def createWarrior(self, arena, color):
        self.clearShapes(arena, color)
        
        launchers = 0x0002
        humans = 0x0004
        
        noTouchingLaunchers = 0xFFFF ^ launchers
        noTouchingHumans = 0xFFFF ^ humans
        
        # Create warrior body, with "Rocket launcher" on top
        warriorBody = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 20),
                        fixtures = b2FixtureDef(
                                shape = b2PolygonShape(box=(1, 2, (0, 2.5), 0)),
                                density = 2,
                                filter = b2Filter(
                                    categoryBits = humans,
                                    maskBits = noTouchingLaunchers
                                )),
                        userData = "warrior"
                        )
        rocketLauncherBody = world.CreateDynamicBody(position = ((ARENA_WIDTH * (arena + 0.5)) / PPM, 20),
                        fixtures = b2FixtureDef(
                                shape = b2PolygonShape(box=(1.2,0.5,(0, 0), 0)),
                                density = -50,
                                filter = b2Filter(
                                    categoryBits = launchers,
                                    maskBits = noTouchingHumans
                                )),
                        userData = "rocket launcher"
                        )
                        
        # Bind 'em together with revolute joint
        world.CreateRevoluteJoint(bodyA=warriorBody, bodyB=rocketLauncherBody, 
                localAnchorA = (0,0), localAnchorB = (0, 0), collideConnected=False)
        self.shapes.append(warriorBody.fixtures[0])
        self.shapes.append(rocketLauncherBody.fixtures[0])
        
    def aimRocket(self, degree):
        self.shapes[1].body.angularVelocity += degree
        
    def getRocketLauncher(self):
        return self.shapes[1]
