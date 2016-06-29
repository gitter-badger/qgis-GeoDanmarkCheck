from qgis.core import QgsFeature, QgsGeometry
from collections import Iterable


def togeometry(f):
    """If input is feature returns the geometry of the feature.
    If input is geometry returns the input.
    Fails otherwise"""
    if isinstance(f, QgsGeometry):
        return f
    elif isinstance(f, QgsFeature):
        return f.geometry()
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



