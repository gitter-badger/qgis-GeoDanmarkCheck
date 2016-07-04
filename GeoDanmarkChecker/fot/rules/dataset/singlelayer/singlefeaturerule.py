# Rules regarding a single object
from singlelayerrule import SingleLayerRule
from qgis.core import QgsFeatureRequest

class SingleFeatureRule(SingleLayerRule):

    #_executor =  SingleFeatureExecutor()

    def __init__(self, name, feature_type, attributesneeded=None, geometryneeded=True, filter = None):
        super(SingleFeatureRule, self).__init__(name, feature_type, attributesneeded, geometryneeded, filter)


    def checkmany(self, features, reporter):
        for f in features:
            self.check(f, reporter)

    def check(self, feature, reporter):
        raise NotImplementedError()

    #def executor(self):
    #    return SingleFeatureRule._executor

