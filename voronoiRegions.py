import matplotlib.pyplot as plt
import numpy,math,random

dim = 2048
numPoints = 15
machine_epsilon = 0.1

def zeroish(x):
    return abs(x) < machine_epsilon

def manhattanDist(pt1,pt2):
    return abs(pt1[0]-pt2[0])+abs(pt1[1]-pt2[1])


class VoronoiPt:
    def __init__(self,pt,shade):
        self.pt=pt
        self.shade=shade

class SupplyCenter:
    def __init__(self,pt,colorList):
        self.pt=pt
        self.colorList=colorList

def voronoiShade(pixel,voronoiPts):
    closestPoint = sorted(voronoiPts,key=lambda vp: manhattanDist(vp.pt,pixel))[0]
    return closestPoint.shade

def advVoronoiShade(pixel,voronoiPts,supplyCenters):
    closestSC = sorted(supplyCenters,key=lambda sc: manhattanDist(sc.pt,pixel))[0]

    return numpy.array(closestSC.colorList) * voronoiShade(pixel,voronoiPts)



voronoiPts = [ VoronoiPt((random.randint(0,dim),random.randint(0,dim)),random.random()) for _ in range(numPoints) ]


supplyCenters = [ SupplyCenter((random.randint(0,dim),random.randint(0,dim)),[1,0,0]),SupplyCenter((random.randint(0,dim),random.randint(0,dim)),[0,1,0]),SupplyCenter((random.randint(0,dim),random.randint(0,dim)),[0,0,1]),SupplyCenter((random.randint(0,dim),random.randint(0,dim)),[1,1,0]),SupplyCenter((random.randint(0,dim),random.randint(0,dim)),[1,0,1]) ]


img = numpy.zeros((dim,dim,3))

for x in range(dim):
    print(x)
    for y in range(dim):
        #img[x][y] = numpy.array([0,voronoiShade((x,y),voronoiPts),0])
        img[x][y] = advVoronoiShade((x,y),voronoiPts,supplyCenters) 

for sc in supplyCenters:
    plt.plot(sc.pt[1],sc.pt[0],'wo')

plt.imshow(img,interpolation='none',origin='lower')
plt.plot(0,0)
plt.show()
