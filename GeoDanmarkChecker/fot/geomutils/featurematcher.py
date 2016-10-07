# -*- coding: utf-8 -*-
"""
Routines for quality control of GeoDanmark map data
Copyright (C) 2016
Developed by Septima.dk for the Danish Agency for Data Supply and Efficiency

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from . import FeatureIndex, togeometry, geometryequal, extractlinestrings, shortestline, discretehausdorffdistance
from .algorithms import orienteddistance
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
    def __init__(self, f1, f2, matchgeom = None, exactmatch = False, matchscore = None):
        self.exactmatch = exactmatch
        self.feature1 = f1
        self.feature2 = f2
        self.matchgeometry = matchgeom
        self.matchscore = matchscore # Can be used for ordering matches. Low score means good match


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
        matches = []
        for otherfeat in nearbyfeatures:
            m = matcher.match(prep, otherfeat)
            if m:
                matches.append(m)
        matches.sort(key=lambda match: match.matchscore)
        return matches

class ExactGeometryMatcher(object):

    def __init__(self, coordinatetolerance=0.01, **kwargs):
        self.coordinatetolerance = coordinatetolerance
        self.bboxexpansion = 0.0

    def match(self, preparedfeature, otherfeature):
        return self.matchesexactly(preparedfeature, otherfeature)

    def matchesexactly(self, preparedfeature, otherfeature):
        othergeom = togeometry(otherfeature)
        if geometryequal(preparedfeature.geom, othergeom, self.coordinatetolerance):
            return FeatureMatch(preparedfeature.feature, otherfeature, othergeom, exactmatch=True, matchscore=0.0)
        return None

class HausdorffGeometryMatcher(ExactGeometryMatcher):
    def __init__(self, maxhausdorffdistance, **kwargs):
        super(HausdorffGeometryMatcher, self).__init__(**kwargs)
        self.maxhausdorffdistance = float(maxhausdorffdistance)
        self.bboxexpansion = maxhausdorffdistance

    def match(self, preparedfeature, otherfeature):
        # If exact match - return that
        m = self.matchesexactly(preparedfeature, otherfeature)
        if m:
            return m
        g1 = preparedfeature.geom
        dist, p1, p2 = discretehausdorffdistance(g1, otherfeature)
        if dist < self.maxhausdorffdistance:
            matchgeom = QgsGeometry.fromPoint(p1) if dist == 0 else QgsGeometry.fromPolyline([p1,p2])
            return FeatureMatch(
                preparedfeature.feature,
                otherfeature,
                matchgeom=matchgeom,
                exactmatch=False,
                matchscore=dist)

class NearbyObjectsGeometryMatcher(ExactGeometryMatcher):
    def __init__(self, distancewithin, **kwargs):
        super(NearbyObjectsGeometryMatcher, self).__init__(**kwargs)
        self.distancewithin = float(distancewithin)
        self.bboxexpansion = self.distancewithin

    def match(self, preparedfeature, otherfeature):
        # If exact match - return that
        m = self.matchesexactly(preparedfeature, otherfeature)
        if m:
            return m
        line = shortestline(preparedfeature.geom, otherfeature)
        length = line.length()
        if length < self.distancewithin:
            return FeatureMatch(preparedfeature.feature, otherfeature, line, matchscore=length)


class ApproximatePolygonMatcher(ExactGeometryMatcher):

    def __init__(self, **kwargs):
        super(ApproximatePolygonMatcher, self).__init__(**kwargs)
        self.useareaintersection = False
        if 'relativeintersectionarea' in kwargs:
            self.relativeintersectionarea = float(kwargs['relativeintersectionarea'])
            self.useareaintersection = bool(self.relativeintersectionarea)

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
            diff1 = intersectionarea / area1
            diff2 = intersectionarea / area2
            if diff1 > self.relativeintersectionarea and diff2 > self.relativeintersectionarea:
                score = 1.0 - min(diff1, diff2) # Lower score means better match. Lets us compare against the worst of the two
                return FeatureMatch(preparedfeature.feature, otherfeature, intersection, matchscore=score)
        return None


class ApproximateLineMatcher(ExactGeometryMatcher):

    def __init__(self, **kwargs):
        super(ApproximateLineMatcher, self).__init__(**kwargs)
        self.uselineintersection = True
        self.relativeintersectionlength = None
        self.minimumintersectionlength = 0
        if 'relativeintersectionlength' in kwargs:
            self.relativeintersectionlength = float(kwargs['relativeintersectionlength'])
            self.uselineintersection = True

        if 'minimumintersectionlength' in kwargs:
            self.minimumintersectionlength = float(kwargs['minimumintersectionlength'])

        self.linebuffer = self.coordinatetolerance
        if 'linebuffer' in kwargs:
            self.linebuffer = float(kwargs['linebuffer'])
            self.usebufferintersection = True
            self.bboxexpansion = self.linebuffer

    def match(self, preparedfeature, otherfeature):
        # If exact match - return that
        m = self.matchesexactly(preparedfeature, otherfeature)
        if m:
            return m

        othergeom = togeometry(otherfeature)
        # Do we use exact intersection?
        if self.uselineintersection:
            if self.linebuffer:
                # buffer( radius, segments, endcapstyle (2=flat), joinstyle(1=round), mitrelimit)
                isectgeom = preparedfeature.geom.buffer(self.linebuffer, 3, 2, 1, 0)
            else:
                isectgeom = preparedfeature.geom
            intersection = isectgeom.intersection(othergeom) #preparedfeature.preparedgeom.intersection(othergeom.geometry())
            isectlength = intersection.length()

            if isectlength:
                line = extractlinestrings(intersection)
                l1 = preparedfeature.geom.length()
                l2 = othergeom.length()
                diff1 = isectlength / l1
                diff2 = isectlength / l2
                # Lower score means better match. Lets us compare against the worst of the two
                score = 1.0 - min(diff1, diff2)
                if self.relativeintersectionlength is None and isectlength > self.minimumintersectionlength:
                    return FeatureMatch(preparedfeature.feature, otherfeature, line, exactmatch=False, matchscore=score)
                if diff1 > self.relativeintersectionlength \
                        and diff2 > self.relativeintersectionlength \
                        and isectlength > self.minimumintersectionlength:
                    return FeatureMatch(preparedfeature.feature, otherfeature, line, exactmatch=False, matchscore=score)
        return None


class OrientedHausdorffDistanceMatcher(ExactGeometryMatcher):

    def __init__(self, maxorientedhausdorffdistance, **kwargs):
        super(OrientedHausdorffDistanceMatcher, self).__init__(**kwargs)
        self.maxorientedhausdorffdistance = float(maxorientedhausdorffdistance)
        self.bboxexpansion = self.maxorientedhausdorffdistance

    def match(self, preparedfeature, otherfeature):
        # If exact match - return that
        m = self.matchesexactly(preparedfeature, otherfeature)
        if m:
            return m

        othergeom = togeometry(otherfeature)

        distance, frompoint, topoint = orienteddistance(preparedfeature.geom, othergeom)

        if distance <= self.maxorientedhausdorffdistance:
            line = QgsGeometry.fromPolyline([frompoint, topoint])
            return FeatureMatch(
                preparedfeature.feature,
                otherfeature,
                matchgeom=line,
                exactmatch=False,
                matchscore=distance)




