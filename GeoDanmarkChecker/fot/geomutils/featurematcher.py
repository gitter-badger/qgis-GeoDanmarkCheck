from . import FeatureIndex, togeometry, geometryequal
from qgis.core import QgsGeometry, QgsGeometryEngine, QgsFeature

# Classes which finds matching features in another collection of features

class PreparedFeature(object):
    def __init__(self, feature):
        self.feature = feature
        self.geom = togeometry(feature)
        geomengine = QgsGeometry.createGeometryEngine(self.geom.geometry())
        geomengine.prepareGeometry()
        self.preparedgeom = geomengine

class FeatureMatch(object):
    def __init__(self, f1, f2, matchgeom = None):
        self.feature1 = f1
        self.feature2 = f2
        self.matchgeometry = matchgeom

class FeatureMatcher(object):

    def __init__(self, coordinatetolerance = 0.01, bboxexpansion = 0.0):
        self.coordinatetolerance = coordinatetolerance
        self.bboxexpansion = bboxexpansion

    def match(self, featurecollection1, featurecollection2):
        indexedcollection2 = FeatureIndex(featurecollection2, usespatialindex=True)
        for f in featurecollection1:
            prep = PreparedFeature(f)
            for m in self._oneagainstmany(prep, indexedcollection2):
                yield m

    def _oneagainstmany(self, prep, indexedfeaturecollection):
        if not isinstance(indexedfeaturecollection, FeatureIndex):
            raise TypeError("Expected FeatureIndex")

        geom = prep.geom
        bbox = geom.boundingBox()
        if self.bboxexpansion > 0:
            bbox.buffer(self.bboxexpansion)

        intersecting = indexedfeaturecollection.geometryintersects(bbox)
        for otherfeature in intersecting:
            othergeom = togeometry(otherfeature)
            if geometryequal(geom, othergeom, self.coordinatetolerance):
                yield FeatureMatch(prep.feature, otherfeature, geom)
            else:
                m = self.matchesfeature(prep, otherfeature)
                if m:
                    yield m

class LineMatcher(FeatureMatcher):
    pass


class PolygonMatcher(FeatureMatcher):

    def __init__(self, **kwargs):
        super(PolygonMatcher, self).__init__()

        self.useareaintersection = False
        if 'relativeareadeviation' in kwargs:
            self.relativeareadeviation = float( kwargs['relativeareadeviation'] )
            self.useareaintersection = bool(self.relativeareadeviation)

    def matchesfeature(self, preparedfeature, otherfeature):
        othergeom = togeometry(otherfeature)
        if self.useareaintersection:
            area1 = preparedfeature.preparedgeom.area()
            area2 = othergeom.area()
            intersection = preparedfeature.preparedgeom.intersection(othergeom.geometry())
            intersectionarea = intersection.area()
            diff1 = abs(area1 - intersectionarea) / area1
            diff2 = abs(area2 - intersectionarea) / area2
            if diff1 < self.relativeareadeviation or diff2 < self.relativeareadeviation:
                return FeatureMatch(preparedfeature.feature, otherfeature, intersection)
        return None

class PointMatcher(FeatureMatcher):
    pass







