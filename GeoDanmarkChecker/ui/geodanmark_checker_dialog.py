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
    QFileDialog,
    QTreeWidgetItem,
    QTreeWidgetItemIterator
)
from PyQt4.QtCore import (
    Qt,
    pyqtSlot
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
        self.rules_set = rules
        self.checked_off = set()

        self.before_dataset.clicked.connect(self.select_before_file)
        self.after_dataset.clicked.connect(self.select_after_file)

        self.rules_tree.setColumnCount(1)
        self.rules_tree.setHeaderLabel(rules.name)
        self.rules_tree.itemChanged.connect(self._tree_item_changed)

        # Draw the tree
        self._fill_tree()

    def select_before_file(self):
        self.before_dataset_input.setText(QFileDialog.getOpenFileName())

    def select_after_file(self):
        self.after_dataset_input.setText(QFileDialog.getOpenFileName())

    def _create_widget_item(self, rule_name, rule):
        """ Creates a widget item from a rule object. """
        return TreeWidgetItem(rule_name, rule)

    def _fill_tree(self):
        """ Fills the tree with items. """
        if len(self.rules_set) < 1:
            self._set_root_path_message(
                self.trUtf8('No rules configured.')
            )
            return

        self.rules_tree.clear()

        for key, rules in self.rules_set.rules.iteritems():
            # Create the root item
            base_item = self._create_widget_item(key, None)
            # Fill the rules tree from the baseitem
            self._fill_tree_recursively(base_item, rules)
            self.rules_tree.addTopLevelItem(base_item)
            base_item.setFirstColumnSpanned(True)
            base_item.setExpanded(True)
        # TODO: Figure out if below is needed
        # if self.filterLineEdit.text().strip():
        #     self._expandTree()

    def _fill_tree_recursively(self, base_item, rules):
        """ Fills a base item with rules """
        for rule in rules:
            rule_widget = self._create_widget_item(rule.name, rule)
            base_item.addChild(rule_widget)

    def _set_root_path_message(self, message):
        self.rules_tree.clear()
        base_item = QTreeWidgetItem([message])
        font = base_item.font(0)
        font.setItalic(True)
        base_item.setFont(0, font)
        self.rules_tree.addTopLevelItem(base_item)

    @pyqtSlot(QTreeWidgetItem, int)
    def _tree_item_changed(self, item, column):
        """ Triggered on a change event of a Tree Widget. """
        checked = item.checkState(column) == Qt.Checked
        # We just checked a parent node
        if checked and not item.parent():
            self._check_all_childen(item)

        # We just unchecked a parent node
        if not checked and not item.parent():
            self._check_all_childen(item, check=False)

    def _check_all_childen(self, parent, check=True):
        """ Checks or uncheck all

        Args:
            parent: QTreeWidgetItem with children
            check: true if check, false if uncheck
        """
        status = Qt.Checked if check else Qt.Unchecked
        for i in range(parent.childCount()):
            item = parent.child(i)
            item.setCheckState(0, status)

    def get_rules(self):
        """ Returns a lost of the checked off rules """
        rules = []

        iterator = QTreeWidgetItemIterator(self.rules_tree)
        item = iterator.value()
        while item:
            if item.rule:
                rules.append(item.rule)
            iterator += 1
            item = iterator.value()

        return rules


class TreeWidgetItem(QTreeWidgetItem):
    """ An item in the Tree Widget. """
    def __init__(self, name, rule=None, checked=None, icon=None):
        """ Constructor. Sets the properties for display """
        super(TreeWidgetItem, self).__init__()
        self.rule = rule
        self.display_name = name
        # self.subchecked = checked_sub_paths
        self.subchecked = None
        if icon:
            self.setIcon(0, icon)
        self.setToolTip(0, self.display_name)
        self.setCheckState(0, Qt.Unchecked if not checked else Qt.Checked)
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.update_display()

    def update_display(self):
        """ Updates the display, sets the font, displayname. """
        name = self.display_name
        font = self.font(0)
        font.setBold(False)
        if self.subchecked:
            name += ' ({0})'.format(self.subchecked)
            font.setBold(True)
        self.display_name = name
        self.setText(0, name)
        self.setFont(0, font)

    def set_sub_checked(self, num):
        """ Sets a sub-item to checked.

        Args:
            num: The number of the item.
        """
        self.subchecked = num
        self.update_display()