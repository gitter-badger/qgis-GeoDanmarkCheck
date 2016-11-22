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

from PyQt4.QtGui import (
    QTreeWidget,
    QTreeWidgetItem,
    QTreeWidgetItemIterator
)
from PyQt4.QtCore import (
    Qt,
    pyqtSlot
)


class RulesTreeWidget(QTreeWidget):
    def __init__(self, parent=None, rules={}):
        super(RulesTreeWidget, self).__init__(parent)
        self.rules_set = rules
        self.setColumnCount(1)
        self.itemChanged.connect(self._tree_item_changed)
        if self.rules_set:
            self._fill_tree()
            self.setHeaderLabel(self.rules_set.name)

    @pyqtSlot(QTreeWidgetItem, int)
    def _tree_item_changed(self, item, column):
        """ Triggered on a change event of a Tree Widget. """
        checked = item.checkState(column) == Qt.Checked

        # Special choose all TreeWidget
        if item.display_name == 'All':
            self.check_all(check=checked)
            return

        # We just checked a parent node
        if checked and not item.parent():
            self._check_all_childen(item)

        # We just unchecked a parent node
        if not checked and not item.parent():
            self._check_all_childen(item, check=False)

    def update_tree(self):
        print(self.rules_set)
        if self.rules_set:
            self._fill_tree()
            return

        self._set_root_path_message(
            self.trUtf8('No rules configured.')
        )

    def _fill_tree(self):
        """ Fills the tree with items. """
        if len(self.rules_set) < 1:
            self._set_root_path_message(
                self.trUtf8('No rules configured.')
            )
            return

        self.clear()
        self.setHeaderLabel(self.rules_set.name)
        self.addTopLevelItem(TreeWidgetItem('All'))

        for key, rules in self.rules_set.rules.iteritems():
            # Create the root item
            base_item = self._create_widget_item(key, None)
            # Fill the rules tree from the baseitem
            self._fill_tree_recursively(base_item, rules)
            self.addTopLevelItem(base_item)
            base_item.setFirstColumnSpanned(True)
            base_item.setExpanded(self.rules_set.expanded[key])

    def _fill_tree_recursively(self, base_item, rules):
        """ Fills a base item with rules """
        for rule in rules:
            rule_widget = self._create_widget_item(rule.name, rule)
            base_item.addChild(rule_widget)

    def _set_root_path_message(self, message):
        self.clear()
        base_item = QTreeWidgetItem([message])
        font = base_item.font(0)
        font.setItalic(True)
        base_item.setFont(0, font)
        self.addTopLevelItem(base_item)

    def _create_widget_item(self, rule_name, rule):
        """ Creates a widget item from a rule object. """
        return TreeWidgetItem(rule_name, rule)

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

    def check_all(self, check=True):
        """ Checks or uncheck all

        Args:
            check: true if check, false if uncheck
        """
        status = Qt.Checked if check else Qt.Unchecked
        iterator = QTreeWidgetItemIterator(self)
        item = iterator.value()
        while item:
            item.setCheckState(0, status)
            iterator += 1
            item = iterator.value()

    def get_rules(self):
        """ Returns a list of the checked off rules """
        rules = []

        iterator = QTreeWidgetItemIterator(self)
        item = iterator.value()
        while item:
            if item.checkState(0) == Qt.Checked and item.rule:
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
        self.display_name = name
        self.setText(0, name)
        self.setFont(0, font)
