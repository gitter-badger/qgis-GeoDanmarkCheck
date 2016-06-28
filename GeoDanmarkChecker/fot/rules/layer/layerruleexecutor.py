from layerrule import GlobalRule
from GeoDanmarkChecker.fot.repository import Repository

class SingleFeatureExecutor():

    def __init__(self):
        pass

    def handles(self, rule):
        return isinstance(rule, GlobalRule)

    def execute(self, repo, reporter, rules):
        # Dont optimize for now. Later bundle all rules for the same feature_type
        for r in rules:
            if not isinstance(r, GlobalRule):
                raise TypeError("Unexpected type")
            #if not isinstance(repo, Repository):
            #    raise TypeError("Unexpected type")

            features = repo.read(r.featuretype(), r.filter())
            print "got", len(features), "features"
            r.checkmany(features, reporter, prefiltered=True)

