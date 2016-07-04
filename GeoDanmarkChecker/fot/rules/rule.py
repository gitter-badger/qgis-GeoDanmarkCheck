class Rule(object):
    def __init__(self, name):
        self.name = name

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        """Executes the rule. Must be overridden"""
        raise NotImplementedError()