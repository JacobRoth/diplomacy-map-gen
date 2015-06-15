import random,numpy
import matplotlib.pyplot as plt

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
    '''take a boolArray that represents a region in space and voronoi segment it. Returns the segments as boolArray-type regions.'''
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

        segments.append(numpy.fromfunction(numpy.vectorize(voronoiFunc),boolArray.shape)) # i have no idea why that requires vectorize. I saw it on stack exchange.
    return segments

def simpleColorfulImage(listOfBoolArrays):
    '''takes a list of bool-array regions, assigns them random colors, and returns a composite image that has them all. All the bool-array regions must have the same array shape'''
    assert(all(map(lambda boolArray: boolArray.shape == listOfBoolArrays[0].shape,listOfBoolArrays))) # confirm they all have the same shape.
    rgbshape = (listOfBoolArrays[0].shape[0],listOfBoolArrays[0].shape[1],3) #same height and width as the bool but it has a color dimension.
    compositeImage = numpy.zeros(rgbshape)  
    for boolArray in listOfBoolArrays:
        compositeImage += colorRegion(boolArray,numpy.array([random.randint(0,255),random.randint(0,255),random.randint(0,255)]))
    return compositeImage

def colorRegion(boolArray,colorArray):
    '''takes a boolean array and returns a color image of it in color colorArray'''
    colorImage = numpy.dstack((boolArray,boolArray,boolArray))
    return colorImage*colorArray 

def diploMap(shape, sealevel, mountainlevel, numPlayerCountries, totalCountries, regionsPerCountry):
    '''render an image of a diplomacy map. Note that totalCountries is the number of big country-sized spaces on the map, including water and mountain. Can generate for up to 7 players right now'''
    assert(numPlayerCountries <= 7)
    possibleColors = [numpy.array([1.0,0,0]),numpy.array([0,1.0,0]),numpy.array([0,0,1.0]),numpy.array([1.0,1.0,0]),numpy.array([0,1.0,1.0]),numpy.array([1.0,0,1.0]) ] 
    diploMap = numpy.full(shape,True,bool) # numpy array representing the whole space.
    diploCanvas = numpy.zeros((shape[0],shape[1],3)) # create a color numpy array image that is the blank canvas we will draw everything on.

    # ok now we start the numerical heavy lifting

    bigSpaces = voronoiSegmentation(diploMap,totalCountries) # land regions, mountains, and seas.
    # now we need to separate the bigSpaces into player lands and neutral stuff. First we shuffle:
    random.shuffle(bigSpaces) # shuffles in place!
    playerCountries = bigSpaces[:numPlayerCountries]
    neutralBigSpaces = bigSpaces[numPlayerCountries:]
    
    #now make the players' lands
    playerRegions = [ voronoiSegmentation(playerCountry,regionsPerCountry) for playerCountry in playerCountries ] # out of this we get a list of lists - the starting regions of players 0 thru numPlayerCountries-1
    
    
    #now we make neutral lands, including mountains and seas
    seaRegions = []
    neutralLandRegions = []
    mountainRegions = []
    # gonna have to do the snoise stuff here.

    for iii in range(len(playerRegions)): #now we draw the players' lands into the canvas 
        for region in playerRegions[iii]: # iterate over this player's regions
            diploCanvas += colorRegion(region,possibleColors[iii])


    return diploCanvas
