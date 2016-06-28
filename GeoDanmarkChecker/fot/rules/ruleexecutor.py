from GeoDanmarkChecker.fot.rules import Rule
from GeoDanmarkChecker.fot.repository import Repository
from GeoDanmarkChecker.fot.rules.compare.comparerule import CompareRule
from GeoDanmarkChecker.fot.rules.dataset.datasetrule import DatasetRule

class RuleExecutor:

    def __init__(self, beforerepo, afterrepo):
        if not isinstance(beforerepo, Repository):
            raise TypeError("beforerepo is not a Repository")
        if not isinstance(afterrepo, Repository):
            raise TypeError("afterrepo is not a Repository")

        self.before = beforerepo
        self.after = afterrepo

    def execute(self, rules, errorreporter, progressreporter):
        for r in rules:
            if not isinstance(r, Rule):
                raise Exception("Unknown rule type: " + type(r))

            if isinstance(r, CompareRule):
                r.execute(self.before, self.after, errorreporter, progressreporter)
            elif isinstance(r, DatasetRule):
                # For now just execute on after case. Maybe allow user to select
                r.execute(self.after, errorreporter, progressreporter)
            else:
                raise TypeError("Unkown rule type: " + r)

