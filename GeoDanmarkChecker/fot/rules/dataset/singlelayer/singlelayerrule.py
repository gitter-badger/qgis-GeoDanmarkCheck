from ..datasetrule import DatasetRule


# Rules applying to one layer at a time
class SingleLayerRule(DatasetRule):
    def __init__(self, name, feature_type, attributesneeded=None, geometryneeded=True, filter = None):
        super(SingleLayerRule, self).__init__(name)
        self.featuretype = feature_type
        assert not filter or isinstance(filter, str)
        self.attributesneeded = attributesneeded
        self.geometryneeded = geometryneeded
        self.filter = filter

    def checkmany(self, features, reporter, prefiltered=False):
        raise NotImplementedError

    def execute(self, repo, errorreporter, progressreporter):
        features = repo.read(self.featuretype,
                                 attributes=self.attributesneeded,
                                 geometry=self.geometryneeded,
                                 feature_filter=self.filter)
        print "got", len(features), "features"
        self.checkmany(features, errorreporter)