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

from .singlelayerrule import SingleLayerRule
from ....geomutils.segmentmatcher import SegmentMatchFinder

class DuplicateLineStringLayerGeometries(SingleLayerRule):
    """Check for duplicate or almost coincident linestring geometry segments.

    Check is done segment by segment, with the option to split segments into smaller segments before check is executed.

    If a feature A is within 'equalstolerance' distance of both ends of a segment from feature B then features A and B
    are considered to be coincident along that segment.

    Parameters
    ----------
    name : str
        Name if this rule instance
    feature_type : fot.FeatureType
        Feature type to apply check to
    segmentize : float or None
        Segmentize geometry into pieces of maximum this length. If None the geometry is not segmentized.
    equalstolerance : float
        Maximum distance to consider geometries coincident.
    filter : str
        QGIS Filter Expression which is applied to features before evaluating this rule.
    """
    def __init__(self, name, feature_type, segmentize=2, equalstolerance=0.1, filter=None):
        super(DuplicateLineStringLayerGeometries, self).__init__(name, feature_type)
        self.filter = filter
        self.segmentize = float(segmentize)
        self.equalstolerance = float(equalstolerance)

    def checkmany(self, features, reporter, progressreporter):
        progressreporter.begintask(self.name, len(features))

        segmentmatchfinder = SegmentMatchFinder(features, segmentize=self.segmentize)
        for f in features:
            for sm in segmentmatchfinder.findmatching(f, maxdistance=self.equalstolerance):
                f2 = sm.nearestfeature
                if f != f2:
                    reporter.error(self.name, self.featuretype,
                                   "Possible duplicate geometry", sm.togeometry())
            progressreporter.completed_one()