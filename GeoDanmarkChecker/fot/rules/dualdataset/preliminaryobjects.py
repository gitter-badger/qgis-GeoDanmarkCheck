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
from ...repository import Repository
from ...geomutils import FeatureIndex, geometryequal, shortestline


class PreliminaryObjectsRule(CompareRule):

    def __init__(self, name, feature_type):
        super(PreliminaryObjectsRule, self).__init__(name)
        self.statusattribute = u'geometri_status'
        self.featuretype = feature_type
        self.beforefilter = self.statusattribute + u' = "Foreløbig"'
        self.idcolumn = 'fot_id'

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        neededattribs = [self.idcolumn, self.statusattribute]

        beforefeats = beforerepo.read(self.featuretype, attributes=neededattribs, feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, attributes=neededattribs)

        progressreporter.begintask(self.name, len(beforefeats))

        if not beforefeats:
            return

        afterindex = FeatureIndex(afterfeats, usespatialindex=False, indexedattributes=[self.statusattribute])

        for f in beforefeats:
            fot_id = f[self.idcolumn]
            matches = afterindex.attributeequals(self.idcolumn, fot_id)

            if not matches:
                errorreporter.error(self.name, self.featuretype, 'Preliminary object ({0}={1}) deleted'.format(self.idcolumn, fot_id), f)

            # Should be checked elsewhere
            if len(matches) > 1:
                line = shortestline(matches[0], matches[1])
                errorreporter.error(self.name, self.featuretype, 'Multiple objects  with {0}={1}'.format(self.idcolumn, fot_id), line)

            newf = matches[0]

            geometryequals = geometryequal(f, newf)
            # TODO: What are the rules exactly?

