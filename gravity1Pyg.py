import pygame
import math as maths
import random
# initialise
# pygame:
pygame.init()
clock = pygame.time.Clock()
win = pygame.display.set_mode((1500,1000))
pygame.display.set_caption('gravity')
run = True
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)
adjX = 0
adjY = 0

# physics:
GRAV_CONST = 10
MAX_SPEED = 100000000

class object():
    def __init__(self, mass, startPos, colour="grey", debug=False) -> None:
        self.mass = mass
        self.forcesDict = {} # key = object, value = gravitational force (newtons)
        self.gravVector = [0,0] # a vector of the resultant gravitational force
        self.velocity = [0,0] # vector for the resultant velocity
        self.position = startPos
        self.colour = colour
        self.debug = debug
    def findGravForces(self, objectList):
        global GRAV_CONST
        newDict = {}
        for obj in objectList:
            if obj != self:
                if obj in self.forcesDict: # if force has been updated by object first
                    newDict[obj] = self.forcesDict[obj]
                else:
                    Gmm = GRAV_CONST * self.mass * obj.mass
                    r_sqrd = ((self.position[0] - obj.position[0])**2 
                        + (self.position[1] - obj.position[1])**2)
                    r_sqrd = min(max(r_sqrd, 1), 100) # no extreme values - bit cheaty for r^2 will always be 100
                    F_g = (Gmm)/(r_sqrd) # newton's gravitational equation
                    if self.debug:
                        print("r", maths.sqrt(r_sqrd))
                        print("f_g", F_g)
                    # update the force for both objects involved
                    newDict[obj] = F_g
                    obj.forcesDict[self] = F_g
        self.forcesDict = newDict.copy()
    def resolveGravForces(self):
        self.gravVector = [0,0]
        for obj in self.forcesDict:
            # [difX, difY] is a vector between the two objects' coordinates
            # as only the direction between the two objects is wanted, not the magnitude, the vector is normalised.
            difVec = [obj.position[0] - self.position[0], obj.position[1] - self.position[1]]
            difVec = normalise(difVec)
            # set the magnitude to the gravitational force between the two objects
            forceX = difVec[0] * self.forcesDict[obj]
            forceY = difVec[1] * self.forcesDict[obj]
            # add the combined direction-vector-with-gravitational-force-magnitude to resultant vector
            self.gravVector[0] += forceX
            self.gravVector[1] += forceY
            if self.debug:
                pygame.draw.line(win, "green", (self.position[0]+adjX, self.position[1]+adjY), (
                    (self.position[0]+adjX)+forceX*100, 
                    (self.position[1]+adjY)+forceY*100
                    ),width=10)
                print(self.forcesDict[obj])
        if self.debug:
            pygame.draw.line(win, "yellow", (self.position[0]+adjX, self.position[1]+adjY), (
                (self.position[0]+adjX)+self.gravVector[0]*100, 
                (self.position[1]+adjY)+self.gravVector[1]*100
                ),width=3)
    def calcVelocity(self):
        # calculate accel[eration] due to gravity using F=ma (newton's 2nd law)
        accel = [self.gravVector[0]/self.mass, self.gravVector[1]/self.mass]
        # calculate velocity (in pixels per frame)
        self.velocity[0] += accel[0]
        self.velocity[1] += accel[1]
    def updatePos(self):
        global MAX_SPEED
        # update pygame
        pygame.draw.circle(win, self.colour, (self.position[0]+adjX, self.position[1]+adjY), self.mass)
        # cap the cumulative velocity
        currentVelocityMag = maths.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        targetVelocityMag = min(currentVelocityMag, MAX_SPEED)
        div = targetVelocityMag / currentVelocityMag
        self.velocity[0] *= div
        self.velocity[1] *= div
        if self.debug:
            print("velocity", self.velocity)
            pygame.draw.line(win, "blue", (self.position[0]+adjX, self.position[1]+adjY), (
                (self.position[0]+adjX) + self.velocity[0]*100, 
                (self.position[1]+adjY) + self.velocity[1]*100
                ))
        # update the position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        # clear the forces dictionary
        self.forcesDict = {}

def normalise(vector):
    # see: https://www.khanacademy.org/computing/computer-programming/programming-natural-simulations...
    # .../programming-vectors/a/vector-magnitude-normalization
    difMag = maths.sqrt(vector[0]**2 + vector[1]**2)
    vector[0] /= difMag
    vector[1] /= difMag
    return vector

def update_fps():
	fps = str(int(clock.get_fps()))
	fps_text = font.render(fps, 1, pygame.Color("coral"))
	return fps_text

objectList = [
    object(5,[110,200],colour="red",debug=True),
    object(50,[600,400],colour="white"),
    object(5,[200,600],colour="orange")
]
#objectList = []

# random objects:
'''for i in range(4):
    objectList.append(object(
        random.randint(1,50),
        [random.randint(100,900),random.randint(100,900)]
    ))'''

while run:
    pygame.time.delay(100)
    win.fill((0,0,0))
    win.blit(update_fps(), (10,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                adjX += 300
            if event.key == pygame.K_RIGHT:
                adjX -= 300
            if event.key == pygame.K_UP:
                adjY += 300
            if event.key == pygame.K_DOWN:
                adjY -= 300
    for obj in objectList:
        obj.findGravForces(objectList)
        obj.resolveGravForces()
        obj.calcVelocity()
    for obj in objectList:
        obj.updatePos()
    clock.tick(60)
    pygame.display.flip()