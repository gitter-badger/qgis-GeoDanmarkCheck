from GeoDanmarkChecker.fot.geomutils import FeatureIndex, togeometry
from qgis.core import QgsGeometry, QgsGeometryEngine
# Class which matches two features against each other


class FeatureMatcher(object):

    def __init__(self):
        # exact geometry match
        # at least some intersection
        # centroid inside
        # within distance
        self.coordinatetolerance = 0.01
        pass


    def match(self, featurecollection1, featurecollection2):
        pass
        yield match


    def _oneagainstmany(self,f, indexedfeaturecollection):
        if not isinstance(indexedfeaturecollection, FeatureIndex):
            raise TypeError("Expected FeatureIndex")
        geom = togeometry(f)


        intersecting = indexedfeaturecollection.geometryintersects(f)
        for otherfeature in intersecting:
            othergeom = togeometry(otherfeature)
            if QgsGeometry.compare(f, othergeom, self.coordinatetolerance):
                return (f, otherfeature, geom)

            geomengine = QgsGeometryEngine( geom.geometry() )
            geomengine.prepareGeometry()





class FeatureMatch(object):
    def __init__(self, f1, f2, matchgeom = None):
        self.feature1 = f1
        self.feature2 = f2
        self.matchgeometry = matchgeom
