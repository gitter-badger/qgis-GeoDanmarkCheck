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

from .comparerule import CompareRule
from ... import Repository
from ... import FeatureType
from ...geomutils.featurematcher import MatchFinder, ExactGeometryMatcher
from ...geomutils.segmentmatcher import SegmentMatchFinder
from qgis.core import QgsPoint, QgsFeature, QgsGeometry, QGis


class MatchingGeometrySameDirection(CompareRule):
    def __init__(self, name, feature_type, direction_attribute, maxdist, segmentize = None, beforefilter=None, afterfilter=None):
        super(MatchingGeometrySameDirection, self).__init__(name, beforefilter, afterfilter)
        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        self.featuretype = feature_type
        self.direction_attribute = direction_attribute
        self.maxdist = float(maxdist)
        self.segmentize = float(segmentize) if segmentize else 0

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype, attributes=[self.direction_attribute], feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, attributes=[self.direction_attribute], feature_filter=self.afterfilter)

        # Features that appear to be changed
        changed_before_features = list(beforefeats)
        changed_after_features = []

        progressreporter.begintask(self.name, len(afterfeats))

        exactMatcher = ExactGeometryMatcher()

        # Find exact (reversed)geometry matches
        finder = MatchFinder(beforefeats)
        for f in afterfeats:
            matches = finder.findmatching(f, exactMatcher)
            match_found = False
            for match in matches:
                match_found = True
                self._check(errorreporter, match.feature2, f, f)
                # Remove from changed if exists (Duplicate geometries forces us to use this check)
                if match.feature2 in changed_before_features:
                    changed_before_features.remove(match.feature2)
            if not match_found:
                changed_after_features.append(f)
            # check on reversed geom
            reversedGeom = QgsGeometry.fromPolyline(list(reversed(f.geometry().asPolyline())))
            matches = finder.findmatching(reversedGeom, exactMatcher)
            match_found = False
            for match in matches:
                match_found = True
                self._check2(errorreporter, match.feature2, f, f)
                # Remove from changed if exists (Duplicate geometries forces us to use this check)
                if match.feature2 in changed_before_features:
                    changed_before_features.remove(match.feature2)
            if not match_found:
                changed_after_features.append(f)
            progressreporter.completed_one()

        # Compare nonexact (reversed)geometry matches
        # TODO: does not work as SegmentMatchFinder does not care about direction
        # progressreporter.begintask(self.name, len(changed_after_features))
        # segmentmatchfinder = SegmentMatchFinder(changed_before_features, segmentize=self.segmentize)
        # for f in changed_after_features:
        #     for sm in segmentmatchfinder.findmatching(f, maxdistance=self.maxdist):
        #         f2 = sm.nearestfeature
        #         self._check(errorreporter, f2, f, sm.togeometry())
        #     # check on reversed geom
        #     reversedGeom = QgsGeometry.fromPolyline(list(reversed(QgsGeometry(f.geometry()).asPolyline())))
        #     for sm in segmentmatchfinder.findmatching(reversedGeom, maxdistance=self.maxdist):
        #         f2 = sm.nearestfeature
        #         self._check2(errorreporter, f2, f, sm.togeometry())
        #     progressreporter.completed_one()

    # check for exact geometry matches - should have same dir
    def _check(self, errorreporter, fbefore, fafter, geom):
        messages = []
        beforeDir = fbefore[self.direction_attribute] if fbefore.fieldNameIndex(self.direction_attribute) != -1 else 0
        afterDir = fafter[self.direction_attribute] if fafter.fieldNameIndex(self.direction_attribute) != -1 else 0

        if beforeDir != afterDir:
            messages.append(u'{0}: "{1}" -> "{2}"'.format(self.direction_attribute, beforeDir, afterDir))
        if messages:
            message = "Geometry match, attribute changed: " + '; '.join(messages)
            errorreporter.error(self.name, self.featuretype, message, geom)

    # check for exact reverse geometry matches - should have opposite dir
    def _check2(self, errorreporter, fbefore, fafter, geom):
        messages = []
        beforeDir = fbefore[self.direction_attribute] if fbefore.fieldNameIndex(
            self.direction_attribute) != -1 else 0
        afterDir = fafter[self.direction_attribute] if fafter.fieldNameIndex(self.direction_attribute) != -1 else 0

        if beforeDir == afterDir:
            messages.append(u'{0}: "{1}" -> "{2}"'.format(self.direction_attribute, beforeDir, afterDir))
        if messages:
            message = "Geometry reversed match, attribute unchanged: " + '; '.join(messages)
            errorreporter.error(self.name, self.featuretype, message, geom)