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
from qgis.core import QgsMessageLog


class QgisLogger(object):
    # TODO: either dont print geometry, or print some textual repr, probably fails now
    def __init__(self, plugin_name):
        self.plugin_name = plugin_name

    def log(self, rulename, typeinfo, message, geometry, level=QgsMessageLog.INFO):
        QgsMessageLog.logMessage(
            u'{rulename} - {typeinfo} - {message} - {geometry}'.format(
                rulename=rulename,
                typeinfo=typeinfo,
                message=message,
                geometry=geometry
            ),
            self.plugin_name,
            level
        )

    def info(self, rulename, typeinfo, message, geometry):
        self.log(
            rulename,
            typeinfo,
            message,
            geometry,
            level=QgsMessageLog.INFO
        )

    def warning(self, rulename, typeinfo, message, geometry):
        self.log(
            rulename,
            typeinfo,
            message,
            geometry,
            level=QgsMessageLog.WARNING
        )

    def critical(self, rulename, typeinfo, message, geometry):
        self.log(
            rulename,
            typeinfo,
            message,
            geometry,
            level=QgsMessageLog.CRITICAL
        )

    def error(self, rulename, typeinfo, message, geometry):
        self.critical(rulename, typeinfo, message, geometry)
