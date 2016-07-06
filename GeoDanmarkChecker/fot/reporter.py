from datetime import datetime
from PyQt4.QtCore import QVariant
from qgis.core import (
    QgsFeature,
    QGis
)
import osgeo.ogr as ogr
import osgeo.osr as osr


class Reporter(object):

    def __init__(self, output_path):
        # output file is path and filename is a db based on timestamp
        self.layer = None
        self.driver = None
        self.feature = None
        self.data_source = None
        self.output_path = output_path
        self._initialize_spatialite()

    def reportError(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "error")

    def reportWarning(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "warning")

    def report(self, rulename, typeinfo, message, geometry, level):
        if isinstance(geometry, QgsFeature):
            geometry = geometry.geometry()
            # QGis.flatType if we don't care about 25D and whatnot
            if QGis.flatType(geometry.wkbType()) == QGis.WKBLineString:
                self.feature = ogr.Feature(self.layer.GetLayerDefn())
                self.feature.SetField("rulename", str(rulename))
                self.feature.SetField("typeinfo", str(typeinfo))
                self.feature.SetField("message", str(message))
                self.feature.SetField("level", str(level))
                self.feature.SetGeometry(
                    ogr.CreateGeometryFromWkb(geometry.asWkb())
                )
                self.layer.CreateFeature(self.feature)
                self.feature.Destroy()

            if QGis.flatType((geometry.wkbType())) == QGis.WKBPoint:
                pass

            if QGis.flatType((geometry.wkbType())) == QGis.WKBPolygon:
                pass

    def _initialize_spatialite(self):
        self.driver = ogr.GetDriverByName("SQLite")
        self.data_source = self.driver.CreateDataSource(
            "geodk_report_{}.sqlite".format(
                datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
            ),
            options=[
                'SPATIALITE=YES',
                'INIT_WITH_EPSG=YES',
                'OGR_SQLITE_SYNCHRONOUS=OFF'
            ]
        )
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(25832)
        self.layer = self.data_source.CreateLayer("linestring_report", srs, ogr.wkbLineString25D)
        rulename = ogr.FieldDefn("rulename", ogr.OFTString)
        rulename.SetWidth(1000)
        self.layer.CreateField(rulename)
        typeinfo = ogr.FieldDefn("typeinfo", ogr.OFTString)
        typeinfo.SetWidth(1000)
        self.layer.CreateField(typeinfo)
        message = ogr.FieldDefn("message", ogr.OFTString)
        message.SetWidth(1000)
        self.layer.CreateField(message)
        level = ogr.FieldDefn("level", ogr.OFTString)
        level.SetWidth(1000)
        self.layer.CreateField(level)
