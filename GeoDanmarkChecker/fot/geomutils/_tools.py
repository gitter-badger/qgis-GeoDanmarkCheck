from qgis.core import QgsFeature, QgsGeometry


def togeometry(f):
    """If input is feature returns the geometry of the feature.
    If input is geometry returns the input.
    Fails otherwise"""
    if isinstance(f, QgsGeometry):
        return f
    elif isinstance(f, QgsFeature):
        return f.geometry()
    else:
        raise TypeError()

def shortestline(f1, f2):
    """Returns the shortest line between two geometries or features"""
    g1 = togeometry(f1)
    g2 = togeometry(f2)
    return g1.shortestLine(g2)



