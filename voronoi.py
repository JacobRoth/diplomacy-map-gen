from quadspace import *
from PIL import Image,ImageDraw
import random
from noise import snoise2 # todo - builtin library

def distsquared(pt1,pt2):
    return (pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2


def voronoiSegmentation(bqs,numpts): 
    ''' takes a BuiltQuadSpace and segments it into voronoi polynomials,
    returning a list of these polynomials represented as BuiltQuadSpaces'''
    voronoiPoints = [ bqs.randomPointWithin() for iii in range(numpts) ]
    voronoiRegions = []
    for iii in range(len(voronoiPoints)):
        def isInCurrentRegion(x,y):
            ''' function that we create for each voronoi Point to find out if any (x,y) is part of that point's voronoi region'''
            if not bqs.query(x,y):
                return False # immediately determine that points outside the \parent\ region are invalid
            else:

                '''
                distsquareds = [ distsquared((x,y),vpt) for vpt in voronoiPoints ] # calculate the distance to every voronoi point from this x,y
                return min(distsquareds)==distsquareds[iii] # if the minimum distance to a point is the distance to this point, return true.
                # todo - make that less naive by iterating over voronoiPoints not our own and returning False as soon as we find one too big.'''
                
                #now we are going to write the less naive version
                distsquaredToCurrentPoint = distsquared((x,y),voronoiPoints[iii]) # distance to this point
                for vpt in voronoiPoints[0:iii]+voronoiPoints[iii+1:]: #iterate over all voronoi points that are not the current point
                    if distsquared((x,y),vpt) < distsquaredToCurrentPoint: # current point is not the closest point
                        return False
                return True # if no closer point found, we are in region

        voronoiRegions.append(BuiltQuadSpace.constructRecursively(bqs.x,bqs.y,bqs.size,isInCurrentRegion,color=None )) #we'll set color later
    return voronoiRegions

def landWaterVoronoi(sz,num):
    space = BuiltQuadSpace.constructRecursively(0,0,sz,lambda x,y:True,color="white",resolution=4)
    v = voronoiSegmentation(space,num)
    for item in v:
        pointX, pointY = item.randomPointWithin()
        elevation = snoise2(pointX/sz,pointY/sz)
        if  elevation < 0:
            item.setColor( (0,0,random.randint(100,255)) ) # ocean (blue)
        elif  elevation < 0.6:
            item.setColor( (0,random.randint(100,255),0) ) # land (green)
        else:
            item.setColor( "grey" ) # mountain


    return produceCompositePILImage(v)
