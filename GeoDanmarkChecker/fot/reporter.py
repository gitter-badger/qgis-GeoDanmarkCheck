from datetime import datetime
from qgis.core import (
    QgsFeature,
    QGis
)
import osgeo.ogr as ogr
from ogrspatialite import OGRSPatialite


class Reporter(object):

    def __init__(self, output_path):
        # output file is path and filename is a db based on timestamp
        self.layer = None
        self.driver = None
        self.feature = None
        self.data_source = None
        self.output_path = output_path
        self._initialize_db()

    def reportError(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "error")

    def reportWarning(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "warning")

    def report(self, rulename, typeinfo, message, geometry, level):
        if isinstance(geometry, QgsFeature):
            geometry = geometry.geometry()
            fields = [
                ('rulename', str(rulename)),
                ('typeinfo', str(typeinfo)),
                ('message', str(message)),
                ('level', str(level))
            ]
            # QGis.flatType if we don't care about 25D and whatnot
            if QGis.flatType(geometry.wkbType()) == QGis.WKBLineString:
                self.db.add_feature_to_layer(
                    'linestring',
                    fields,
                    geometry
                )

            if QGis.flatType((geometry.wkbType())) == QGis.WKBPoint:
                self.db.add_feature_to_layer(
                    'point',
                    fields,
                    geometry
                )

            if QGis.flatType((geometry.wkbType())) == QGis.WKBPolygon:
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
            ogr.wkbLineString25D,
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
