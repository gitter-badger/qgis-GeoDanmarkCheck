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
        self.linestring_table = 'error_linestring'
        self.point_table = 'error_point'
        self.polygon_table = 'error_polygon'
        self.text_table = 'error_text'
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
            ('objecttype', unicode(typeinfo).encode('utf-8')),
            ('message', unicode(message).encode('utf-8')),
            ('level', unicode(level).encode('utf-8'))
        ]

        # QGis.flatType if we don't care about 25D and whatnot
        if geometry is None:
            print 'XXXXX text output xxxxx', message
            self.db.add_feature_to_layer(
                self.text_table,
                fields,
                None
            )
        elif QGis.flatType(geometry.wkbType()) == QGis.WKBLineString:
            if geometry.length() < 0.001:
                # Lines with length 0 tends to crash spatialite. Report as point instead
                self.report(rulename, typeinfo, message, geometry.centroid(), level)
            else:
                self.db.add_feature_to_layer(
                    self.linestring_table,
                    fields,
                    geometry
                )
        elif QGis.flatType((geometry.wkbType())) == QGis.WKBPoint:
            self.db.add_feature_to_layer(
                self.point_table,
                fields,
                geometry
            )

        elif QGis.flatType((geometry.wkbType())) == QGis.WKBPolygon:
            self.db.add_feature_to_layer(
                self.polygon_table,
                fields,
                geometry
            )

    def _initialize_db(self):
        self.db = OGRSPatialite(self.output_path)
        fields = [
            ('rulename', ogr.OFTString),
            ('objecttype', ogr.OFTString),
            ('message', ogr.OFTString),
            ('level', ogr.OFTString)
        ]
        # Add layer for linestring
        self.db.add_layer(
            self.linestring_table,
            ogr.wkbLineString,
            fields
        )
        # Add layer for points
        self.db.add_layer(
            self.point_table,
            ogr.wkbPoint,
            fields
        )
        # Add layer for polygons
        self.db.add_layer(
            self.polygon_table,
            ogr.wkbPolygon,
            fields
        )
        # Add layer for plain text
        self.db.add_layer(
            self.text_table,
            ogr.wkbNone,
            fields
        )


class CascadingReporter(object):
    def __init__(self, reporters):
        self.reporters = list(reporters)

    def error(self, rulename, typeinfo, message, geometry):
        for r in self.reporters:
            r.error(rulename, typeinfo, message, geometry)

    def warning(self, rulename, typeinfo, message, geometry):
        for r in self.reporters:
            r.warning(rulename, typeinfo, message, geometry)

    def report(self, rulename, typeinfo, message, geometry, level):
        for r in self.reporters:
            r.report(rulename, typeinfo, message, geometry, level)
