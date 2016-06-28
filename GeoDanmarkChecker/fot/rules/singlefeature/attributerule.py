from singlefeaturerule import SingleFeatureRule


class AttributeInList(SingleFeatureRule):

    def __init__(self, feature_type, attributename, validvalues, filter=None):
        super(AttributeInList, self).__init__(feature_type, filter)
        self.attributename = attributename
        self.validvalues = validvalues

    def check(self, feature, reporter):
        try:
            value = feature[self.attributename]
            if not value in self.validvalues:
                reporter.reportError("AttibuteInList", self.attributename + "=" + str(value) + " not valid", feature)
        except:
            reporter.reportError("")
