#quadtree space partitioning libTrueQuadSpacerary, by Jacob Roth
# in this software we will be representing all points as two-element tuples (x,y)

import random

from PIL import Image
from PIL import ImageDraw

def weighted_choice(items,weights):
    assert(len(items)==len(weights))
    rnd = random.random() * sum(weights)
    for iii in range(len(items)):
        rnd -= weights[iii]
        if rnd < 0:
            return items[iii]

def PILCoords(x,y,im):
    '''takes an x,y coordinate in normal Euclidian space and translates
    it to the image address coordinate on the PIL image im, assuming 0,0
    is at the center of the PIL image.'''
    imgwidth,imgheight = im.size
    column = x+(imgwidth/2)
    row = (imgheight/2)-y
    return row,column

class BuiltQuadSpace():
    # a quadtree region that is built up from the pixel level.

    def __init__(self,x,y,size,topleft,topright,bottomleft,bottomright):
        '''construct a BuiltQuadSpace by explictily defining its subspaces'''
        self.topleft = topleft
        self.topright = topright
        self.bottomleft = bottomleft
        self.bottomright = bottomright
        
        self.x = x
        self.y = y
        self.size = size

    def query(self,x,y):
        '''returns true or false at the point'''
        
        if x > self.x+self.size or x < self.x-self.size or y > self.y+self.size or y < self.y-self.size:
            raise ValueError("Queried outside of bounds")

        if x<= self.x and y>self.y:
            return self.topleft.query(x,y)
        elif x> self.x and y>self.y:
            return self.topright.query(x,y)

        elif x<= self.x and y<=self.y:
            return self.bottomleft.query(x,y)
        elif x> self.x and y<=self.y:
            return self.bottomright.query(x,y)

    def randomPointWithin(self): 
        '''returns a random point within the "True" region of the BuiltQuadSpace. The BuiltQuadSpace must have some true regions or this will crash.'''
        quadrants = [self.topleft,self.topright,self.bottomleft,self.bottomright]
        selectedQuadrant = weighted_choice(quadrants,[ quadrant.percentFull() for quadrant in quadrants]) # pick a quadrant at random, weighting based on how full that quadrant is (a quadrant with more full space should be picked more often. A FalseQuadUnit should never be picked (weight 0)).
        return selectedQuadrant.randomPointWithin() # recur until we hit a TrueSubUnit that gives us a random point within itself. 
    def percentFull(self):
        ''' returns what percent of the builtQuadSpace is True '''
        return (self.topleft.percentFull()+self.topright.percentFull()+self.bottomleft.percentFull()+self.bottomright.percentFull())/4

    def PILRender(self,draw):
        '''draws this BuiltQuadUnit onto the provided PIL draw space recursively'''
        quadrants = [self.topleft,self.topright,self.bottomright,self.bottomleft]
        for quadrant in quadrants:
            quadrant.PILRender(draw)

    def producePILImage(self):
        '''return a Python Imaging Library image of myself.'''
        im = Image.new("RGB",(self.size*2,self.size*2),"white")
        draw= ImageDraw.Draw(im)
        self.PILRender(draw)
        del draw
        return im


    @classmethod # make a constructor that works by returning 
    def constructRecursively(cls,x,y,size,constructionFunc,resolution=1):
        '''iterate over the entire square space defined by x,y, and size
        to construct a BuiltQuadSpace that defines where in that space
        constructionFunc is true. it's recommended that size be a power of
        two so we have integer sizes all the way down to 1.'''
        if size<=resolution: # we won't be recursing any further. Make a decision and return true or false
            if constructionFunc(x,y):
                return TrueQuadSpace(x,y,size)
            else:
                return FalseQuadSpace(x,y,size)
                

        halfsize = size/2
        topleft = BuiltQuadSpace.constructRecursively(x-halfsize,y+halfsize,halfsize,constructionFunc,resolution)
        topright = BuiltQuadSpace.constructRecursively(x+halfsize,y+halfsize,halfsize,constructionFunc,resolution)
        bottomleft = BuiltQuadSpace.constructRecursively(x-halfsize,y-halfsize,halfsize,constructionFunc,resolution)
        bottomright = BuiltQuadSpace.constructRecursively(x+halfsize,y-halfsize,halfsize,constructionFunc,resolution)

        if all(map(lambda quadspace: isinstance(quadspace,TrueQuadSpace),[topleft,topright,bottomleft,bottomright])): #if all four quadrants are contiguous true, we are contiguous true
            return TrueQuadSpace(x,y,size) 
        elif all(map(lambda quadspace: isinstance(quadspace,TrueQuadSpace),[topleft,topright,bottomleft,bottomright])): #if all four quadrants are contiguous false, we are contiguous false 
            return FalseQuadSpace(x,y,size)
        else: # mixed subspace
            return cls(x,y,size,topleft,topright,bottomleft,bottomright)

class TrueQuadSpace(BuiltQuadSpace):
    ''' represents a block on which the construction function is true'''
    def __init__(self,x,y,size):
        self.x =x
        self.y=y
        self.size=size
    def query(self,x,y):
        return True
    
    def percentFull(self):
        return 1 # 100% true
    def randomPointWithin(self): 
        return random.uniform(self.x-self.size,self.x+self.size),random.uniform(self.y-self.size,self.y+self.size)
    def PILRender(self,draw):
        draw.rectangle([PILCoords(self.x-self.size,self.y-self.size,draw.im),PILCoords(self.x+self.size,self.y+self.size,draw.im)],fill="black")

class FalseQuadSpace(BuiltQuadSpace):
    ''' represents a block on which the construction function is false'''
    def __init__(self,x,y,size):
        self.x =x
        self.y=y
    def query(self,x,y):
        return False
        self.size=size
    def randomPointWithin(self): 
        raise TypeError("Attempted to get a random point inside a false quadspace. This means you did something wrong.")
    def PILRender(self,draw):
        pass # do nothing, we are a false space

    def percentFull(self):
        return 0 # 0% true
