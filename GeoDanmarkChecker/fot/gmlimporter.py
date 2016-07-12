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


def ogr_convert(
    source,
    source_driver,
    destination,
    destination_driver,
    options=[]
):
    """ Converts the source to the output format

    Args:
        source: file to be converted
        source_driver: ogr driver for source file
        destination: destination of converted file
        destination_driver: ogr driver for converted file
        options (optional): ogr creation options for destination file
    Returns:
        True: if conversion was successful
    Raises:
        RuntimeError: if the source file doesnt exists or if ogr fails
    """
    if not os.path.isfile(source):
        raise RuntimeError('{} does not exists.'.format(source))

    source = ogr.GetDriverByName(source_driver).Open(source)
    if not source:
        raise RuntimeError('Unable to open input file: {}'.format(source))

    destination = ogr.GetDriverByName(destination_driver).CopyDataSource(
        source,
        destination,
        options
    )
    if not destination:
        raise RuntimeError(
            'Unable to create output file: {}'.format(destination)
        )

    return True


def gml_to_spatialite(source, destination=None):
    """" Converts a gml file to a spatialite file using ogr_convert, the new
    file is kept next to the original by default.

    Args:
        source: file to be converted
        destination (optional): destination of converted file
    Returns:
        True: if conversion was successful
        False: if conversion failed
    """

    if not destination:
        destination = '{}.sqlite'.format(
            os.path.splitext(source)[0]
        )

    options = [
        'SPATIALITE=YES',
        'INIT_WITH_EPSG=YES',
        'OGR_SQLITE_SYNCHRONOUS=OFF'
    ]

    try:
        ogr_convert(source, 'GML', destination, 'SQLite', options)
    except RuntimeError:
        return False

    return True
