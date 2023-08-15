import random
from numpy import *
class Guts:
    def __init__(self, pointLocations, linePointIndices):
        # This is the angle by which yaw and/or pitch will change by at each frame, in radians
        self.angle = 1/40
        # This is the movement speed, in units per frame. It is also the magnitude of each vector in the observer (see
        # self.observerBasisVectors) and chain (see self.chainBasisVectors) bases for faster calculation of movement translation.
        # This affects how any distance measurements using these bases should be taken. Furthermore, the meaning of this value,
        # originally an exact value, gets conflated later on with a proportion (see self.toggleHelmet)
        self.speed = 0.1
        # This holds the locations of our points in the standard basis, and it is not affected by movement/rotation of the user.
        # It takes the form of a 3xn matrix where each column represents the location of one point
        self.originalPointLocations = pointLocations
        # This holds the locations of our points in the observer basis. Because of the non-unit magnitudes of the vectors of this
        # basis, distances in this basis should be taken carefully, considering the value of self.speed. It is also formatted
        # as a 3xn matrix
        self.pointLocations = pointLocations
        # This determines how the lines are drawn. It keeps track of the vertex pairs between which a line is to be drawn in the
        # form of a 2xm matrix. Each element represents the index of a point in the range (0,n-1). An element of value n, which may
        # be placed by this program in the final column and row of linePointIndices, is taken in a special purpose to represent a
        # (terminal) vertex not yet, but soon to be, determined (see self.holdingPoint)
        self.linePointIndices = linePointIndices
        # The next three lines support an editor mode by creating unmoving lines (in the observer basis) that model a helmet and
        # track whether the editor mode is active
        self.helmetPointLocations = matrix([[-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,-0.16,-0.16,-0.16,-0.16,0.16,0.16,0.16,0.16],
                                            [-0.03,-0.03,0.03,0.03,-0.03,-0.03,0.03,0.03,-0.03,-0.03,0.03,0.03,-0.03,-0.03,0.03,0.03],
                                            [ 0.01,  1,0.01, 1,0.01,   1,0.01, 1,0.01,  1,0.01, 1,0.01,   1,0.01, 1]], float32)
        self.helmetLinePointIndices = matrix([[0,2,4,6,1,3,8,10,12,14],
                                              [1,3,5,7,5,7,9,11,13,15]])
        self.helmet = False
        # These are additional initial values used in the editor mode; holdingPoint represents whether the user has placed the
        # initial vertex of a new line and has yet to place the terminal vertex, and zOfInitial allows a terminal vertex to be
        # held (and placed) at an distance from the user equal to the initial point, making editor mode more user-friendly
        self.holdingPoint = False
        self.zOfInitial = 20
        # These track the position and orientation of the observer. The difference between the observer and chain bases is analogous
        # to the difference between a head and body. The orientation of the two bases only differs in pitch (like a head looking up
        # or down), and the chain basis remains upright, like a standing body. This is in keeping with user expectations for typical
        # movement in videogames. These matrices are 3x3, and their columns represent their basis vectors
        self.observerLocation = matrix([[0],[0],[0]],float32)
        self.observerBasisVectors = multiply(matrix([[1,0,0],[0,1,0],[0,0,1]],float32),matrix([[self.speed]],float32))
        self.chainBasisVectors = multiply(matrix([[1,0,0],[0,1,0],[0,0,1]],float32),matrix([[self.speed]],float32))
        # These allow for rotation of the observer and chain bases by matrix multiplications (and sometimes a change of basis)
        self.pitchDown = matrix([[1,0,0],[0,cos(self.angle),-sin(self.angle)],[0,sin(self.angle),cos(self.angle)]])
        self.pitchUp = matrix([[1,0,0],[0,cos(self.angle),sin(self.angle)],[0,-sin(self.angle),cos(self.angle)]])
        self.yawLeft = matrix([[cos(self.angle),0,-sin(self.angle)],[0,1,0],[sin(self.angle),0,cos(self.angle)]])
        self.yawRight = matrix([[cos(self.angle),0,sin(self.angle)],[0,1,0],[-sin(self.angle),0,cos(self.angle)]])
        # This tracks the current pitch of the observer basis relative to the chain basis to impose a constraint on pitch, keeping
        # it in the range (-pi/2, pi/2) in keeping with user expectations.
        self.anglePitchedAt = 0
        # This allows for more immediate retrieval of the indices of points, which are often needed
        self.n = pointLocations.shape[1]
        # This creates our moves dictionary, where keycodes linked to movement functions
        self.fwKey = '87'
        self.bwKey = '83'
        self.lfKey = '65'
        self.rtKey = '68'
        self.upKey = '32'
        self.dnKey = '16'
        self.pUKey = '38'
        self.pDKey = '40'
        self.yLKey = '37'
        self.yRKey = '39'
        self.moveDict = {self.fwKey: self.forward, self.bwKey: self.backward, self.lfKey: self.left, self.rtKey: self.right, self.upKey: self.up, self.dnKey: self.down, self.pUKey: self.lookUp, self.pDKey: self.lookDown, self.yLKey: self.lookLeft, self.yRKey: self.lookRight, 'none': self.none}

    def project(self):
        '''
        Return perspective projection of self.pointLocations by dividing by the absolute value of the z-value (third row). Points
        both in front and behind are displayed (i.e. control of which lines to draw is not included within this function)
        '''
        return divide(self.pointLocations[ix_([0,1],arange(self.n))],absolute(self.pointLocations[ix_([2],arange(self.n))]))
    
    def projectHelmet(self):
        '''
        Return perspective projection of self.HelmetPointLocations by dividing by the absolute value of the z-value (third row). Points
        both in front and behind are displayed (i.e. control of which lines to draw is not included within this function)
        '''
        return divide(self.helmetPointLocations[ix_([0,1],arange(16))],absolute(self.helmetPointLocations[ix_([2],arange(16))]))
    
    def paint(self, canvas):
        '''
        Create final image from self.pointLocations and self.linePointIndices and apply to 'canvas', including presence or absence of
        editor-mode helmet (known by self.helmet) and removal of lines existing behind the observer
        '''
        canvas.delete('all')
        # Using self.project(), adjusting size, and centering, produce the final locations of the points on the canvas
        scale = max(canvas.winfo_width(),canvas.winfo_height())
        endpoints = add(multiply(self.project(),matrix([[scale],[-1*scale]])),matrix([[canvas.winfo_width()/2],[canvas.winfo_height()/2]], float32))
        helmetEndpoints = add(multiply(self.projectHelmet(),matrix([[scale],[-1*scale]])),matrix([[canvas.winfo_width()/2],[canvas.winfo_height()/2]], float32))
        # Iterate through all lines, except the last (which will be checked for a special case)
        for i in range(0,self.linePointIndices.shape[1]-1):
            # Determine whether at least one vertex is in front of the observer
            if not (self.pointLocations[2,self.linePointIndices[0,i]] < 0 and  self.pointLocations[2,self.linePointIndices[1,i]] < 0):
                # If so, draw the line
                canvas.create_line(endpoints[0,self.linePointIndices[0,i]], endpoints[1,self.linePointIndices[0,i]], endpoints[0,self.linePointIndices[1,i]], endpoints[1,self.linePointIndices[1,i]])
        # Save the index in linePointIndices of the final line for repeated retrieval
        lastLineIndex = self.linePointIndices.shape[1]-1
        # Determine whether our special case is at hand
        if self.linePointIndices[1,lastLineIndex]==self.pointLocations.shape[1]:
            # If so, have the final line terminate at the center of the canvas
            canvas.create_line(endpoints[0,self.linePointIndices[0,lastLineIndex]], endpoints[1,self.linePointIndices[0,lastLineIndex]], canvas.winfo_width()/2, canvas.winfo_height()/2)
        else:
            # If not, draw the final line as normal
            canvas.create_line(endpoints[0,self.linePointIndices[0,lastLineIndex]], endpoints[1,self.linePointIndices[0,lastLineIndex]], endpoints[0,self.linePointIndices[1,lastLineIndex]], endpoints[1,self.linePointIndices[1,lastLineIndex]])
        # Determine whether the user is in editor mode
        if self.helmet:
            # If so, draw the helmet (10 is the number of the lines in the helmet, and it is constant)
            canvas.create_line(-14250.0, 5100.0, 600.0, 645.0)
            canvas.create_line(-14250.0, -3900.0, 600.0, 555.0)
            canvas.create_line(15750.0, 5100.0, 900.0, 645.0)
            canvas.create_line(15750.0, -3900.0, 900.0, 555.0)
            canvas.create_line(600.0, 645.0, 900.0, 645.0)
            canvas.create_line(600.0, 555.0, 900.0, 555.0)
            canvas.create_line(-23250.0, 5100.0, 510.0, 645.0)
            canvas.create_line(-23250.0, -3900.0, 510.0, 555.0)
            canvas.create_line(24750.0, 5100.0, 990.0, 645.0)
            canvas.create_line(24750.0, -3900.0, 990.0, 555.0)

    def act(self, buttons, canvas):
        '''
        Make an action within the space. Through a list of keycodes 'buttons' and a given canvas 'canvas' to paint on, this function
        instructs the program to make the proper movements, record the changes, and paint the resulting frame
        '''
        for key in buttons:
            # For each keycode represented by buttons as being currently pressed, call the appropriate function from our moves dictionary
            self.moveDict.get(str(key),self.moveDict['none'])()
        # Call translate() to update pointLocations from originalPointLocations, since the observer may have moved and/or rotated
        self.translate()
        # Paint the provided canvas
        self.paint(canvas)

    def interact(self, key, canvas):
        '''
        Interact with your space through editor mode. By different keycodes, toggle editor mode, create a line originating at a new or
        existing vertex, and terminate a line at a new or existing vertex
        '''
        #\/ If 'i' is pressed at any time
        if key == 73:
            # Toggle editor mode
            self.toggleHelmet()
            # Paint the new frame with/without the helmet
            self.paint(canvas)
        #\/ If 'q' is pressed in helmet mode (nearby existing point)
        if key == 81 and self.helmet:
            # Find nearest point to center
            nearestPointIndex = self.getIndexOfNearestPointToCenter()
            if self.holdingPoint:
                # If user is holding a point, connect the line to the new nearest point
                self.linePointIndices[1,self.linePointIndices.shape[1]-1] = nearestPointIndex
                # Additionally, reset the previously-saved z-value to its default of 10 (divide by speed to get the default
                # basis-vector length; 10 times the default basis-vector length equals 1, the proper standard-basis distance)
                self.zOfInitial = 10/self.speed
            else:
                # If the user is not holding a point, create a new line from the nearest point to the helmet (0,0)
                self.linePointIndices = append(self.linePointIndices,[[nearestPointIndex],[self.pointLocations.shape[1]]],axis=1)
                # Additionally, save the (observer-basis) z-value from the nearest point (it will be used to coordinate the placement
                # of the new point)
                self.translate()
                self.zOfInitial = self.pointLocations[2,nearestPointIndex]
            self.holdingPoint = not self.holdingPoint
            self.paint(canvas)
        #\/ If 'r' is pressed in helmet mode (new point)
        if key == 82 and self.helmet:
            # Create a new point
            self.originalPointLocations = append(self.originalPointLocations,add(multiply(self.observerBasisVectors[ix_([0,1,2],[2])],[[self.zOfInitial]]),self.observerLocation),axis=1)
            self.n+=1
            if self.holdingPoint:
                # If the user is holding a point, connect the line to the newly created point
                self.linePointIndices[1,self.linePointIndices.shape[1]-1] = self.originalPointLocations.shape[1]-1
                # Additionally, reset the previously-saved z-value to its default of 10 (10 times the default basis-vector length
                # equals 1, the default standard-basis distance)
                self.zOfInitial = 10/self.speed
            else:
                # If the user is not holding a point, create a new line from the newly created point to the helmet (0,0)
                self.linePointIndices = append(self.linePointIndices,[[self.originalPointLocations.shape[1]-1],[self.originalPointLocations.shape[1]]],axis=1)
            # Update pointLocations from originalPointLocations (this is necessary not because the observer has moved but because
            # a new point has been added to originalPointLocations that needs to be reflected in pointLocations)
            self.holdingPoint = not self.holdingPoint
            self.translate()
            self.paint(canvas)
        
    def toggleHelmet(self):
        '''
        Turn on and off editor mode
        '''
        # Toggle our flag variable to keep track of our state
        self.helmet = not self.helmet
        # Determine whether the user is in editor mode
        # (Here we find the conflation of self.speed. In the constructor, it is used as the initial value. In toggleHelmet, it is repurposed as a multiplier. Therefore, the two instances of self.speed below must be reciprocals, so that two
        # toggles will return the speed to its original value)
        if self.helmet:
            # Set the speed multiplier
            self.speed = 0.5
            # Set the new rotation speed (not a multiplier)
            self.angle = self.angle/2
        else:
            # Set the speed multiplier
            self.speed = 2
            # Set the new rotation speed (not a multiplier)
            self.angle = self.angle*2
        # Update our user bases and our rotation matrices to reflect the change in speed and rotation speed, respectively
        self.observerBasisVectors = multiply(self.observerBasisVectors,matrix([[self.speed]]))
        self.chainBasisVectors = multiply(self.chainBasisVectors,matrix([[self.speed]]))
        self.pitchDown = matrix([[1,0,0],[0,cos(self.angle),-sin(self.angle)],[0,sin(self.angle),cos(self.angle)]])
        self.pitchUp = matrix([[1,0,0],[0,cos(self.angle),sin(self.angle)],[0,-sin(self.angle),cos(self.angle)]])
        self.yawLeft = matrix([[cos(self.angle),0,-sin(self.angle)],[0,1,0],[sin(self.angle),0,cos(self.angle)]])
        self.yawRight = matrix([[cos(self.angle),0,sin(self.angle)],[0,1,0],[-sin(self.angle),0,cos(self.angle)]])

    def forward(self):
        '''
        Move one step FORWARD (normal). The length of one step is the length of one/each vector of the chain basis. 
        '''
        self.observerLocation = add(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[2])])

    def forwardFloat(self):
        '''
        Move one step FORWARD (as a floating head). The length of one step is the length of one/each vector of the observer basis. 
        '''
        self.observerLocation = add(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[2])])
    
    def backward(self):
        '''
        Move one step BACKWARD (normal). The length of one step is the length of one/each vector of the chain basis. 
        '''
        self.observerLocation = subtract(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[2])])

    def backwardFloat(self):
        '''
        Move one step BACKWARD (as a floating head). The length of one step is the length of one/each vector of the observer basis. 
        '''
        self.observerLocation = subtract(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[2])])
    
    def left(self):
        '''
        Move one step LEFT (normal). The length of one step is the length of one/each vector of the chain basis. 
        '''
        self.observerLocation = subtract(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[0])])

    def leftFloat(self):
        '''
        Move one step LEFT (as a floating head). The length of one step is the length of one/each vector of the observer basis. 
        '''
        self.observerLocation = subtract(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[0])])
    
    def right(self):
        '''
        Move one step RIGHT (normal). The length of one step is the length of one/each vector of the chain basis. 
        '''
        self.observerLocation = add(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[0])])

    def rightFloat(self):
        '''
        Move one step RIGHT (as a floating head). The length of one step is the length of one/each vector of the observer basis. 
        '''
        self.observerLocation = add(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[0])])
    
    def up(self):
        '''
        Move one step UP (normal). The length of one step is the length of one/each vector of the chain basis. 
        '''
        self.observerLocation = add(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[1])])
    
    def upFloat(self):
        '''
        Move one step UP (as a floating head). The length of one step is the length of one/each vector of the observer basis. 
        '''
        self.observerLocation = add(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[1])])
    
    def down(self):
        '''
        Move one step DOWN (normal). The length of one step is the length of one/each vector of the chain basis. 
        '''
        self.observerLocation = subtract(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[1])])

    def downFloat(self):
        '''
        Move one step DOWN (as a floating head). The length of one step is the length of one/each vector of the observer basis. 
        '''
        self.observerLocation = subtract(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[1])])

    def lookUp(self):
        '''
        INCREASE pitch angle, if within bounds.
        '''
        if self.anglePitchedAt<1.55:
            self.observerBasisVectors = self.observerBasisVectors@self.pitchUp
            self.anglePitchedAt+=self.angle

    def lookUpFloat(self):
        '''
        INCREASE pitch angle, with no bounds. ######### NEEDS EDITING TO ACCOUNT FOR CHAIN BASIS
        '''
        self.observerBasisVectors = self.observerBasisVectors@self.pitchUp
    
    def lookDown(self):
        '''
        DECREASE pitch angle, if within bounds.
        '''
        if self.anglePitchedAt>-1.55:
            self.observerBasisVectors = self.observerBasisVectors@self.pitchDown
            self.anglePitchedAt-=self.angle
    
    def lookDownFloat(self):
        '''
        DECREASE pitch angle, with no bounds. ######### NEEDS EDITING TO ACCOUNT FOR CHAIN BASIS
        '''
        self.observerBasisVectors = self.observerBasisVectors@self.pitchDown

    def lookLeft(self):
        '''
        Increment yaw toward the left (normal).
        '''
        self.observerBasisVectors = self.chainBasisVectors@self.yawLeft@linalg.inv(self.chainBasisVectors)@self.observerBasisVectors
        self.chainBasisVectors = self.yawLeft@self.chainBasisVectors

    def lookLeftFloat(self):
        '''
        Increment yaw toward the left (as a floating head). ########## NEEDS EDITING TO ACCOUNT FOR CHAIN BASIS
        '''
        self.observerBasisVectors = self.observerBasisVectors@self.yawLeft
        self.chainBasisVectors = self.yawLeft@self.chainBasisVectors ### edit here (here's a beginning of a plan. measure the forward observerBasisVector in the chain basis. take the forward component. that is your adjacent side. one is the hypotenuse. therefore, take inverseCos(fwd comp) to get the angle between forwardChainBasisVector and where it needs to be. then, yaw chainbasis by that angle. positive or negative? not sure yet. use the sign of the left-right component to determine that) not quite. fixed plan is on paper, needs to be augmented to support pitch retention when switching between modes. This plan might actually be more overcomplicated since chain basis only needs to be updated when switching back to standard mode from floating head. it can be re-established logically from scratch
    
    def lookRight(self):
        '''
        Increment yaw toward the right (normal). 
        '''
        self.observerBasisVectors = self.observerBasisVectors@self.yawRight
        self.chainBasisVectors = self.yawRight@self.chainBasisVectors ### edit here
    
    def lookRightFloat(self):
        '''
        Increment yaw toward the right (as a floating head). ########## NEEDS EDITING TO ACCOUNT FOR CHAIN BASIS
        '''
        self.observerBasisVectors = self.chainBasisVectors@self.yawRight
        self.chainBasisVectors = self.yawRight@self.chainBasisVectors ### edit here


    def translate(self):
        '''
        Update pointLocations (such that it reflects the points in originalPointLocations as viewed from the observer)
        '''
        # Perform a translation to reflect the position of the observer
        self.pointLocations = subtract(self.originalPointLocations,self.observerLocation)
        # Perform a change of basis to reflect the orientation of the observer
        self.pointLocations = linalg.inv(self.observerBasisVectors)@self.pointLocations

    def getIndexOfNearestPointToCenter(self):
        '''
        Identify the nearest point to where the user is looking (does not eliminate points behind the user yet)
        '''
        # Capture the one norm of each projected point in 2d
        oneNorms = matrix([[1,1]])@absolute(self.project())
        # Find and return the index of the point with the minimum one norm (this index corresponds to that same point in
        # pointLocations and originalPointLocations)
        min = Inf
        minIndex = -1
        for i in range(0,self.n):
            if oneNorms[0,i]<min:
                min = oneNorms[0,i]
                minIndex = i
        return minIndex

    def none(self):
        '''
        Perform no move. This is necessary so that irrelevant keys can still be directed without throwing an exception
        '''
        pass

