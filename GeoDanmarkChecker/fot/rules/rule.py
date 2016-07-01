class Rule(object):
    def __init__(self, name, attributesneeded=None, geometryneeded=True, filter=""):
        self.attributesneeded = attributesneeded
        self.geometryneeded = geometryneeded
        self.filter = filter
        self.name = name

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        """Executes the rule. Must be overridden"""
        raise NotImplementedError()