# Rules regarding a single object
from singlelayerrule import SingleLayerRule
from qgis.core import QgsFeatureRequest

class SingleFeatureRule(SingleLayerRule):

    #_executor =  SingleFeatureExecutor()

    def __init__(self, name, feature_type):
        super(SingleLayerRule, self).__init__(name)
        self._feature_type = feature_type

    def featuretype(self):
        """Returns the featuretype which this rule applies to"""
        return self._feature_type

    def checkmany(self, features, reporter):
        for f in features:
            self.check(f, reporter)

    def check(self, feature, reporter):
        raise NotImplementedError()

    #def executor(self):
    #    return SingleFeatureRule._executor

