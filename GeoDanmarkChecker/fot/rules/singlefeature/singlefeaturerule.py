# Rules regarding a single object
from GeoDanmarkChecker.fot.rules.rule import Rule
from qgis.core import QgsFeatureRequest
# from singlefeatureexecutor import SingleFeatureExecutor

class SingleFeatureRule(Rule):

    #_executor =  SingleFeatureExecutor()

    def __init__(self, feature_type):
        super(SingleFeatureRule, self).__init__()
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

