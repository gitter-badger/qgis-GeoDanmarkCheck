from rule import Rule
from GeoDanmarkChecker.fot.repository import Repository
class RuleExecutor:
    def __init__(self, repo, reporter):
        if not isinstance(repo, Repository):
            raise TypeError("repo is not a Repository")

        self.repo = repo
        self.reporter = reporter
        self.executors = []

    def execute(self, rules):
        for r in rules:
            if not isinstance(r, Rule):
                raise Exception("Unknown rule type: " + type(r))

            # Do not optimise yet. Use same executor for all rules of same type to allow executor to optimise
            executor = r.executor()
            executor.execute(self.repo, reporter, rules)

