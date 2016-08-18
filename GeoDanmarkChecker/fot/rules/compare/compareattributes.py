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


class AttributesMustNotBeChanged(CompareRule):
    def __init__(self, name, feature_type, unchangedattributes, featurematcher, beforefilter=None, afterfilter=None):
        super(AttributesMustNotBeChanged, self).__init__(name, beforefilter, afterfilter)
        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        self.featuretype = feature_type
        self.unchangedattributes = unchangedattributes
        self.matcher = featurematcher

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype, attributes=self.unchangedattributes, feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, attributes=self.unchangedattributes, feature_filter=self.afterfilter)

        progressreporter.begintask(self.name, len(beforefeats))
        matchfinder = MatchFinder(afterfeats)
        for f in beforefeats:
            for m in matchfinder.findmatching(f, self.matcher):
                f1 = m.feature1
                f2 = m.feature2
                messages = []
                for attrib in self.unchangedattributes:
                    try:
                        if not f1[attrib] == f2[attrib]:
                            messages.append(u'Attribute {0} changed from {1} to {2}'.format(attrib, f1[attrib], f2[attrib]))
                    except KeyError as e:
                        messages.append(u'Attribute {0} not found'.format(attrib))
                if messages:
                    errorreporter.error(self.name, self.featuretype, ';'.join(messages), m.matchgeometry)
            progressreporter.completed_one()


class SegmentAttributesMustNotBeChanged(CompareRule):
    """Matches segment by segment. Possibly on a densified geometry. Disregards anything further away than maxdist"""
    def __init__(self, name, feature_type, unchangedattributes, maxdist, segmentize = None, beforefilter=None, afterfilter=None):
        super(SegmentAttributesMustNotBeChanged, self).__init__(name, beforefilter, afterfilter)
        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        self.featuretype = feature_type
        self.unchangedattributes = unchangedattributes
        self.maxdist = float(maxdist)
        self.segmentize = float(segmentize) if segmentize else 0

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype, attributes=self.unchangedattributes, feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, attributes=self.unchangedattributes, feature_filter=self.afterfilter)

        # Features that appear to be changed
        changed_before_features = list(beforefeats)
        changed_after_features = []

        progressreporter.begintask(self.name, len(afterfeats))

        # Find exact geometry matches
        finder = MatchFinder(beforefeats)
        exactMatcher = ExactGeometryMatcher()
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
            progressreporter.completed_one()

        # Compare nonexact geometry matches
        progressreporter.begintask(self.name, len(changed_after_features))
        segmentmatchfinder = SegmentMatchFinder(changed_before_features, segmentize=self.segmentize)
        for f in changed_after_features:
            for sm in segmentmatchfinder.findmatching(f, maxdistance=self.maxdist):
                f2 = sm.nearestfeature
                self._check(errorreporter, f2, f, sm.togeometry())
            progressreporter.completed_one()


    def _check(self, errorreporter, fbefore, fafter, geom):
        messages = []
        for attrib in self.unchangedattributes:
            try:
                if not fbefore[attrib] == fafter[attrib]:
                    messages.append(u'{0}: {1} -> {2}'.format(attrib, fbefore[attrib], fafter[attrib]))
            except KeyError as e:
                messages.append(u'{0} not found'.format(attrib))
        if messages:
            message = "Attribute error: " + '; '.join(messages)
            errorreporter.error(self.name, self.featuretype, message, geom)


