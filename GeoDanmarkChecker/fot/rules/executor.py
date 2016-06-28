from singlefeature.singlefeatureexecutor import SingleFeatureExecutor
from layer.layerruleexecutor import LayerRuleExecutor

class SingleRepoExecutor():

    def __init__(self, repo, rules, reporter, progress=None):
        self.repo = repo
        self.rules = rules
        self.reporter = reporter
        self.progress = progress
        self.executors = [SingleFeatureExecutor(), LayerRuleExecutor()]

    def execute(self):
        unhandledrules = self.rules
        for e in self.executors:
            handledrules = [r for r in unhandledrules if e.handles(r)]
            e.execute(self.repo, self.reporter, handledrules)
            unhandledrules = [r for r in unhandledrules if not r in handledrules]

        if unhandledrules:
            raise NotImplementedError("Not all rules where executed")
        


