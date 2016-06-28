# Rules regarding a single object
from GeoDanmarkChecker.fot.rules.rule import Rule
class SingleFeatureRule(Rule):

    def __init__(self, rulename, feature_type, filter = None):
        self.rulename = rulename
        self.feature_type = feature_type
        self.filter = filter

    def rulename(self):
        return self.rulename

    def featuretype(self):
        """Returns the featuretype which this rule applies to"""
        return self.feature_type

    def filter(self):
        """Returns a QgsFeatureRequest (or subclass) which could be applied to features before passing to this rule"""
        return self.filter

    def checkmany(self, features, reporter, prefiltered = False):
        if self.filter and not prefiltered:
            features = [f for f in features if filter.acceptFeature(f)]
        for f in features:
            self.check(f, reporter)

    def check(self, feature, reporter):
        raise NotImplementedError()

