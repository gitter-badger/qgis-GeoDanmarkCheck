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

class FeatureType(object):

    def __init__(self, name, tablename, displayname):
        self.name = name
        self.tablename = tablename
        self.displayname = displayname

    def __repr__(self):
        return self.name


featuretypes = []

BYGNING = FeatureType('BYGNING', 'bygning', '')
featuretypes.append(BYGNING)

VINDMOELLE = FeatureType('VINDMOELLE', 'vindmoelle', '')
featuretypes.append(VINDMOELLE)

VANDLOEBSMIDTE_BRUDT = FeatureType('VANDLOEBSMIDTE_BRUDT', 'vandloebsmidte_brudt', '')
featuretypes.append(VANDLOEBSMIDTE_BRUDT)

VEJMIDTE_BRUDT = FeatureType('VEJMIDTE_BRUDT', 'vejmidte_brudt', '')
featuretypes.append(VEJMIDTE_BRUDT)