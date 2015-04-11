
import noise
import random
import math
import matplotlib.pyplot as plt
import numpy

dim = 100

colors = ['b','g','r','c','m','y','k']

def monotonicFunc(order): #monotonically decreasing random
    #function, of order (-order).
    const = random.random()
    if order<=0:
        return (lambda x: float(const) )
    else:
        def headFunc(x):
            if x == 0: # catch div by zero case
                return float('inf') # sometimes i fucking love python
            else:
                return float(const)/float(x**order)
        tailFunc = monotonicFunc(order-1)
        return (lambda x: headFunc(x) + tailFunc(x))


class Region:
    def __init__(self,x,y,dim,color):
        self.x=x
        self.y=y
        self.color=color
        self.monotonic = monotonicFunc(4)
        self.placeFunc = lambda xinput,yinput: self.monotonic( math.sqrt( (self.x-xinput)**2 + (self.y-yinput)**2))

        self.placeFuncMap = numpy.zeros((dim,dim))
        for x in range(dim):
            for y in range(dim):
                self.placeFuncMap[x][y] = self.placeFunc(x,y) 
                # we are addressing the arrays like this dammit



def __main__():
    
    

    regions = []
    for x in range(0,dim,int(dim/10)):
        for y in range(0,dim,int(dim/10)):
            regions.append(Region(x+random.randint(-1*int(dim/10),int(dim/10)),y+random.randint(-1*int(dim/10),int(dim/10)),dim,random.choice(colors)))



    for x in range(dim):
        for y in range(dim):
            regionScores = sorted(regions,key= lambda region: region.placeFuncMap[x][y],reverse=True) 
            #print(regionScores)
            controllingRegion = regionScores[0]
            plt.plot(x,y,controllingRegion.color+'o')
    '''ls = numpy.linspace(0.1,50,10000)
    plt.plot(ls,numpy.vectorize(r1.monotonic)(ls))
    plt.plot(ls,numpy.vectorize(r2.monotonic)(ls))'''
    plt.show()

if __name__=="__main__":
    __main__()
