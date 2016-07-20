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
from ..fot.progress import ProgressReporter
from PyQt4.QtGui import QProgressBar
from PyQt4.QtCore import Qt


class ProgressDialog(ProgressReporter):
    def __init__(self, iface):
        super(ProgressReporter, self).__init__()
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.iface = iface
        self.widget = None

    def begintask(self, taskname, tasksize):
        self.progress_bar.setRange(0, tasksize)

        self.widget = self.iface.messageBar().createMessage(
            taskname,
            " Progress:"
        )
        self.widget.layout().addWidget(self.progress_bar)
        self.iface.messageBar().pushWidget(
            self.widget,
            self.iface.messageBar().INFO
        )
        # TODO: maybe below is needed
        # self.iface.messageBar().clearWidgets()
        # self.iface.mapCanvas().refresh()
        super(ProgressDialog, self).begintask(taskname, tasksize)

    def completed_one(self):
        super(ProgressDialog, self).completed(self.taskcompleted + 1)
        self.progress_bar.setValue(self.taskcompleted)
