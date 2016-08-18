from qgis.core import QgsGeometry
from . import FeatureIndex
from featurematcher import FeatureMatch
from . import togeometry, tocoordinates
from .algorithms import densify
from math import sqrt, cos, pi

class SegmentMatch(object):
    def __init__(self, f, nearest_feature):
        self.thisfeature = f
        self.nearestfeature = nearest_feature
        self.vertices = []
        self.maxdistancefound = -1

    def togeometry(self):
        return QgsGeometry.fromPolyline(self.vertices)

    def addvertex(self, point, distance):
        self.vertices.append(point)
        self.maxdistancefound = max(distance, self.maxdistancefound)

class SegmentMatchFinder(object):
    def __init__(self, matchagainstfeatures, segmentize = 0):
        self.features = matchagainstfeatures
        self.indexedfeatures = FeatureIndex(matchagainstfeatures, usespatialindex=True)
        self.segmentize = float(segmentize) if segmentize else 0
        self.approximate_angle_threshold = cos(pi/4.0)

    def findmatching(self, feature, maxdistance):
        maxdistance = float(maxdistance)
        maxdistsqrd = maxdistance * maxdistance
        geom = togeometry(feature)

        # segmentize feature
        seggeom = densify(geom, self.segmentize) if self.segmentize else geom
        segcoords = tocoordinates(seggeom)

        # For each vertws in this geom calculate distance to all neighbors
        distances_per_vertex = []
        for coord in segcoords:
            rect = QgsGeometry.fromPoint(coord).boundingBox()
            rect.buffer(maxdistance)
            nearbyfeatures = self.indexedfeatures.geometryintersects(rect)
            distances = {}
            for neighbor in nearbyfeatures:
                sqrddist, closestsegmentpoint, indexofclosestvertexafter = neighbor.geometry().closestSegmentWithContext(coord)
                if sqrddist <= maxdistsqrd:
                    distances[neighbor] = (sqrddist, closestsegmentpoint, indexofclosestvertexafter)
            distances_per_vertex.append(distances)

        # for each segment find the matching feature which has the lowest summed sqrdistance from the endpoints
        # Make sure we dont use distance to the same point
        segment_matches = []
        current_segmentmatch = None
        for i in range(1, len(distances_per_vertex)):
            this_vertex = segcoords[i]
            prev_vertex = segcoords[i-1]
            this_segment = QgsGeometry.fromPolyline([prev_vertex, this_vertex])
            this_segment_length = this_segment.length()
            prev_distances = distances_per_vertex[i - 1]
            this_distances = distances_per_vertex[i]
            smallest_distance_sqrd = float('inf')
            smallest_distance_feature = None
            for f, this_distance in this_distances.iteritems():
                if not f in prev_distances:
                    # Feature f wasnt nearby at the previous vertex => f is not candidate for this segment
                    continue
                prev_distance = prev_distances[f]
                sumsqrddistance = this_distance[0] + prev_distance[0]
                # What point was closest? Make sure we dont match an endpoint of the other geom or a geom at a near 90 angle
                prev_point = prev_distance[1]
                this_point = this_distance[1]
                other_segment = QgsGeometry.fromPolyline([prev_point, this_point])
                if other_segment.length() > this_segment_length * self.approximate_angle_threshold and sumsqrddistance < smallest_distance_sqrd:
                    # We found a closer feature
                    smallest_distance_sqrd = sumsqrddistance
                    smallest_distance_feature = f
                    # Perfekt match. Stop looking
                    if smallest_distance_sqrd == 0.0:
                        break
            # Do we have a running segmentmatch to extend?
            if current_segmentmatch and current_segmentmatch.nearestfeature == smallest_distance_feature:
                current_segmentmatch.addvertex(this_vertex, sqrt(smallest_distance_sqrd))
            else:
                # The closes feature is not the same as in the last segment
                if current_segmentmatch:
                    segment_matches.append(current_segmentmatch)
                    current_segmentmatch = None
                if smallest_distance_feature:
                    current_segmentmatch = SegmentMatch(feature, smallest_distance_feature)
                    current_segmentmatch.addvertex(prev_vertex, sqrt(smallest_distance_sqrd))
                    current_segmentmatch.addvertex(this_vertex, sqrt(smallest_distance_sqrd))
        # Add last segmentmatch
        if current_segmentmatch:
            segment_matches.append(current_segmentmatch)
        return segment_matches