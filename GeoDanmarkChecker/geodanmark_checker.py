# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoDanmarkChecker
                                 A QGIS plugin
 This plugin provides methods to check GeoDanmark data
                              -------------------
        begin                : 2016-06-20
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Septima
        email                : asger@septima.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import (
    QSettings,
    QTranslator,
    qVersion,
    QCoreApplication
)
from PyQt4.QtGui import (
    QAction,
    QIcon
)
from qgis.core import (
    QgsMapLayerRegistry,
    QgsDataSourceURI,
    QgsVectorLayer
)
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from .ui.geodanmark_checker_dialog import GeoDanmarkCheckerDialog
from .rules import rules_set
from fot.reporter import Reporter
# from fot.progress import ProgressReporter
from .ui.progressdialog import ProgressDialog
from fot.repository import Repository
from fot.rules import RuleExecutor
import os.path


class GeoDanmarkChecker:
    """ QGIS Plugin Implementation. """

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # For github-updater
        self.github_owner = 'Septima'
        self.github_repository = 'qgis-GeoDanmarkCheck'

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeoDanmarkChecker_{}.qm'.format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        rules = rules_set
        self.dlg = GeoDanmarkCheckerDialog(rules)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GeoDanmark Checker')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeoDanmarkChecker', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # Try and setup github updater
        try:
            from github import addUpdatePluginMenu
            addUpdatePluginMenu(
                "GeoDanmark Checker",
                self.github_owner,
                self.github_repository
            )
        except ImportError:
            pass

        self.check_geodanmark_action = QAction(
            QIcon(':/plugins/GeoDanmarkChecker/icon.png'),
            self.tr(u'Check GeoDanmark Data'),
            self.iface.mainWindow()
        )
        self.check_geodanmark_action.triggered.connect(self.run)
        self.check_geodanmark_action.setEnabled(True)
        self.iface.addPluginToMenu(self.menu, self.check_geodanmark_action)
        self.iface.addToolBarIcon(self.check_geodanmark_action)
        self.actions.append(self.check_geodanmark_action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        # Try and remove the github updater plugin menu
        try:
            from github import removeUpdatePluginMenu
            removeUpdatePluginMenu("GeoDanmark Checker")
        except ImportError:
            pass

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&GeoDanmark Checker'),
                action
            )
            self.iface.removeToolBarIcon(action)

    def add_spatialite_layer(self, sqlite):
        """ Adds an sqlite database as layers, expects layers: linestring,
        point and polygon. """

        tables = ['linestring', 'point', 'polygon']
        for table in tables:
            uri = QgsDataSourceURI()
            uri.setDatabase(sqlite)
            uri.setDataSource('', table, 'GEOMETRY')
            # Create new layer
            layer = QgsVectorLayer(uri.uri(), table, 'spatialite')
            if not layer:
                print('error creating layer')
            # Set encoding on the layer
            layer.setProviderEncoding(u'UTF-8')
            layer.dataProvider().setEncoding(u'UTF-8')
            # TODO: uncomment below once we have the style available
            # layer.loadNamedStyle('default_style.gml')
            # Add layer to qgis
            if not QgsMapLayerRegistry.instance().addMapLayer(layer):
                print('Unable to add layer: {}'.format(table))

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        print('Test')
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            before_file = self.dlg.before_dataset_input.text()
            after_file = self.dlg.after_dataset_input.text()
            if not before_file or not after_file:
                # TODO: error handling if no before/after file
                pass

            output_file = os.path.join(
                os.path.dirname(before_file),
                'geodk_check_output.sqlite'
            )
            reporter = Reporter(output_file)
            progress = ProgressDialog(self.iface.messageBar())

            rules = self.dlg.get_rules()
            exe = RuleExecutor(
                Repository(before_file),
                Repository(after_file)
            )
            exe.execute(rules, reporter, progress)
            self.add_spatialite_layer(output_file)
            # clean up the progress widgets
            self.iface.messageBar().clearWidgets()