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

from PyQt4 import uic
from PyQt4.QtGui import (
    QDialog,
    QFileDialog
)

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(
        os.path.dirname(__file__),
        'geodanmark_checker_dialog_base.ui'
    )
)


class GeoDanmarkCheckerDialog(QDialog, FORM_CLASS):
    def __init__(self, rules, parent=None):
        """ Takes a set of rules and creates a QTreeWidget of them

        Args:
            rules: set of rules of some sort, is WIP
        """
        super(GeoDanmarkCheckerDialog, self).__init__(parent)
        self.setupUi(self)

        # Setup comparison rules
        self.rules_compare.rules_set = rules[0]
        self.rules_compare.update_tree()

        # Setup validation rules
        self.rules_validate.rules_set = rules[1]
        self.rules_validate.update_tree()

        self.before_dataset.clicked.connect(self.select_before_file)
        self.after_dataset.clicked.connect(self.select_after_file)

    def select_before_file(self):
        # http://stackoverflow.com/questions/23002801/pyqt-how-to-make-getopenfilename-remember-last-opening-path
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            self.before_dataset_input.setText(dialog.selectedFiles()[0])

    def select_after_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            self.after_dataset_input.setText(dialog.selectedFiles()[0])