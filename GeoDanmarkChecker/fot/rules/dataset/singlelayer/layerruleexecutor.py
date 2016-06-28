from singlelayerrule import LayerRule
from GeoDanmarkChecker.fot.repository import Repository

class LayerRuleExecutor():

    def __init__(self):
        pass

    def handles(self, rule):
        return isinstance(rule, LayerRule)

    def execute(self, repo, reporter, rules):
        # Dont optimize for now. Later bundle all rules for the same feature_type
        for r in rules:
            if not isinstance(r, LayerRule):
                raise TypeError("Unexpected type")
            #if not isinstance(repo, Repository):
            #    raise TypeError("Unexpected type")

            features = repo.read(r.featuretype(),
                                 attributes=r.attributesneeded,
                                 geometry=r.geometryneeded,
                                 feature_filter=r.filter)
            print "got", len(features), "features"
            r.checkmany(features, reporter)

