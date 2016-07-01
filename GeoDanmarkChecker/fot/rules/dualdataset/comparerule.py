from .. import Rule

class CompareRule(Rule):

    def __init__(self, name):
        super(CompareRule, self).__init__(name)

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        """Executes the rule. Must be overridden"""
        raise NotImplementedError()
