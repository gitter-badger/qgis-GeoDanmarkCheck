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

from .utils import QgisLogger
from .utils import PrintLogger


class ConsoleReporter(object):
    """ Report to a console

    Args:
        reporter_type: 'log' or 'qgis'
    Raises:
        ValueError: if reporter_type not allowed
    """

    def __init__(self, reporter_type='log'):
        self.reporter = self.get_reporter(reporter_type)

    def get_reporter(self, reporter_type):
        """ returns the class to use for reporting

        Args:
            reporter_type: either 'log' or 'qgis'
        Raises:
            ValueError: if reporter_type isn't either 'log' or 'qgis'
        """
        if reporter_type == 'log':
            return PrintLogger()

        if reporter_type == 'qgis':
            return QgisLogger('GeoDanmark Checker')

        raise ValueError('Reporter type has to be either qgis or log')

    # TODO: make geometry a textual representation
    def error(self, rulename, typeinfo, message, geometry):
        self.reporter.error(rulename, typeinfo, message, geometry)

    def warning(self, rulename, typeinfo, message, geometry):
        self.reporter.warning(rulename, typeinfo, message, geometry)

    def critical(self, rulename, typeinfo, message, geometry):
        self.reporter.critical(rulename, typeinfo, message, geometry)
