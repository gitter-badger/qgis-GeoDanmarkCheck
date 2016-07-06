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
import osgeo.ogr as ogr
import osgeo.osr as osr


class OGRSPatialite(object):
    def __init__(self, path):
        self.path = path
        self.layers = {}
        self.driver = ogr.GetDriverByName("SQLite")
        self._create_data_source()

    def __str__(self):
        return '{}'.format(self.path)

    def add_layer(self, layer_name, type, fields, srs=25832):
        """" Creates a new layer (table) in database

        Args:
            layer_name: name of the layer
            type:       ogr type of geometry in layer
            fields:     list of tuples of (field name, ogr field type)
            srs:        coordinate reference system, defaults to 25832
        """
        _srs = osr.SpatialReference()
        _srs.ImportFromEPSG(srs)
        layer = self.data_source.CreateLayer(
            layer_name,
            _srs,
            type
        )
        for field in fields:
            field_definition = ogr.FieldDefn(field[0], field[1])
            field_definition.SetWidth(1000)
            layer.CreateField(field_definition)

        self.layers[layer_name] = layer

    def add_feature_to_layer(self, layer_name, fields, geometry):
        """" Adds a feature to the layer

        Args:
            layer_name: name of the layer
            fields:     list of tuples of (field name, ogr field type)
        """
        layer = self.layers[layer_name]
        feature = ogr.Feature(layer.GetLayerDefn())
        for field in fields:
            feature.SetField(field[0], field[1])

        feature.SetGeometry(
            ogr.CreateGeometryFromWkb(geometry.asWkb())
        )
        layer.CreateFeature(feature)
        feature.Destroy()

    def _create_data_source(self):
        """" Creates a spatialite database on disk.

        Raises:
            RuntimeError: in case a database is already on disk or if ogr fails
        """
        if os.path.isfile(self.path) or os.path.isdir(self.path):
            RuntimeError('File already found on disk.')

        self.data_source = self.driver.CreateDataSource(
            self.path,
            options=[
                'SPATIALITE=YES',
                'INIT_WITH_EPSG=YES',
                'OGR_SQLITE_SYNCHRONOUS=OFF'
            ]
        )
        if not self.data_source:
            RuntimeError('Unknown error in ogr CreateDataSource.')
