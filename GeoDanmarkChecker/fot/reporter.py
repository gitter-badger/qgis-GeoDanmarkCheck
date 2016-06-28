from qgis.core import QgsFeature, QgsGeometry

class Reporter:

    def __init__(self, outputfile):
        self.outputfile = outputfile

    def reportError(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "error")

    def reportWarning(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "warning")

    def report(self, rulename, typeinfo, message, geometry, level):
        if isinstance(geometry, QgsFeature):
            geometry = geometry.geometry()
        print level, rulename, typeinfo, message, geometry.exportToWkt(2)