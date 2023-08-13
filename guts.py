import random
from numpy import *
class Guts:
    def __init__(self, pointLocations, linePointIndices):
        self.angle = 1/40
        self.speed = 0.1
        self.originalPointLocations = pointLocations
        self.pointLocations = pointLocations
        self.linePointIndices = linePointIndices
        #the next three lines are for a superimposed helmet that moves alonside the face
        self.helmetPointLocations = matrix([[-0.1,-0.1,-0.1,-0.1,0.1,0.1,0.1,0.1,-0.16,-0.16,-0.16,-0.16,0.16,0.16,0.16,0.16],
                                            [-0.03,-0.03,0.03,0.03,-0.03,-0.03,0.03,0.03,-0.03,-0.03,0.03,0.03,-0.03,-0.03,0.03,0.03],
                                            [ 0.01,  1,0.01, 1,0.01,   1,0.01, 1,0.01,  1,0.01, 1,0.01,   1,0.01, 1]], float32)
        self.helmetLinePointIndices = matrix([[0,2,4,6,1,3,8,10,12,14],
                                              [1,3,5,7,5,7,9,11,13,15]])
        self.helmet = False
        #the next ___ lines are for managing the state of the adding of a point, if needed
        self.holdingPoint = False
        self.zOfFromPoint = 20
        self.observerLocation = matrix([[0],[0],[0]],float32)
        self.observerBasisVectors = multiply(matrix([[1,0,0],[0,1,0],[0,0,1]],float32),matrix([[self.speed]],float32))
        self.chainBasisVectors = multiply(matrix([[1,0,0],[0,1,0],[0,0,1]],float32),matrix([[self.speed]],float32))
        self.pitchDown = matrix([[1,0,0],[0,cos(self.angle),-sin(self.angle)],[0,sin(self.angle),cos(self.angle)]])
        self.pitchUp = matrix([[1,0,0],[0,cos(self.angle),sin(self.angle)],[0,-sin(self.angle),cos(self.angle)]])
        self.yawLeft = matrix([[cos(self.angle),0,-sin(self.angle)],[0,1,0],[sin(self.angle),0,cos(self.angle)]])
        self.yawRight = matrix([[cos(self.angle),0,sin(self.angle)],[0,1,0],[-sin(self.angle),0,cos(self.angle)]])
        self.anglePitchedAt = 0
        self.n = pointLocations.shape[1]
        # dictionary
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

    def reset(self):
        self.pointLocation = self.originalPointLocations

    def project(self):
        return divide(self.pointLocations[ix_([0,1],arange(self.n))],absolute(self.pointLocations[ix_([2],arange(self.n))]))
    
    def projectHelmet(self):
        return divide(self.helmetPointLocations[ix_([0,1],arange(16))],absolute(self.helmetPointLocations[ix_([2],arange(16))]))
    
    def paint(self, canvas):
        canvas.delete('all')
        scale = max(canvas.winfo_width(),canvas.winfo_height())
        endpoints = add(multiply(self.project(),matrix([[scale],[-1*scale]])),matrix([[canvas.winfo_width()/2],[canvas.winfo_height()/2]], float32))
        helmetEndpoints = add(multiply(self.projectHelmet(),matrix([[scale],[-1*scale]])),matrix([[canvas.winfo_width()/2],[canvas.winfo_height()/2]], float32))
        for i in range(0,self.linePointIndices.shape[1]-1):
            if not (self.pointLocations[2,self.linePointIndices[0,i]] < 0 and  self.pointLocations[2,self.linePointIndices[1,i]] < 0):
                canvas.create_line(endpoints[0,self.linePointIndices[0,i]], endpoints[1,self.linePointIndices[0,i]], endpoints[0,self.linePointIndices[1,i]], endpoints[1,self.linePointIndices[1,i]])
        #this next line is important. Currently it will draw all lines except the last. If the last line has a final index (second position)
        #that indicates a nonexistent point, the line will be drawn to zero zero
        lastLineIndex = self.linePointIndices.shape[1]-1
        if self.linePointIndices[1,lastLineIndex]==self.pointLocations.shape[1]:
            canvas.create_line(endpoints[0,self.linePointIndices[0,lastLineIndex]], endpoints[1,self.linePointIndices[0,lastLineIndex]], canvas.winfo_width()/2, canvas.winfo_height()/2)
        else:
            canvas.create_line(endpoints[0,self.linePointIndices[0,lastLineIndex]], endpoints[1,self.linePointIndices[0,lastLineIndex]], endpoints[0,self.linePointIndices[1,lastLineIndex]], endpoints[1,self.linePointIndices[1,lastLineIndex]])
            #print([endpoints[0,self.linePointIndices[0,i]], endpoints[1,self.linePointIndices[0,i]],endpoints[0,self.linePointIndices[0,i]], endpoints[1,self.linePointIndices[0,i]]])
            #canvas.create_line(random.randint(0,canvas.winfo_width()),random.randint(0,canvas.winfo_height()),random.randint(0,canvas.winfo_width()),random.randint(0,canvas.winfo_height()))
        if self.helmet:
            #for i in range(0,10):
            #    print("canvas.create_line(" + str(helmetEndpoints[0,self.helmetLinePointIndices[0,i]])+", "+str(helmetEndpoints[1,self.helmetLinePointIndices[0,i]])+", "+str(helmetEndpoints[0,self.helmetLinePointIndices[1,i]])+", "+str(helmetEndpoints[1,self.helmetLinePointIndices[1,i]])+")")
            #    canvas.create_line(helmetEndpoints[0,self.helmetLinePointIndices[0,i]], helmetEndpoints[1,self.helmetLinePointIndices[0,i]], helmetEndpoints[0,self.helmetLinePointIndices[1,i]], helmetEndpoints[1,self.helmetLinePointIndices[1,i]])
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
        for key in buttons:
            self.moveDict.get(str(key),self.moveDict['none'])()
        self.translate()
        self.paint(canvas)

    def interact(self, key, canvas):
        ####################print("interact called with key "+str(key)+": editor mode is "+str(self.helmet))
        #\/ if 'i' is pressed at any time
        if key == 73:
            self.toggleHelmet()
            self.paint(canvas)
        #\/ if 'q' is pressed in helmet mode (nearby existing point)
        if key == 81 and self.helmet:
            # find nearest point to center
            nearestPointIndex = self.getIndexOfNearestPointToCenter()
            if self.holdingPoint:
                # if user is holding a point, connect the line to the new nearest point
                self.linePointIndices[1,self.linePointIndices.shape[1]-1] = nearestPointIndex
                # additionally, reset the previously-saved z-value to its default of 10 (divide by speed to get the default basis-vector length; 10 times the default basis-vector length equals 1, the proper standard-basis distance)
                self.zOfFromPoint = 10/self.speed
            else:
                # if the user is not holding a point, create a new line from the nearest point to the helmet (0,0)
                self.linePointIndices = append(self.linePointIndices,[[nearestPointIndex],[self.pointLocations.shape[1]]],axis=1)
                # additionally, save the (observer-basis) z-value from the nearest point (it will be used to coordinate the placement of the new point)
                self.translate()
                self.zOfFromPoint = self.pointLocations[2,nearestPointIndex]
            self.holdingPoint = not self.holdingPoint
            self.paint(canvas)
        #\/ if 'r' is pressed in helmet mode (new point)
        if key == 82 and self.helmet:
            # create a new point
            self.originalPointLocations = append(self.originalPointLocations,add(multiply(self.observerBasisVectors[ix_([0,1,2],[2])],[[self.zOfFromPoint]]),self.observerLocation),axis=1)
            self.n+=1
            if self.holdingPoint:
                # if the user is holding a point, connect the line to the newly created point
                self.linePointIndices[1,self.linePointIndices.shape[1]-1] = self.originalPointLocations.shape[1]-1
                # additionally, reset the previously-saved z-value to its default of 10 (10 times the default basis-vector length equals 1, the default standard-basis distance)
                self.zOfFromPoint = 10/self.speed
            else:
                # if the user is not holding a point, create a new line from the newly created point to the helmet (0,0)
                self.linePointIndices = append(self.linePointIndices,[[self.originalPointLocations.shape[1]-1],[self.originalPointLocations.shape[1]]],axis=1)
            # translate is necessary so that pointLocations (which, to remember, are translated and in the observer basis) is refreshed to include the new point
            self.holdingPoint = not self.holdingPoint
            self.translate()
            self.paint(canvas)
        
    def toggleHelmet(self):
        self.helmet = not self.helmet
        if self.helmet:
            self.speed = 0.5
            self.angle = self.angle/2
        else:
            self.speed = 2
            self.angle = self.angle*2
        self.observerBasisVectors = multiply(self.observerBasisVectors,matrix([[self.speed]]))
        self.chainBasisVectors = multiply(self.chainBasisVectors,matrix([[self.speed]]))
        self.pitchDown = matrix([[1,0,0],[0,cos(self.angle),-sin(self.angle)],[0,sin(self.angle),cos(self.angle)]])
        self.pitchUp = matrix([[1,0,0],[0,cos(self.angle),sin(self.angle)],[0,-sin(self.angle),cos(self.angle)]])
        self.yawLeft = matrix([[cos(self.angle),0,-sin(self.angle)],[0,1,0],[sin(self.angle),0,cos(self.angle)]])
        self.yawRight = matrix([[cos(self.angle),0,sin(self.angle)],[0,1,0],[-sin(self.angle),0,cos(self.angle)]])

    def move(self, key):
        self.moveDict.get(str(key),self.moveDict['none'])()

    def forward(self):
        self.observerLocation = add(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[2])])
    
    def backward(self):
        self.observerLocation = subtract(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[2])])
    
    def left(self):
        self.observerLocation = subtract(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[0])])
    
    def right(self):
        self.observerLocation = add(self.observerLocation,self.observerBasisVectors[ix_([0,1,2],[0])])
    
    def up(self):
        self.observerLocation = add(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[1])])
    
    def down(self):
        self.observerLocation = subtract(self.observerLocation,self.chainBasisVectors[ix_([0,1,2],[1])])

    def lookUp(self):
        if self.anglePitchedAt<1.55:
            self.observerBasisVectors = self.observerBasisVectors@self.pitchUp
            self.anglePitchedAt+=self.angle
    
    def lookDown(self):
        if self.anglePitchedAt>-1.55:
            self.observerBasisVectors = self.observerBasisVectors@self.pitchDown
            self.anglePitchedAt-=self.angle

    def lookLeft(self):
        self.observerBasisVectors = self.chainBasisVectors@self.yawLeft@linalg.inv(self.chainBasisVectors)@self.observerBasisVectors
        self.chainBasisVectors = self.yawLeft@self.chainBasisVectors
    
    def lookRight(self):
        self.observerBasisVectors = self.chainBasisVectors@self.yawRight@linalg.inv(self.chainBasisVectors)@self.observerBasisVectors
        self.chainBasisVectors = self.yawRight@self.chainBasisVectors


    def translate(self):
        self.pointLocations = subtract(self.originalPointLocations,self.observerLocation)
        self.pointLocations = linalg.inv(self.observerBasisVectors)@self.pointLocations

    def getIndexOfNearestPointToCenter(self):
        oneNorms = matrix([[1,1]])@absolute(self.project())
        print(oneNorms)
        min = Inf
        minIndex = -1
        for i in range(0,self.n):
            if oneNorms[0,i]<min:
                min = oneNorms[0,i]
                minIndex = i
        return minIndex

    def none(self):
        pass

