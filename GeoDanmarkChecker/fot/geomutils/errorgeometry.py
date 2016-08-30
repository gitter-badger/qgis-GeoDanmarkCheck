from . import togeometry, extractassingle, shortestline, tocoordinates
from qgis.core import QGis, QgsGeometry

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
        if fromgeom and length > 2 * MARKER_SHRINK_SIZE:
            # 'shrink' line by x meters in each end
            p0 = g.interpolate(MARKER_SHRINK_SIZE)
            p1 = g.interpolate (length - MARKER_SHRINK_SIZE)
            coords = tocoordinates(g)
            outcoords = []
            for i in len(coords):
                d = g.distanceToVertex(i)
                if MARKER_SHRINK_SIZE < d < length - MARKER_SHRINK_SIZE:
                    if not outcoords:
                        outcoords.append(p0)
                    outcoords.append(coords[i])
            outcoords.append(p1)
            shortedline = QgsGeometry.fromPolyline(outcoords)
            return shortedline.nearestPoint(fromgeom)
        else:
            return g.centroid()
    elif g.type() == QGis.Polygon:
        if fromgeom:
            return g.buffer(-1 * MARKER_SHRINK_SIZE, 8).nearestPoint(fromgeom)
        else:
            return g.pointOnSurface()

def createlinemarker(f0, f1):
    g0 = togeometry(f0)
    g1 = togeometry(f1)
    p0 = linemarkerpoint(g0, g1)
    p1 = linemarkerpoint(g1, g0)
    return QgsGeometry.fromPolyline([p0.asPoint(), p1.asPoint()])

