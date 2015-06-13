import random,numpy

def randomPointWithin(boolArray):
    '''takes a numpy array full of booleans and returns
    a random row,column where the array is True. Must
    be given a boolArray that contains a True somewhere.'''
    assert(True in boolArray) # confirm that the boolArray contains True.
    while (True): # note that this will take awhile for large arrays containing small True spaces
        rndrow = random.randint(0,boolArray.shape[0]-1)
        rndcol = random.randint(0,boolArray.shape[1]-1)
        if boolArray[rndrow][rndcol]:
            return rndrow,rndcol

def distsquared(pt1,pt2):
    return (pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2

def voronoiSegmentation(boolArray, numpts):
    voronoiPoints = [ randomPointWithin(boolArray) for _ in range(numpts) ]
    segments = [] # the regions we will return, represented as boolArrays
    for iii in range(len(voronoiPoints)): 
        def voronoiFunc(row,col): # function that we create for each voronoi point to find otu if any (row,col) is part of that point's voronoi region.
            if not boolArray[row][col]: # if the point row, col is not part of the region to be segmented,
                return False  #  it sure isn't in one of the segments.
            else:
                distsquaredToCurrentPoint = distsquared((row,col),voronoiPoints[iii])
                for vpt in voronoiPoints[0:iii]+voronoiPoints[iii+1:]: #iterate over all voronoi points that are not the current point
                    if distsquared((row,col),vpt) < distsquaredToCurrentPoint: # current point is not the closest point
                        return False
                return True # if no closer point found, we are in region.

        segments.append(numpy.fromfunction(numpy.vectorize(voronoiFunc),boolArray.shape))
    return segments

