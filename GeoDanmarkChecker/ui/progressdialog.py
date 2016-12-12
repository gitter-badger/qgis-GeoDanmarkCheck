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
from PyQt4.QtGui import (
    QApplication,
    QDialog,
    QDialogButtonBox
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
        self.clear()

    def clear(self):
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(False)
        self.output_text.clear()

    def enable_close(self):
        self.buttonBox.button(QDialogButtonBox.Close).setEnabled(True)

    def add_message(self, text):
        self.output_text.appendPlainText(text)

    def begintask(self, taskname, tasksize):
        self.progress_bar.setRange(0, tasksize)
        self.add_message('Currently processing rule: ' + taskname)
        super(ProgressDialog, self).begintask(taskname, tasksize)

    def completed(self, completed):
        QApplication.processEvents()
        super(ProgressDialog, self).completed(completed)

    def completed_all(self):
        self.add_message('Done!')

    def _report(self):
        self.progress_bar.setValue(self.taskcompleted)
        QApplication.processEvents()
