import Polygon
import Polygon.IO
import scipy.spatial
import random
import numpy

from simplex import SimplexNoise 
from colorized_voronoi import voronoi_finite_polygons_2d

FAR = 100 # ok, this merits a little explanation. Voronoi diagrams have several points we need to make use of that are located infinitely far away from the diagram in some direction. The function voronoi_finite_polygons puts these points some finite distance away from the diagram, so we use FAR units. A typical diplomacy map in this program will be 1 or maybe 2 units wide, so 100 units is very far away.

class ColorfulPolygon(Polygon.Polygon):
    '''Polygon that has fill and stroke color attributes. We'll use this throughout the program.'''
    def __init__(self, *args, **kwargs):
        Polygon.Polygon.__init__(self,*args,**kwargs)
        self.fill_color = (255,255,255) # defaults to white fill,
        self.stroke_color= (0,0,0) # black lines

def randomInRange(lower,upper):
    return lower+random.random()*(upper-lower)

def randomPointWithin(polygon):
    '''returns a random point inside of the polygon'''
    xmin,xmax,ymin,ymax = polygon.boundingBox() # this is the search space
    while(True): #loop forever until we get a valid result. Should take a couple of iterations on most sane-shaped polygons.
        xtest = randomInRange(xmin,xmax)
        ytest =  randomInRange(ymin,ymax)
        if polygon.isInside(xtest,ytest): # found a match!
            return xtest,ytest

def voronoiSegmentation(polygon,npoints):
    ''' returns a list of polygons that segment polygon into npoints regions. npoints must be an integer greater than two.'''
    assert(npoints>2)
    points = [randomPointWithin(polygon) for _ in range(npoints) ]
    voronoiDiagram = scipy.spatial.Voronoi(points)
    regions,vertices = voronoi_finite_polygons_2d(voronoiDiagram,radius=FAR) # read the main function in the file colorized_voronoi for an idea of what's going on here 
    bigPolygons = [ ColorfulPolygon([ vertices[point] for point in region]) for region in regions] # okay, nested listcomp. So what happens here is each region returned from voronoi_finite_polygons_2d becomes a Polygon library polygon. This polygon is constructed from the appropriate vertices of the voronoi diagram for said region. (A region is represented as something like [2,0,5], meaning it is a polynomial constructed from voronoi vertices 2, 0, and 5, in that order)

    return [ ColorfulPolygon(polygon & bigPolygon) for bigPolygon in bigPolygons ] # iterate over the big polygons and take the intersection (&) of each big polygon and the polgyon to be segmented. We have to cast the result to ColorfulPolygon because the '&' operator returns cPolygon.Polygon. (I have no idea why that cast operation works. Python, man.)


class DiploMap:
    def __init__(self,widthToHeightRatio, sealevel, mountainlevel, numPlayerCountries, totalCountries, regionsPerCountry):
        '''Generate a diplomacy map. This algorithm generates terrain first, and allocates the player countries out of land only. It should look more organic.'''

        diploMap = ColorfulPolygon([ (0,0), (widthToHeightRatio,0),(widthToHeightRatio,1),(0,1) ]) # this is the game board

        assert(numPlayerCountries <= totalCountries)

        # Let's make the geography first:

        isEnoughLand = False 
        while not isEnoughLand:
            bigSpaces = voronoiSegmentation(diploMap,totalCountries) # land regions, mountains, and seas.
            seaSpaces = []
            landSpaces = []
            mountainSpaces = []
            noiseGen  = SimplexNoise(period=widthToHeightRatio)
            for bigSpace in bigSpaces: 
                rndx,rndy = randomPointWithin(bigSpace)
                elevation = noiseGen.noise2(2*rndx/widthToHeightRatio,2*rndy) # float division
                if elevation < sealevel:
                    seaSpaces.append(bigSpace)
                elif elevation < mountainlevel:
                    landSpaces.append(bigSpace)
                else:
                    mountainSpaces.append(bigSpace)
                # let's first confirm that there is enough land for all players
            isEnoughLand = (len(landSpaces) >= numPlayerCountries)
            if not isEnoughLand:
                print("There weren't enough land spaces to allocate all players. Regenerating geography...")

        # now we need to decide which of these are players.
        playerCountries = landSpaces[:numPlayerCountries]
        neutralLandSpaces = landSpaces[numPlayerCountries:]

        # now all the regions are made, and we have to segment the land.
        self.neutralLandRegions = sum([ voronoiSegmentation(space,regionsPerCountry) for space in neutralLandSpaces ],[])
        self.playerRegions = [ voronoiSegmentation(country,regionsPerCountry) for country in playerCountries ]
        # also save the seas and mountains to self memory (todo - make these segmented)
        self.seaSpaces = seaSpaces
        self.mountainSpaces = mountainSpaces

        #ok, now the map itself is created and we need to handle some random odds and ends. Namely, we need to give things colors.

        playerColors = [ (random.randint(0,255),random.randint(0,255),random.randint(0,255)) for _ in range(numPlayerCountries) ]
        for iii in range(numPlayerCountries):
            for region in self.playerRegions[iii]:
                region.fill_color = playerColors[iii] 
        for seaSpace in self.seaSpaces:
            seaSpace.fill_color = (0,0,255) # deep blue sea
        for mountainSpace in self.mountainSpaces:
            mountainSpace.fill_color = (255,255,255) # snow-capped mountain
        for neutralLandRegion in self.neutralLandRegions:
            neutralLandRegion.fill_color = (255,200,150) # like they are on the diplomacy board.

    def render(self,filename):
        polygonsToBeRendered = self.seaSpaces+self.mountainSpaces+self.neutralLandRegions+sum(self.playerRegions,[])
        Polygon.IO.writeSVG(filename,[Polygon.Polygon(p[0]) for p in polygonsToBeRendered],fill_color=[item.fill_color for item in polygonsToBeRendered]) # what that second argument is doing is iteration over all the colorful polygons and making vanilla polygons out of them (The writeSVG function can only handle vanilla polygons)

