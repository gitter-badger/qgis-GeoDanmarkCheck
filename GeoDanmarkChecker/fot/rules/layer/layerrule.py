from GeoDanmarkChecker.fot.rules.rule import Rule
from qgis.core import QgsFeatureRequest

# Rules applying to the total set of objects. Like UUIDs being globally unique
class LayerRule(Rule):
    def __init__(self, feature_type, filter = None):
        super(LayerRule, self).__init__()
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