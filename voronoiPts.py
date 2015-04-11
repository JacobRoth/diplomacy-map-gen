import matplotlib.pyplot as plt
import numpy,math,random

dim = 4096
numPoints = 30
machine_epsilon = 0.1

def zeroish(x):
    return abs(x) < machine_epsilon

def manhattanDist(pt1,pt2):
    return abs(pt1[0]-pt2[0])+abs(pt1[1]-pt2[1])
    
def chebyshevDist(pt1,pt2):
    return(abs(pt1[0]-pt2[0]),abs(pt1[1]-pt2[1]))

def funkDist(pt1,pt2):
    return (math.sqrt(abs(pt1[0]-pt2[0]))+math.sqrt(abs(pt1[1]-pt2[1])))**2


class voronoiPt:
    def __init__(self,pt,shade):
        self.pt=pt
        self.shade=shade

def voronoiShade(pixel,voronoiPts):
    closestPoint = sorted(voronoiPts,key=lambda vp: manhattanDist(vp.pt,pixel))[0]
    return closestPoint.shade


voronoiPts = [ voronoiPt((random.randint(0,dim),random.randint(0,dim)),random.random()) for _ in range(numPoints) ]

img = numpy.zeros((dim,dim,3))

for x in range(dim):
    print(x)
    for y in range(dim):
        img[x][y] = numpy.array([0,voronoiShade((x,y),voronoiPts),0])

plt.imshow(img,interpolation='none',origin='lower').set_cmap('hot')
plt.plot(0,0)
plt.show()
