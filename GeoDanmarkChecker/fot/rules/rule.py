class Rule(object):
    def __init__(self, attributesneeded=None, geometryneeded=True, filter=""):
        self.attributesneeded = attributesneeded
        self.geometryneeded = geometryneeded
        self.filter = filter
