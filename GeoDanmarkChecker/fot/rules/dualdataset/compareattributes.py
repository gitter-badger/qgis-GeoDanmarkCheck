from .comparerule import CompareRule
from ... import Repository
from ... import FeatureType
from ...geomutils.featurematcher import MatchFinder


class AttributesMustNotBeChanged(CompareRule):
    def __init__(self, name, feature_type, unchangedattributes, featurematcher, beforefilter=None, afterfilter=None):
        super(AttributesMustNotBeChanged, self).__init__(name, beforefilter, afterfilter)
        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        self.featuretype = feature_type
        self.unchangedattributes = unchangedattributes
        self.matcher = featurematcher

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype, attributes=self.unchangedattributes, feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, attributes=self.unchangedattributes, feature_filter=self.afterfilter)

        progressreporter.begintask(self.name, len(beforefeats))
        matchfinder = MatchFinder(afterfeats)
        for f in beforefeats:
            for m in matchfinder.findmatching(f, self.matcher):
                f1 = m.feature1
                f2 = m.feature2
                for attrib in self.unchangedattributes:
                    messages = []
                    if not f1[attrib] == f2[attrib]:
                        messages.append(u'Attribute {0} changed from {1} to {2}'.format(attrib, f1[attrib], f2[attrib]))
                    if messages:
                        errorreporter.error(self.name, self.featuretype, ';'.join(messages), m.matchgeometry)
            progressreporter.completed_one()
