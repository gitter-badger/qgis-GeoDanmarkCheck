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
from ..repository import InvalidLayerException, Repository
from . import Rule
from .compare.comparerule import CompareRule
from .validate.datasetrule import DatasetRule

class RuleExecutor:

    def __init__(self, beforerepo, afterrepo):
        if not isinstance(beforerepo, Repository):
            raise TypeError("beforerepo is not a Repository")
        if not isinstance(afterrepo, Repository):
            raise TypeError("afterrepo is not a Repository")

        self.before = beforerepo
        self.after = afterrepo

    def execute(self, rules, errorreporter, progressreporter):
        for r in rules:
            if not isinstance(r, Rule):
                raise Exception("Unknown rule type: " + str(r))

            try:
                if isinstance(r, CompareRule):
                    r.execute(self.before, self.after, errorreporter, progressreporter)
                elif isinstance(r, DatasetRule):
                    # For now just execute on after case. Maybe allow user to select
                    r.execute(self.after, errorreporter, progressreporter)
                else:
                    raise TypeError("Unkown rule type: " + str(r))
            except InvalidLayerException as e:
                errorreporter.error(
                    r.name, "", "Exception when processing rule {0}. Message: {1}".format(r.name, str(e)), None)

