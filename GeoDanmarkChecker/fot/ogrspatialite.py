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

        Keyword arguments:
        layer_name -- name of the layer
        type -- ogr type of geometry in layer
        fields -- list of tuples of (field name, ogr field type)
        srs -- coordinate reference system, defaults to 25832
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

        Keyword arguments:
        layer_name -- name of the layer
        fields -- list of tuples of (field name, ogr field type)
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
        self.data_source = self.driver.CreateDataSource(
            self.path,
            options=[
                'SPATIALITE=YES',
                'INIT_WITH_EPSG=YES',
                'OGR_SQLITE_SYNCHRONOUS=OFF'
            ]
        )


