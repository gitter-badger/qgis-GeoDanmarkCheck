from qgis.core import QgsGeometry
from . import FeatureIndex
from featurematcher import FeatureMatch
from . import togeometry, tocoordinates
from .algorithms import densify

class SegmentMatchFinder(object):
    def __init__(self, matchagainstfeatures, segmentize = 0):
        self.features = matchagainstfeatures
        self.indexedfeatures = FeatureIndex(matchagainstfeatures, usespatialindex=True)
        self.segmentize = float(segmentize) if segmentize else 0

    def findmatching(self, feature, maxdistance):
        maxdistance = float(maxdistance)
        geom = togeometry(feature)
        bbox = geom.boundingBox()

        # segmentize feature
        seggeom = densify(geom, self.segmentize) if self.segmentize else geom
        segcoords = tocoordinates(seggeom)

        # for each segment find the matching feature which has the lowest summed distance from the endpoints
        for index, coord in enumerate(segcoords):
            rect = QgsGeometry.fromPoint(coord).boundingBox()
            rect.buffer(maxdistance)
            nearbyfeatures = self.indexedfeatures.geometryintersects(rect)
            for neighbor in nearbyfeatures:
                sqrddist, closestsegmentpoint, indexofclosestvertexafter = g2.closestSegmentWithContext(c1)




        # This is the matching feature



        if segmentmatcher.bboxexpansion > 0:
            bbox.buffer(segmentmatcher.bboxexpansion)


        nearbyfeatures = self.indexedfeatures.geometryintersects(bbox)
        matches = []


        for otherfeat in nearbyfeatures:
            m = matcher.match(prep, otherfeat)
            if m:
                matches.append(m)
        matches.sort(key=lambda match: match.matchscore)
        return matches