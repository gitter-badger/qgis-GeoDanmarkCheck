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
import os
from ..fot.progress import ProgressReporter
from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QProgressBar,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QTextCursor
)

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'progressdialog.ui'
    )
)


class ProgressDialog(ProgressReporter, QDialog, FORM_CLASS):
    def __init__(self):
        super(ProgressReporter, self).__init__()
        self.setupUi(self)
        self._currentTaskName = None
        self._currentTaskProgressBar = None
        self._currentTaskIncidents = None
        self._currentTaskIncidentsWidget = None
        self._currentTaskMessages = 0

        self.clear()

    def clear(self):
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.output_text.clear()
        self.tableWidget.clear()

        self._currentTaskName = None
        self._currentTaskProgressBar = None
        self._currentTaskIncidents = None
        self._currentTaskIncidentsWidget = None
        self._currentTaskMessages = 0

        # Set up tablewidget
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setRowCount(0);
        self.tableWidget.setColumnCount(3)
        item = QTableWidgetItem()
        item.setText('Rule')
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setText('Progress')
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        item.setText('Incidents')
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        #self.tableWidget.horizontalHeader().setStretchLastSection(True)

    def enable_close(self):
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)

    def add_message(self, text):
        self.output_text.appendPlainText(text)
        self.output_text.moveCursor(QTextCursor.End)
        self.output_text.ensureCursorVisible()

    def begintask(self, taskname, tasksize):
        self._begintask(taskname, tasksize)

    def completed(self, completed):
        QApplication.processEvents()
        super(ProgressDialog, self).completed(completed)

    def completed_all(self):
        pass

    def _report(self):
        percentcompleted = 100.0 * self.taskcompleted / self.tasksize if self.tasksize > 0 else 100
        self._currentTaskProgressBar.setValue(percentcompleted)
        QApplication.processEvents()


    def _begintask(self, taskname, tasksize):
        """Internal code when a new task is seen"""
        if taskname != self._currentTaskName:
            self._currentTaskName = taskname
            #item = QTableWidgetItem(taskname, "ProgressBar", "Count")
            rowPosition = self.tableWidget.rowCount()  # necessary even when there are no rows in the table
            self.tableWidget.insertRow(rowPosition)
            self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(taskname))
            self._currentTaskProgressBar = QProgressBar()
            self.tableWidget.setCellWidget(rowPosition, 1, self._currentTaskProgressBar)
            self._currentTaskIncidentsWidget = QTableWidgetItem('0')
            self._currentTaskIncidentsWidget.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tableWidget.setItem(rowPosition, 2, self._currentTaskIncidentsWidget)
            self.tableWidget.scrollToBottom()
            self._currentTaskIncidents = 0
            self._currentTaskMessages = 0

        super(ProgressDialog, self).begintask(taskname, tasksize)

    # Error reporter
    def error(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, 'ERROR')

    def warning(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, 'Warning')

    def report(self, rulename, typeinfo, message, geometry, level):
        if rulename != self._currentTaskName:
            self._begintask(rulename, -1)
        self._currentTaskIncidents += 1
        self._currentTaskIncidentsWidget.setText(str(self._currentTaskIncidents))
        if geometry is None:
            if self._currentTaskMessages == 0:
                self.add_message('-----------------------------------------------------------')
                self.add_message('{} ({})'.format(self._currentTaskName, str(typeinfo)))
                self.add_message('-----------------------------------------------------------')
            self._currentTaskMessages += 1
            self.add_message('{}:\n{}'.format(level, message))


