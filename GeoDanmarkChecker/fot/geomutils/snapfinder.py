from . import FeatureIndex
from . import tocoordinates, togeometry
from qgis.core import QgsGeometry

class SnapFinder(object):
    def __init__(self, features):
        """instantiates a snapfinder which finds snaps to features"""
        self.features = list(features)
        self.index = FeatureIndex(self.features, usespatialindex=True)
        self.snapepsilon = 0.001

    def vertexsnaps(self, feature, vertexindex):
        # Only works for lines at the moment
        featgeom = togeometry(feature)
        coords = tocoordinates(feature)
        return self._vertexsnaps(feature, coords, vertexindex)

    def endpointsnaps(self, feature):
        featgeom = togeometry(feature)
        coords = tocoordinates(feature)
        return self._vertexsnaps(feature, coords, 0), self._vertexsnaps(feature, coords, len(coords) - 1)

    def _vertexsnaps(self, feature, coordinates, vertexindex):
        """Finds all other features where this feature snaps to one of their vertices"""
        #coord = coords[ringindex][vertexindex] if ringindex else coords[vertexindex]
        coord = coordinates[vertexindex]
        rect = QgsGeometry.fromPoint(coord).boundingBox()
        rect.buffer(self.snapepsilon)
        candidates = self.index.geometryintersects(rect)

        firstvertex = vertexindex == 0
        lastvertex = vertexindex == len(coordinates) - 1
        for c in candidates:
            if c == feature:
                # Dont check against self
                continue
            ccoord, cindex, cbeforeindex, cafterindex, cdistance = feature.geometry().closestVertex(coord)
            if cdistance < self.snapepsilon:
                # Snap!
                s1 = SnapLocation(feature, coord, vertexindex=vertexindex, firstvertex=firstvertex, lastvertex=lastvertex)
                first = cbeforeindex <= 0
                last = cafterindex < 0
                s2 = SnapLocation(c, ccoord, vertexindex=cindex, firstvertex=first, lastvertex=last)
                return Snap(s1, s2, cdistance, None)

class SnapLocation(object):
    def __init__(self, feature, coordinate, vertexindex = None, firstvertex = False, lastvertex = False):
        self.feature = feature
        self.ringindex = None
        self.vertexindex = vertexindex
        self.lastvertex = lastvertex
        self.firstvirtex = firstvertex
        self.coordinate = coordinate

class Snap(object):
    def __init__(self, feature1location, feature2location, xydifference, zdifference = None):
        self.feature1location = feature1location # Snaplocation
        self.feature2location = feature2location
        self.zdifference = zdifference # Difference in Z
        self.xydifference = xydifference # Distance in xy-plane

    def is_3D_snap(self):
        raise NotImplementedError()

    def is_2D_snap(self):
        return self.feature1location.vertexindex is not None and self.feature2location.vertexindex is not None

    def is_segment_snap(self):
        return self.feature1location.vertexindex is None or self.feature2location.vertexindex is None