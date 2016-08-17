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

from .geomutils import togeometry
from qgis.core import QGis
import osgeo.ogr as ogr
from .ogrspatialite import OGRSPatialite


class Reporter(object):

    def __init__(self, output_path):
        # output file is path and filename is a db based on timestamp
        self.output_path = output_path
        self._initialize_db()

    # Maybe take a Rule as first argument? Rule knows its name and should now what types are touched
    def error(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "error")

    def warning(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "warning")

    def report(self, rulename, typeinfo, message, geometry, level):
        if geometry:
            try:
                geometry = togeometry(geometry)
            except TypeError:
                geometry = None

        fields = [
            ('rulename', unicode(rulename).encode('utf-8')),
            ('typeinfo', unicode(typeinfo).encode('utf-8')),
            ('message', unicode(message).encode('utf-8')),
            ('level', unicode(level).encode('utf-8'))
        ]

        # QGis.flatType if we don't care about 25D and whatnot
        if geometry is None:
            print 'XXXXX text output xxxxx', message
            self.db.add_feature_to_layer('text', fields, None)
        elif QGis.flatType(geometry.wkbType()) == QGis.WKBLineString:
            if geometry.length() < 0.001:
                # Lines with length 0 tends to crash spatialite. Report as point instead
                self.report(rulename, typeinfo, message, geometry.centroid(), level)
            else:
                self.db.add_feature_to_layer(
                    'linestring',
                    fields,
                    geometry
                )
        elif QGis.flatType((geometry.wkbType())) == QGis.WKBPoint:
            self.db.add_feature_to_layer(
                'point',
                fields,
                geometry
            )

        elif QGis.flatType((geometry.wkbType())) == QGis.WKBPolygon:
            self.db.add_feature_to_layer(
                'polygon',
                fields,
                geometry
            )

    def _initialize_db(self):
        self.db = OGRSPatialite(self.output_path)
        fields = [
            ('rulename', ogr.OFTString),
            ('typeinfo', ogr.OFTString),
            ('message', ogr.OFTString),
            ('level', ogr.OFTString)
        ]
        # Add layer for linestring
        self.db.add_layer(
            'linestring',
            ogr.wkbLineString,
            fields
        )
        # Add layer for points
        self.db.add_layer(
            'point',
            ogr.wkbPoint,
            fields
        )
        # Add layer for polygons
        self.db.add_layer(
            'polygon',
            ogr.wkbPolygon,
            fields
        )
        # Add layer for plain text
        self.db.add_layer(
            'text',
            ogr.wkbNone,
            fields
        )
