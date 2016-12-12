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


class ProgressReporter(object):
    def __init__(self):
        self.taskname = None
        self.tasksize = 0
        self.taskcompleted = 0
        self.taskcompletedpercentage = 0
        self.reportevery = 1
        self._nextreportat = 0

    def begintask(self, taskname, tasksize):
        self.taskname = taskname
        self.tasksize = tasksize
        self.reportevery = tasksize / 100.0
        self._nextreportat = 0
        self.completed(0)

    def completed(self, completed):
        self.taskcompleted = completed
        if completed >= self._nextreportat:
            self._report()
            self._nextreportat = min(self.tasksize, completed + self.reportevery)
        if completed == self.tasksize:
            self.completed_all()

    def completed_one(self):
        self.completed(self.taskcompleted + 1)

    def completed_all(self):
        pass

    def _report(self):
        # Better ways of reporting!
        percentcompleted = 100.0 * self.taskcompleted / self.tasksize if self.tasksize > 0 else 100
        print "{0} {1}% complete".format(self.taskname, percentcompleted)
