class FeatureType(object):

    def __init__(self, name, tablename, displayname):
        self.name = name
        self.tablename = tablename
        self.displayname = displayname

    def __repr__(self):
        return self.name


featuretypes = []

BYGNING = FeatureType('BYGNING', 'bygning', '')
featuretypes.append(BYGNING)

VINDMOELLE = FeatureType('VINDMOELLE', 'vindmoelle', '')
featuretypes.append(VINDMOELLE)

VANDLOEBSMIDTE_BRUDT = FeatureType('VANDLOEBSMIDTE_BRUDT', 'vandloebsmidte_brudt', '')
featuretypes.append(VANDLOEBSMIDTE_BRUDT)

VEJMIDTE_BRUDT = FeatureType('VEJMIDTE_BRUDT', 'vejmidte_brudt', '')
featuretypes.append(VEJMIDTE_BRUDT)