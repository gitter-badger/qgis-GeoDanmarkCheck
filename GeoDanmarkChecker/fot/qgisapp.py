# -*- coding: utf-8 -*-
"""
Routines for quality control of GeoDanmark map data
Copyright (C) 2016
Developed by Septima.dk for the Danish Agency for Data Supply and Efficiency

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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