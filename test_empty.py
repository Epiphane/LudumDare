#!/usr/bin/env python

from framework import *

class Level(Framework):
    """You can use this class as an outline for your tests.

    """
    name = "Level" # Name of the class to display
    description="The description text goes here"
    def __init__(self):
        """ 
        Initialize all of your objects here.
        Be sure to call the Framework's initializer first.
        """
        super(Level, self).__init__()

        
        
        
        
        # Initialize all of the objects


    def Keyboard(self, key):
        """
        The key is from Keys.K_*
        (e.g., if key == Keys.K_z: ... )
        """
        
        if key == Keys.K_a:
            print("a pressed")
        
        pass
        
    def KeyboardUp(self, key):
        """
        Callback indicating 'key' has been released.
        """
        pass

    def Step(self, settings):
        """Called upon every step.
        You should always call
         -> super(Your_Test_Class, self).Step(settings)
        at the beginning or end of your function.

        If placed at the beginning, it will cause the actual physics step to happen first.
        If placed at the end, it will cause the physics step to happen after your code.
        """

        super(Level, self).Step(settings)

        # do stuff

        # Placed after the physics step, it will draw on top of physics objects
        self.Print("*** Base your own testbeds on me! ***")

    def ShapeDestroyed(self, shape):
        """
        Callback indicating 'shape' has been destroyed.
        """
        pass

    def JointDestroyed(self, joint):
        """
        The joint passed in was removed.
        """
        pass

    # More functions can be changed to allow for contact monitoring and such.
    # See the other testbed examples for more information.

if __name__=="__main__":
    main(Level)

