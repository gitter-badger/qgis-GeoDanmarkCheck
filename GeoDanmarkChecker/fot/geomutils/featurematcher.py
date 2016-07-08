from . import FeatureIndex, togeometry, geometryequal, extractlinestrings, shortestline
from qgis.core import QgsGeometry

# Classes which finds matching features in another collection of features


class PreparedFeature(object):
    def __init__(self, feature):
        self.feature = feature
        self.geom = togeometry(feature)
        geomengine = QgsGeometry.createGeometryEngine(self.geom.geometry())
        geomengine.prepareGeometry()
        self.preparedgeom = geomengine


class FeatureMatch(object):
    def __init__(self, f1, f2, matchgeom = None, exactmatch = False):
        self.exactmatch = exactmatch
        self.feature1 = f1
        self.feature2 = f2
        self.matchgeometry = matchgeom


class MatchFinder(object):
    def __init__(self, matchagainstfeatures):
        self.features = matchagainstfeatures
        self.indexedfeatures = FeatureIndex(matchagainstfeatures, usespatialindex=True)

    def findmatching(self, feature, matcher):
        prep = PreparedFeature(feature)
        geom = prep.geom
        bbox = geom.boundingBox()
        if matcher.bboxexpansion > 0:
            bbox.buffer(matcher.bboxexpansion)
        nearbyfeatures = self.indexedfeatures.geometryintersects(bbox)
        for otherfeat in nearbyfeatures:
            m = matcher.match(prep, otherfeat)
            if m:
                yield m


class ExactGeometryMatcher(object):

    def __init__(self, coordinatetolerance=0.01, **kwargs):
        self.coordinatetolerance = coordinatetolerance
        self.bboxexpansion = 0.0

    def match(self, preparedfeature, otherfeature):
        return self.matchesexactly(preparedfeature, otherfeature)

    def matchesexactly(self, preparedfeature, otherfeature):
        othergeom = togeometry(otherfeature)
        if geometryequal(preparedfeature.geom, othergeom, self.coordinatetolerance):
            return FeatureMatch(preparedfeature.feature, otherfeature, othergeom, exactmatch=True)
        return None


class NearbyObjectsGeometryMatcher(ExactGeometryMatcher):
    def __init__(self, **kwargs):
        self.distancewithin = 5.0
        self.bboxexpansion = self.distancewithin

    def match(self, preparedfeature, otherfeature):
        # If exact match - return that
        m = self.matchesexactly(preparedfeature, otherfeature)
        if m:
            return m
        line = shortestline(preparedfeature.geom, otherfeature)
        if line.length() < self.distancewithin:
            return FeatureMatch(preparedfeature.feature, otherfeature, line)


class ApproximatePolygonMatcher(ExactGeometryMatcher):

    def __init__(self, **kwargs):
        super(ApproximatePolygonMatcher, self).__init__(**kwargs)
        self.useareaintersection = False
        if 'relativeareadeviation' in kwargs:
            self.relativeareadeviation = float( kwargs['relativeareadeviation'] )
            self.useareaintersection = bool(self.relativeareadeviation)

    def match(self, preparedfeature, otherfeature):
        # If exact match - return that
        m = self.matchesexactly(preparedfeature, otherfeature)
        if m:
            return m

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


class ApproximateLineMatcher(ExactGeometryMatcher):

    def __init__(self, **kwargs):
        super(ApproximateLineMatcher, self).__init__(**kwargs)
        self.uselineintersection = True
        self.relativelengthdeviation = None
        self.minimumintersectionlength = 0
        if 'relativelengthdeviation' in kwargs:
            self.relativelengthdeviation = float( kwargs['relativelengthdeviation'] )
            self.uselineintersection = True

        if 'minimumintersectionlength' in kwargs:
            self.minimumintersectionlength = float(kwargs['minimumintersectionlength'])

        self.linebuffer = self.coordinatetolerance
        if 'linebuffer' in kwargs:
            self.linebuffer = float(kwargs['linebuffer'])
            self.useareaintersection = True
            self.bboxexpansion = self.linebuffer

    def match(self, preparedfeature, otherfeature):
        # If exact match - return that
        m = self.matchesexactly(preparedfeature, otherfeature)
        if m:
            return m

        othergeom = togeometry(otherfeature)
        # Do we use exact intersection?
        if self.uselineintersection:
            intersection = preparedfeature.geom.intersection(othergeom) #preparedfeature.preparedgeom.intersection(othergeom.geometry())
            isectlength = intersection.length()

            if isectlength and isectlength > self.minimumintersectionlength:
                line = extractlinestrings(intersection)
                # If we actually have an intersection - not just points
                if self.relativelengthdeviation is None:
                    return FeatureMatch(preparedfeature.feature, otherfeature, line)
                else:
                    l1 = preparedfeature.geom.length()
                    l2 = othergeom.length()
                    diff1 = abs(l1 - isectlength) / l1
                    diff2 = abs(l2 - isectlength) / l2
                    if diff1 < self.relativelengthdeviation or diff2 < self.relativeareadeviation:
                        return FeatureMatch(preparedfeature.feature, otherfeature, line)
        return None


class ApproximatePointMatcher(ExactGeometryMatcher):
    pass







