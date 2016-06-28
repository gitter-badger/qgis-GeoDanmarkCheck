from qgis.core import QgsApplication, QgsProviderRegistry
import os

# https://gist.github.com/spara/1251012
# http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts

class QgisStandaloneApp():

    def __init__(self, printdebuginfo=False):
        self.printdebuginfo = printdebuginfo

    def __enter__(self):
        # supply path to qgis install location
        prefix_path = '/Applications/QGIS.app/Contents/MacOS'
        os.environ["QGIS_PREFIX_PATH"] = prefix_path

        if self.printdebuginfo:
            print "Setting QGIS_PREFIX_PATH to: ", prefix_path

        # Using QgsApplication.setPrefixPath doesnt seem to work
        #QgsApplication.setPrefixPath(prefix_path, True)

        # create a reference to the QgsApplication, setting the
        # second argument to False disables the GUI
        qgs = QgsApplication([], False)

        # load providers
        qgs.initQgis()

        if self.printdebuginfo:
            print self.debuginfo()

        return qgs

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        QgsApplication.exitQgis()

    def debuginfo(self):
        QgsApplication.showSettings()
        print "Providers:"
        providers = QgsProviderRegistry.instance().providerList()
        for provider in providers:
            print provider