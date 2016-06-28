from singlefeaturerule import SingleFeatureRule
from GeoDanmarkChecker.fot.geomutils import shortestline

class UniqueAttributeValue(SingleFeatureRule):
    def __init__(self, feature_type, attributename, filter=None):
        super(UniqueAttributeValue, self).__init__(feature_type, filter=filter)
        self.attributename = attributename
        self.attributevalues = {}
        self.rulename = "UniqueAttribute"

    def checkmany(self, feature, reporter):
        try:
            value = feature[self.attributename]
            if value in self.attributevalues:
                # Wooops not unique!
                errorgeom = shortestline(feature, self.attributevalues[value])
                reporter.reportError(self.rulename, self.featuretype(), self.attributename + "=" + str(value) + " not unique", errorgeom)
        except:
            reporter.reportError(self.rulename, self.featuretype(), "Error processing attribute: " + self.attributename, feature)