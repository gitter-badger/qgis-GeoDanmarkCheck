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

import os
from osgeo import ogr


# We want to use this to let the user specify a gml file and then be able to
# convert it on the fly
# Takes a file in, and creates a converted file next to it with the same name
class OGRConvert(object):
    """
    Convert data sources using ogr
    """

    def __init__(self, source, new_format):
        self.source = source
        self.new_format = new_format

    def _source_exists(self):
        if not os.path.isfile(self.source):
            return False

        return True


def gml_to_spatialite(source):
    """" Converts an gml file to a spatialite file using ogr

    Args:
        source: file to be converted
    Returns:
        True: if conversion was successful
        False: if conversion failed
    Raises:
        RuntimeError: if the source file doesnt exists
    """
    if not os.path.isfile(source):
        RuntimeError('{} does not exists.'.format(source))

