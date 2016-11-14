from . import togeometry, extractassingle, shortestline, toflatcoordinates
from qgis.core import QGis, QgsGeometry
from math import sqrt

# Marker lines basically go to a point this far into the geometry
MARKER_SHRINK_SIZE = 0.5

def linemarkerpoint(g, fromgeom=None):
    g = extractassingle(g)
    # For now just use first geom if multiple present
    g = g[0]

    if g.type() == QGis.Point:
        return g
    elif g.type() == QGis.Line:
        length = g.length()
        # if False and fromgeom and length > 2 * MARKER_SHRINK_SIZE:
        #     # 'shrink' line by x meters in each end
        #     p0 = g.interpolate(MARKER_SHRINK_SIZE).asPoint()
        #     p1 = g.interpolate (length - MARKER_SHRINK_SIZE).asPoint()
        #     coords = tocoordinates(g)
        #     outcoords = []
        #     d = 0.0
        #     prev = coords[0]
        #     for i in range(1, len(coords)):
        #         curr = coords[i]
        #         d += sqrt(prev.sqrDist(curr))
        #         prev = curr
        #         if MARKER_SHRINK_SIZE <= d <= length - MARKER_SHRINK_SIZE:
        #             if not outcoords:
        #                 outcoords.append(p0)
        #             outcoords.append(coords[i])
        #     outcoords.append(p1)
        #     shortedline = QgsGeometry.fromPolyline(outcoords)
        #     return shortedline.nearestPoint(fromgeom)
        # else:
        return g.interpolate(length * 0.5)
    elif g.type() == QGis.Polygon:
        if fromgeom:
            buf = g.buffer(-1 * MARKER_SHRINK_SIZE, 8)
            if not buf.isGeosEmpty():
                return buf.nearestPoint(fromgeom)
            else:
                return g.pointOnSurface()
        else:
            return g.pointOnSurface()

def createlinemarker(f0, f1):
    g0 = togeometry(f0)
    g1 = togeometry(f1)
    p0 = linemarkerpoint(g0, g1)
    p1 = linemarkerpoint(g1, g0)
    geom = QgsGeometry.fromPolyline([p0.asPoint(), p1.asPoint()])
    return geom
def createpointmarker(f):
    g = togeometry(f)
    coords = toflatcoordinates(g)
    # Dont take first or last. Lines are often connected at first or last making it hard to discern
    ix = min(1, len(coords) - 1)
    return QgsGeometry.fromPoint(coords[ix])
