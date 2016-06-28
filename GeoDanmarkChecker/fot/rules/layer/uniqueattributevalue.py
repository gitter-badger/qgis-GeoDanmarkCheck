from layerrule import LayerRule
from GeoDanmarkChecker.fot.geomutils import shortestline

class UniqueAttributeValue(LayerRule):
    def __init__(self, feature_type, attributename, filter=None):
        super(UniqueAttributeValue, self).__init__(feature_type)
        self.filter = filter
        self.attributesneeded = attributename
        self.attributename = attributename
        self.attributevalues = {}
        self.rulename = "UniqueAttribute"

    def checkmany(self, features, reporter):
        for feature in features:
            try:
                value = feature[self.attributename]
                if value in self.attributevalues:
                    # Wooops not unique!
                    errorgeom = shortestline(feature, self.attributevalues[value])
                    reporter.reportError(self.rulename, self.featuretype(), self.attributename + "=" + str(value) + " not unique", errorgeom)
                else:
                    self.attributevalues[value] = feature
            except:
                reporter.reportError(self.rulename, self.featuretype(), "Error processing attribute: " + self.attributename, feature)