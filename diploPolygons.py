import Polygon
import Polygon.IO
import scipy.spatial
import random
import numpy
import os

from simplex import SimplexNoise 
from colorized_voronoi import voronoi_finite_polygons_2d
from lloydRelaxation import lloydRelaxation

# diplomacy map generator program.
# Daniel Sonner
# Jacob Roth
# Marina Knittel
# Sarah Hale



FAR = 100 # ok, this merits a little explanation. Voronoi diagrams have several points we need to make use of that are located infinitely far away from the diagram in some direction. The function voronoi_finite_polygons puts these points some finite distance away from the diagram, so we use FAR units. A typical diplomacy map in this program will be 1 or maybe 2 units wide, so 100 units is very far away.

class DiplomacyPolygon(Polygon.Polygon):
    '''Polygon that has fill and stroke color attributes and a flag for being a supply center. We'll use this throughout the program.'''
    def __init__(self, *args, **kwargs):
        Polygon.Polygon.__init__(self,*args,**kwargs)
        self.fill_color = (255,255,255) # defaults to white fill,
        self.stroke_color= (0,0,0) # black lines
        self.isSupplyCenter = False

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
    trulyRandomPoints = [randomPointWithin(polygon) for _ in range(npoints) ]
    points = lloydRelaxation(trulyRandomPoints,2,boundingPolygon=polygon) # the ones we actually use, less random
    voronoiDiagram = scipy.spatial.Voronoi(points)
    regions,vertices = voronoi_finite_polygons_2d(voronoiDiagram,radius=FAR) # read the main function in the file colorized_voronoi for an idea of what's going on here 
    bigPolygons = [ DiplomacyPolygon([ vertices[point] for point in region]) for region in regions] # okay, nested listcomp. So what happens here is each region returned from voronoi_finite_polygons_2d becomes a Polygon library polygon. This polygon is constructed from the appropriate vertices of the voronoi diagram for said region. (A region is represented as something like [2,0,5], meaning it is a polynomial constructed from voronoi vertices 2, 0, and 5, in that order)

    return [ DiplomacyPolygon(polygon & bigPolygon) for bigPolygon in bigPolygons ] # iterate over the big polygons and take the intersection (&) of each big polygon and the polgyon to be segmented. We have to cast the result to DiplomacyPolygon because the '&' operator returns cPolygon.Polygon. (I have no idea why that cast operation works. Python, man.)


class DiploMap:
    def __init__(self,widthToHeightRatio, sealevel, mountainlevel, numPlayerCountries, totalCountries, regionsPerPlayerCountry, regionsPerNeutralCountry, neutralSupplyProportion, startingSupplyCentersPerPlayer):
        '''Generate a diplomacy map. This algorithm generates terrain first, and allocates the player countries out of land only. It should look more organic.'''

        diploMap = DiplomacyPolygon([ (0,0), (widthToHeightRatio,0),(widthToHeightRatio,1),(0,1) ]) # this is the game board

        assert(numPlayerCountries <= totalCountries)

        # Let's make the geography first:

        isEnoughLand = False 
        while not isEnoughLand:
            bigSpaces = voronoiSegmentation(diploMap,totalCountries) # land regions, mountains, and seas.
            seaSpaces = []
            landSpaces = []
            mountainSpaces = []
            noiseGen  = SimplexNoise(period=int(widthToHeightRatio))
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
            #if not isEnoughLand:
            #    print("There weren't enough land spaces to allocate all players. Regenerating geography...")

        # now we need to decide which of these are players.
        random.shuffle(landSpaces)
        playerCountries = landSpaces[:numPlayerCountries]
        neutralLandSpaces = landSpaces[numPlayerCountries:]

        # now all the regions are made, and we have to segment the land.
        self.neutralLandRegions = sum([ voronoiSegmentation(space,regionsPerNeutralCountry) for space in neutralLandSpaces ],[])
        self.playerRegions = [ voronoiSegmentation(country,regionsPerPlayerCountry) for country in playerCountries ]
        # also save the seas and mountains to self memory
        self.seaSpaces = seaSpaces
        self.mountainSpaces = mountainSpaces

        #ok, now the map itself is created and we need to handle some random odds and ends. Namely, we need to give things colors, and make some things be supply centers.

        playerColors = [ (255,0,0),(255,127,0),(255,255,0),(0,255,0),(150,0,255) # rainbow, skipping over blue because that's the sea 
                        ,(255,0,255),(0,255,255),(150,150,150)] # magenta,cyan, and gray

        while numPlayerCountries > len(playerColors): # awkward, we don't have enough colors. 
            playerColors.append( (random.randint(0,255),random.randint(0,255),random.randint(0,255)) ) # Let's just make some up. This won't be as clear as using the defaults (could end up with a color that is too sea-like for example) but it will work.
        for iii in range(numPlayerCountries):
            supplyCentersSoFar = 0
            random.shuffle(self.playerRegions[iii])
            for region in self.playerRegions[iii]:
                region.fill_color = playerColors[iii] 
                if supplyCentersSoFar < startingSupplyCentersPerPlayer:
                    supplyCentersSoFar+=1
                    region.isSupplyCenter = True

        for seaSpace in self.seaSpaces:
            seaSpace.fill_color = (0,0,255) # deep blue sea
        for mountainSpace in self.mountainSpaces:
            mountainSpace.fill_color = (255,255,255) # snow-capped mountains 
        for neutralLandRegion in self.neutralLandRegions:
            neutralLandRegion.fill_color = (255,200,150) # like they are on the diplomacy board.
            if random.random() <= neutralSupplyProportion:
                neutralLandRegion.isSupplyCenter = True

    def render(self,filename):
        polygonsToBeRendered = self.seaSpaces+self.mountainSpaces+self.neutralLandRegions+sum(self.playerRegions,[])
        fill_colors=[p.fill_color for p in polygonsToBeRendered]
        supplyCenterLabels = ['.' if p.isSupplyCenter else '' for p in polygonsToBeRendered]

        Polygon.IO.writeSVG(filename,[Polygon.Polygon(p[0]) for p in polygonsToBeRendered],fill_color=fill_colors,labels=supplyCenterLabels,labels_centered=True) # what that second argument is doing is iteration over all the colorful polygons and making vanilla polygons out of them (The writeSVG function can only handle vanilla polygons)

def main():
    while True:
        d = DiploMap(4/3,0.05,.95,15,70,6,3,12/14,3)
        d.render("test.svg")
        os.system("inkview test.svg")
        i = input(">")
        if i == "":
            pass
        elif i=="q":
            break
        else:
            d.render(i)

if __name__=="__main__":
    main()
