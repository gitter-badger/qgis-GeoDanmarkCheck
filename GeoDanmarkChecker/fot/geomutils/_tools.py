from qgis.core import QgsFeature, QgsGeometry, QGis, QgsRectangle, QgsAbstractGeometryV2
from collections import Iterable


def togeometry(f):
    """If input is feature returns the geometry of the feature.
    If input is geometry returns the input.
    Fails otherwise"""
    if isinstance(f, QgsGeometry):
        return f
    elif isinstance(f, QgsFeature):
        return f.geometry()
    elif isinstance(f, QgsAbstractGeometryV2):
        return QgsGeometry(f)
    else:
        raise TypeError("Type was not QgsGeometry or QgsFeature")


def shortestline(f1, f2):
    """Returns the shortest line between two geometries or features"""
    g1 = togeometry(f1)
    g2 = togeometry(f2)
    return g1.shortestLine(g2)


def bbox(f):
    """Returns the bbox [xmin,ymin,xmax,ymax] for a feature, a geometry, a bbox or a list of those"""
    if isinstance(f, QgsFeature) or isinstance(f, QgsGeometry):
        g = togeometry(f)
        rect = g.boundingBox()
        return [rect.xMinimum(), rect.yMinimum(), rect.xMaximum(), rect.yMaximum()]

    if isinstance(f, QgsRectangle):
        return [f.xMinimum(), f.yMinimum(), f.xMaximum(), f.yMaximum()]

    # Potentially a bbox or list of geoms or features
    if isinstance(f, (list, tuple)) and len(f) == 4:
        if all([isinstance(n, (int, float)) for n in f]):
            # This is a bbox itself
            return f
    bboxes = [bbox(o) for o in f]
    xmins, ymins, xmaxs, ymaxs = zip(*bboxes)
    return [min(xmins), min(ymins), max(xmaxs), max(ymaxs)]


def bboxoverlaps(f1, f2):
    """Inputs are either QgsGeometry, QgsFeature or a bbox [xmin,ymin,xmax,ymax]"""
    b1 = bbox(f1)
    b2 = bbox(f2)
    return b1[0] < b2[2] and b1[2] > b2[0] and b1[1] < b2[3] and b1[3] > b2[1]

def geometryequal(f1, f2, tolerance):
    """Compares geometries coordinate by coordinate using specified tolerance"""
    g1 = togeometry(f1)
    g2 = togeometry(f2)
    wkb1 = g1.wkbType()
    wkb2 = g2.wkbType()
    if wkb1 != wkb2:
        return False
    # QgsGeometry.compare only supports lines, polygons and multipolygons
    if wkb1 in (QGis.WKBMultiPoint, QGis.WKBPoint25D):
        return g1.distance(g2) < tolerance
    if wkb1 in (QGis.WKBPolygon, QGis.WKBPolygon25D):
        return QgsGeometry.compare(g1.asPolygon(), g2.asPolygon(), tolerance)
    if wkb1 in (QGis.WKBLineString, QGis.WKBLineString25D):
        return QgsGeometry.compare(g1.asPolyline(), g2.asPolyline(), tolerance)



