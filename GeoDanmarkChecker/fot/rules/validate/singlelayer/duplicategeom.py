from .singlelayerrule import SingleLayerRule
from ....geomutils.segmentmatcher import SegmentMatchFinder

class DuplicateLineStringLayerGeometries(SingleLayerRule):
    def __init__(self, name, feature_type, segmentize=2, equalstolerance=0.1, filter=None):
        super(DuplicateLineStringLayerGeometries, self).__init__(name, feature_type)
        self.filter = filter
        self.segmentize = float(segmentize)
        self.equalstolerance = float(equalstolerance)

    def checkmany(self, features, reporter, progressreporter):
        progressreporter.begintask(self.name, len(features))

        segmentmatchfinder = SegmentMatchFinder(features, segmentize=self.segmentize)
        for f in features:
            for sm in segmentmatchfinder.findmatching(f, maxdistance=self.equalstolerance):
                f2 = sm.nearestfeature
                if f != f2:
                    reporter.error(self.name, self.featuretype,
                                   "Possible duplicate geometry", sm.togeometry())
            progressreporter.completed_one()