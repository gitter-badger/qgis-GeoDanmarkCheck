from .comparerule import CompareRule
from ... import Repository

class AttributesMustNotBeChanged(CompareRule):
    def __init__(self, name, feature_type, unchangedattributes, featurematcher):
        super(AttributesMustNotBeChanged, self).__init__(name)
        self.featuretype = feature_type
        self.unchangedattributes = unchangedattributes
        self.matcher = featurematcher

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype, attributes=self.unchangedattributes)
        afterfeats = afterrepo.read(self.featuretype, attributes=self.unchangedattributes)

        for m in self.matcher.match(beforefeats, afterfeats):
            f1 = m.feature1
            f2 = m.feature2
            for attrib in self.unchangedattributes:
                if not f1[attrib] == f2[attrib]:
                    message = "Attribute {0} changed from {1} to {2}".format(attrib, f1[attrib], f2[attrib])
                    errorreporter.reportError(self.name, self.featuretype, message, m.matchgeometry)
