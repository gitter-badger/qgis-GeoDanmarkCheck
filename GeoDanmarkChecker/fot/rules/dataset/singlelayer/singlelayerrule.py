from ..datasetrule import DatasetRule

# Rules applying to one layer at a time
class SingleLayerRule(DatasetRule):
    def __init__(self, feature_type, filter = None):
        super(SingleLayerRule, self).__init__()
        self._feature_type = feature_type
        assert not filter or isinstance(filter, str)
        self._filter = filter

    def featuretype(self):
        """Returns the featuretype which this rule applies to"""
        return self._feature_type

    def filter(self):
        """Returns a QgsFeatureRequest (or subclass) which could be applied to features before passing to this rule"""
        return self._filter

    def checkmany(self, features, reporter, prefiltered=False):
        raise NotImplementedError

    def execute(self, repo, errorreporter, progressreporter):
        features = repo.read(self.featuretype(),
                                 attributes=self.attributesneeded,
                                 geometry=self.geometryneeded,
                                 feature_filter=self.filter)
        print "got", len(features), "features"
        self.checkmany(features, errorreporter)