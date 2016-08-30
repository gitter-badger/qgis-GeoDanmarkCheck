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
from ....geomutils.errorgeometry import createlinemarker

class UniqueAttributeValue(SingleLayerRule):
    def __init__(self, name, feature_type, attributename, filter=None):
        super(UniqueAttributeValue, self).__init__(name, feature_type)
        self.filter = filter
        self.attributesneeded = attributename
        self.attributename = attributename
        self.attributevalues = {}

    def checkmany(self, features, reporter, progressreporter):
        progressreporter.begintask(self.name, len(features))
        for feature in features:
            try:
                value = feature[self.attributename]
                if value in self.attributevalues:
                    # Wooops not unique!
                    errorgeom = createlinemarker(feature, self.attributevalues[value])
                    reporter.error(
                        self.name,
                        self.featuretype,
                        self.attributename + '="' + unicode(value) + '" not unique',
                        errorgeom
                    )
                else:
                    self.attributevalues[value] = feature
            except Exception as e:
                reporter.error(
                    self.name,
                    self.featuretype,
                    "Error processing attribute: {0} Message: {1}".format(self.attributename, str(e)),
                    feature
                )
            progressreporter.completed_one()