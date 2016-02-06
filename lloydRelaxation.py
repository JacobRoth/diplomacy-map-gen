import Polygon
import Polygon.IO
import scipy.spatial
import random
import numpy

from colorized_voronoi import voronoi_finite_polygons_2d

# diplomacy map generator program.
# Daniel Sonner
# Jacob Roth
# Marina Knittel
# Sarah Hale

FAR = 100 # ok, this merits a little explanation. Voronoi diagrams have several points we need to make use of that are located infinitely far away from the diagram in some direction. The function voronoi_finite_polygons puts these points some finite distance away from the diagram, so we use FAR units. A typical diplomacy map in this program will be 1 or maybe 2 units wide, so 100 units is very far away.

def voronoiPolynomials(points,boundingPolygon ):
    '''constructs a proper Voronoi diagram (out to FAR) for the points'''
    
    assert(len(points)>2)
    voronoiDiagram = scipy.spatial.Voronoi(points)
    regions,vertices = voronoi_finite_polygons_2d(voronoiDiagram,radius=FAR) # read the main function in the file colorized_voronoi for an idea of what's going on here 
    fullPolygons = [ Polygon.Polygon([ vertices[point] for point in region]) for region in regions] # okay, nested listcomp. So what happens here is each region returned from voronoi_finite_polygons_2d becomes a Polygon library polygon. This polygon is constructed from the appropriate vertices of the voronoi diagram for said region. (A region is represented as something like [2,0,5], meaning it is a polynomial constructed from voronoi vertices 2, 0, and 5, in that order)
    return [Polygon.Polygon(item & boundingPolygon) for item in fullPolygons] 




def lloydRelaxation(points, iterations, boundingPolygon=Polygon.Polygon([ (0,0), (1,0),(1,1),(0,1) ])):
    '''do iterations of Lloyd's Relaxation on the points to make them less random. Does not preserve the order of the points'''
    if iterations<=0:
        return points # base case
    vpolys = voronoiPolynomials(points,boundingPolygon)
    return lloydRelaxation([ poly.center()  for poly in vpolys ] , iterations-1, boundingPolygon)

def main():
    import matplotlib.pyplot as plt
    initialPoints = [ (random.random(), random.random()) for _ in range(40) ]
    relaxedPoints = lloydRelaxation(initialPoints,2)
    plt.plot([tup[0] for tup in initialPoints],[tup[1] for tup in initialPoints],"r+")
    plt.plot([tup[0] for tup in relaxedPoints],[tup[1] for tup in relaxedPoints],"bo")
    plt.show()

if __name__=="__main__":
    main()

