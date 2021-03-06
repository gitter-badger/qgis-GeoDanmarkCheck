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

from .singlefeaturerule import SingleFeatureRule


class AttributeRule(SingleFeatureRule):
    """Apply a python function on the value of a given attribute.

    Parameters
    ----------
    name : str
        Name if this rule instance
    feature_type : fot.FeatureType
        Feature type to apply check to
    attributename : str
        Name of attribute which must be unique
    isvalidfunction : function(value) returning bool
        Function which determines whether a value is valid.
        Like 'lambda value: value > 5'
    filter : str
        QGIS Filter Expression which is applied to features before evaluating this rule.

    """

    def __init__(self, name, feature_type, attributename, isvalidfunction, filter=None):
        super(AttributeRule, self).__init__(name, feature_type, attributesneeded=[attributename], geometryneeded=True)
        self.attributename = attributename
        self.isvalidfunction = isvalidfunction

    def check(self, feature, reporter):
        try:
            value = feature[self.attributename]
            if not self.isvalidfunction(value):
                reporter.error(self.name, self.featuretype, self.attributename + '="' + unicode(value) + '" not valid', feature)
        except:
            reporter.error(self.name, self.featuretype, "Error processing attribute: " + self.attributename, feature)
