from .singlefeaturerule import SingleFeatureRule


class AttributeRule(SingleFeatureRule):

    def __init__(self, name, feature_type, attributename, isvalidfunction, filter=None):
        super(AttributeRule, self).__init__(name, feature_type)
        self.filter = filter
        self.attributename = attributename
        self.isvalidfunction = isvalidfunction

    def check(self, feature, reporter):
        try:
            value = feature[self.attributename]
            if not self.isvalidfunction(value):
                reporter.reportError(self.name, self.featuretype(),self.attributename + "=" + str(value) + " not valid", feature)
        except:
            reporter.reportError(self.name, self.featuretype(), "Error processing attribute: " + self.attributename, feature)
