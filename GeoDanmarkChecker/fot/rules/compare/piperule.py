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
from ... import FeatureType, Repository
from ...geomutils import Snap, SnapLocation, SnapFinder, togeometry, FeatureIndex, geometryequal

class PipeRule(CompareRule):
    def __init__(self, name, feature_type, ispipefunction, isshortfunction, unchangedattributes):
        super(PipeRule, self).__init__(name, beforefilter=None, afterfilter=None)

        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        self.featuretype = feature_type
        self.fotid_attribute = self.featuretype.id_attribute

        if not hasattr(ispipefunction, '__call__'):
            raise Exception('ispipefunction must be a function')
        self.ispipe = ispipefunction

        if not hasattr(ispipefunction, '__call__'):
            raise Exception('isshortfunction must be a function')
        self.isshort = isshortfunction

        self.unchanged_attributes = list(unchangedattributes)

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype, feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, feature_filter=self.afterfilter)

        progressreporter.begintask(self.name, len(beforefeats))
        snapfinder = SnapFinder(beforefeats)
        afterindex = FeatureIndex(afterfeats, usespatialindex=False,indexedattributes=[self.fotid_attribute])
        for f in beforefeats:
            progressreporter.completed_one() # We continue

            # If this is not a pipe then just continue
            if not self.ispipe(f):
                continue

            fgeom = togeometry(f)
            # If this is a short pipe and snapped at both ends - it is allowed to edit - just continue
            if self.isshort(fgeom):
                snaps = snapfinder.endpointsnaps(f)
                if len(snaps) == 2 and not None in snaps:
                    # Snappet i begge ender
                    continue

            # Check that this pipe has not been touched
            afterfeature = afterindex.attributeequals(self.fotid_attribute, f[self.fotid_attribute])
            if not afterfeature:
                errorreporter.error(
                    self.name,
                    self.featuretype,
                    'Piped stream changed (Object illegally deleted)',
                    fgeom)
                continue

            # Any (important) changes to the feature?
            afterfeature = afterfeature[0]
            messages = []
            if not geometryequal(f, afterfeature):
                messages.append('geometry changed')

            for attrib in self.unchanged_attributes:
                messages = []
                try:
                    if not f[attrib] == afterfeature[attrib]:
                        messages.append(u'Attribute {0} changed from {1} to {2}'.format(attrib, f[attrib], afterfeature[attrib]))
                except KeyError as e:
                    messages.append(u'Attribute {0} not found'.format(attrib))
                if messages:
                    message = 'Piped stream changed ({})'.format(';'.join(messages))
                    errorreporter.error(self.name, self.featuretype, message, fgeom)
