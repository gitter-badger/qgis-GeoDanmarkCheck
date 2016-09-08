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

from qgis.core import QgsVectorLayer, QgsFeatureRequest, QgsRectangle
from .featuretype import FeatureType

class InvalidLayerException(Exception):
    pass

class Repository(object):

    def __init__(self, filename):
        self.filename = filename
        self.geometrycolumn = 'Geometry'

    def read(self, feature_type, bbox = None, attributes = None, geometry=True, feature_filter=None):
        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        lyr = self._connectlayer(feature_type)

        request = None
        if bbox or attributes is not None or not geometry or feature_filter:
            request = QgsFeatureRequest()
            if bbox:
                rect = QgsRectangle(*bbox)
                request.setFilterRect(rect)
            if attributes:
                request.setSubsetOfAttributes(attributes, lyr.pendingFields())
            if not geometry:
                request.setFlags(QgsFeatureRequest.NoGeometry)
            if feature_filter:
                request.setFilterExpression(feature_filter)
                #lyr.setSubsetString(feature_filter)

        # return listoffeatures
        # filter is maybe a QgsFeatureRequest
        # http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html#iterating-over-a-subset-of-features
        return list(lyr.getFeatures(request) if request else lyr.getFeatures())

    def _connectlayer(self, feature_type):
        url = self.filename+"|layername="+feature_type.tablename
        vlayer = QgsVectorLayer(url, "layer_name_you_like", "ogr")
        if not vlayer.isValid():
            raise( InvalidLayerException(url + " is not a valid layer") )
        return vlayer

print "Before main"
if __name__ == '__main__':
    import qgisapp
    with qgisapp.QgisStandaloneApp(True) as app:
        print "App initialised"
        rep = Repository(u'/Volumes/Macintosh HD/Users/asger/Code/qgis-GeoDanmarkCheck/testdata/fot5.sqlite')
        print rep.read(FeatureType.BYGNING)



