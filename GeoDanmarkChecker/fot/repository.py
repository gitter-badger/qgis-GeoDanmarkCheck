from qgis.core import QgsVectorLayer, QgsFeatureRequest, QgsRectangle

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
            raise( Exception(url + " is not a valid layer") )
        return vlayer

print "Before main"
if __name__ == '__main__':
    import qgisapp
    with qgisapp.QgisStandaloneApp(True) as app:
        print "App initialised"
        rep = Repository(u'/Volumes/Macintosh HD/Users/asger/Code/qgis-GeoDanmarkCheck/testdata/fot5.sqlite')
        print rep.read(FeatureType.BYGNING)



