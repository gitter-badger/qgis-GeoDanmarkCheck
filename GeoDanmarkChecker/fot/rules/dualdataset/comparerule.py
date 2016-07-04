from .. import Rule

class CompareRule(Rule):

    def __init__(self, name, beforefilter=None, afterfilter=None):
        super(CompareRule, self).__init__(name)
        if beforefilter and not isinstance(beforefilter, str):
            raise TypeError()
        if afterfilter and not isinstance(afterfilter, str):
            raise TypeError()
        self.beforefilter = beforefilter
        self.afterfilter = afterfilter

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        """Executes the rule. Must be overridden"""
        raise NotImplementedError()
