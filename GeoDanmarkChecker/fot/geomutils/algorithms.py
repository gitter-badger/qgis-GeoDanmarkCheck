from qgis.core import QgsPoint
from math import sqrt
from . import togeometry, toflatcoordinates

# TODO: Write tests. Use https://github.com/postgis/postgis/blob/svn-trunk/regress/hausdorff.sql

def discretehausdorffdistance(g1,g2):
    """Calculates the discrete hausdorff distance between two geometries.
        Discrete meaning that it only considers vertices as origins.
        When the segment length goes towards zero this measure goes toward the non-discrete hausdorf distance
        """
    g1 = togeometry(g1)
    g2 = togeometry(g2)
    odist1 = orienteddistance(g1, g2)
    odist2 = orienteddistance(g2, g1)
    if odist1[0] >= odist2[0]:
        return odist1
    else:
        return odist2

def orienteddistance(g1, g2):
    """Calculates the maximum distance one must travel if you need to go from a vertex in g1 to the nearest point in g2"""
    coords1 = toflatcoordinates(g1)
    maxsqrddist = -1
    frompoint = None
    topoint = None
    for c1 in coords1:
        sqrddist, closestsegmentpoint, indexofclosestvertexafter = g2.closestSegmentWithContext(c1)
        if sqrddist < 0:
            raise Exception('closestSegmentWithContext failed')
        if sqrddist > maxsqrddist:
            maxsqrddist = sqrddist
            frompoint = QgsPoint(c1)
            topoint = closestsegmentpoint
    return sqrt(maxsqrddist), frompoint, topoint
