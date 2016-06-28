class FeatureIndex():
    # http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html#using-spatial-index

    def __init__(self, featuretype):
        pass

    def insert(self, features):
        # validate wrt featuretype?
        # insert all features into index
        pass

    def intersects(self, geom_or_feature_filter):
        pass