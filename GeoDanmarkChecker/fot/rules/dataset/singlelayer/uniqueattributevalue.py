from .singlelayerrule import SingleLayerRule
from ....geomutils import shortestline

class UniqueAttributeValue(SingleLayerRule):
    def __init__(self, name, feature_type, attributename, filter=None):
        super(UniqueAttributeValue, self).__init__(name, feature_type)
        self.filter = filter
        self.attributesneeded = attributename
        self.attributename = attributename
        self.attributevalues = {}

    def checkmany(self, features, reporter, progressreporter):
        progressreporter.begintask(self.name, len(features))
        for feature in features:
            try:
                value = feature[self.attributename]
                if value in self.attributevalues:
                    # Wooops not unique!
                    errorgeom = shortestline(feature, self.attributevalues[value])
                    reporter.error(self.name, self.featuretype, self.attributename + "=" + unicode(value) + " not unique", errorgeom)
                else:
                    self.attributevalues[value] = feature
            except:
                reporter.error(self.name, self.featuretype, "Error processing attribute: " + self.attributename, feature)
            progressreporter.completed_one()