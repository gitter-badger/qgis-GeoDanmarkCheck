class Rule(object):
    def __init__(self, attributesneeded=None, geometryneeded=True, filter=""):
        self.attributesneeded = attributesneeded
        self.geometryneeded = geometryneeded
        self.filter = filter

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        """Executes the rule. Must be overridden"""
        raise NotImplementedError()