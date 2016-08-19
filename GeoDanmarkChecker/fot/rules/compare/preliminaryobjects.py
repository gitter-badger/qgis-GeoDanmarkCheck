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

from .comparerule import CompareRule
from ...repository import Repository
from ...geomutils import FeatureIndex, geometryequal, shortestline, changedattributes
from ...geomutils.featurematcher import MatchFinder


class PreliminaryObjectsRule(CompareRule):

    def __init__(self, name, feature_type, ispreliminaryfunction, nearbymatcher):
        super(PreliminaryObjectsRule, self).__init__(name)
        self.featuretype = feature_type
        self.idcolumn = self.featuretype.id_attribute

        if not hasattr(ispreliminaryfunction, '__call__'):
            raise TypeError("ispreliminary function must be a function")
        self.ispreliminary = ispreliminaryfunction
        self.nearbymatcher = nearbymatcher

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype)
        afterfeats = afterrepo.read(self.featuretype)

        preliminary_objects = [x for x in beforefeats if self.ispreliminary(x)]

        progressreporter.begintask(self.name, len(preliminary_objects))

        beforeindex = FeatureIndex(beforefeats, usespatialindex=False, indexedattributes=[self.idcolumn])
        afterindex = FeatureIndex(afterfeats, usespatialindex=False, indexedattributes=[self.idcolumn])
        nearbyfinder = MatchFinder(afterfeats)

        for f in preliminary_objects:
            progressreporter.completed_one() # At the beginning because of the continues

            fot_id = f[self.idcolumn]
            prelim_after = afterindex.attributeequals(self.idcolumn, fot_id)

            # Does the prelim object exist in the "after" dataset
            isdeleted = len(prelim_after) == 0

            # Is it still preliminiary
            if not isdeleted:
                if self.ispreliminary(prelim_after[0]):
                    # was anything changed?
                    if not geometryequal(f, prelim_after[0]):
                        errorreporter.error(
                            self.name,
                            self.featuretype,
                            'Preliminary object ({0}="{1}") geometry changed but still preliminary'.format(self.idcolumn, fot_id),
                            f)
                    changed_attributes = changedattributes(f, prelim_after[0])
                    if changed_attributes:
                        errorreporter.error(
                            self.name,
                            self.featuretype,
                            'Preliminary object ({0}="{1}") attributes changed but still preliminary'
                                .format(self.idcolumn, fot_id),
                            f)

            # Are there any objects of the same type "nearby"
            nearby = nearbyfinder.findmatching(f, self.nearbymatcher)

            # Check if one of the nearby objects is newly registered
            new_object = None
            for match in nearby:
                # Is idcolumn==None => object is new
                matching_feature = match.feature2
                if matching_feature[self.idcolumn] is None:
                    new_object = matching_feature
                    break
                # Is idcolumn not found in the before dataset
                sameids = beforeindex.attributeequals(self.idcolumn, matching_feature[self.idcolumn])
                if len(sameids) == 0:
                    new_object = matching_feature
                    break

            if isdeleted and not new_object:
                errorreporter.error(
                    self.name,
                    self.featuretype,
                    'Preliminary object ({0}="{1}") deleted without new object registered'.format(self.idcolumn, fot_id),
                    f)
                continue

            if new_object and not isdeleted:
                errorreporter.warning(
                    self.name,
                    self.featuretype,
                    'Preliminary object ({0}="{1}") not deleted but new object registered'.format(self.idcolumn, fot_id),
                    shortestline(f, new_object))



