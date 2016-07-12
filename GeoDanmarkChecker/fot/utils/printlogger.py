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


class PrintLogger(object):
    def info(self, rulename, typeinfo, message, geometry):
        self.log(rulename, typeinfo, message, geometry, 'info')

    def error(self, rulename, typeinfo, message, geometry):
        self.log(rulename, typeinfo, message, geometry, 'error')

    def warning(self, rulename, typeinfo, message, geometry):
        self.log(rulename, typeinfo, message, geometry, 'warning')

    def critical(self, rulename, typeinfo, message, geometry):
        self.log(rulename, typeinfo, message, geometry, 'critical')

    def log(self, rulename, typeinfo, message, geometry, level):
        print(
            '{level} - {rulename} - {typeinfo} - {message} - {geom}'.format(
                level=level,
                rulename=rulename,
                typeinfo=typeinfo,
                message=message,
                geom=geometry
            )
        )
