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

def attributenames(f):
    [field.name() for field in f.fields()]

def changedattributes(f1, f2, checkattributes=None):
    attriblist = checkattributes if checkattributes else attributenames(f1)
    for attrib in attriblist:
        result = []
        try:
            if not f1[attrib] == f2[attrib]:
                message = u'Attribute {0} changed from {1} to {2}'.format(attrib, f1[attrib], f2[attrib])
        except KeyError as e:
            message = u'Attribute {0} not found'.format(attrib)
        if message:
            result.append((attrib, message))
