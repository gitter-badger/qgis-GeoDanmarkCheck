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

from ..datasetrule import DatasetRule


# Rules applying to one layer at a time
class SingleLayerRule(DatasetRule):
    def __init__(self, name, feature_type, attributesneeded=None, geometryneeded=True, filter = None):
        super(SingleLayerRule, self).__init__(name)
        self.featuretype = feature_type
        assert not filter or isinstance(filter, str)
        self.attributesneeded = attributesneeded
        self.geometryneeded = geometryneeded
        self.filter = filter

    def checkmany(self, features, reporter, progressreporter):
        raise NotImplementedError

    def execute(self, repo, errorreporter, progressreporter):
        features = repo.read(self.featuretype,
                                 attributes=self.attributesneeded,
                                 geometry=self.geometryneeded,
                                 feature_filter=self.filter)
        print "got", len(features), "features"
        self.checkmany(features, errorreporter, progressreporter)