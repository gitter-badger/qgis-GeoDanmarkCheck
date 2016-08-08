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

# Rules regarding a single object
from singlelayerrule import SingleLayerRule
from qgis.core import QgsFeatureRequest

class SingleFeatureRule(SingleLayerRule):

    #_executor =  SingleFeatureExecutor()

    def __init__(self, name, feature_type, attributesneeded=None, geometryneeded=True, filter = None):
        super(SingleFeatureRule, self).__init__(name, feature_type, attributesneeded, geometryneeded, filter)


    def checkmany(self, features, reporter, progressreporter):
        progressreporter.begintask(self.name, len(features))
        for f in features:
            self.check(f, reporter)
            progressreporter.completed_one()


    def check(self, feature, reporter):
        raise NotImplementedError()

    #def executor(self):
    #    return SingleFeatureRule._executor

