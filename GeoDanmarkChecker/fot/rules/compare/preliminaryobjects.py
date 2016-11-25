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
from ...exceptions import FotException
from ...geomutils import FeatureIndex, geometryequal, changedattributes
from ...geomutils.errorgeometry import createlinemarker, createpointmarker
from ...geomutils.featurematcher import MatchFinder, ExactGeometryMatcher


class PreliminaryObjectsRule(CompareRule):
    """Check that preliminary objects in the 'before' dataset are correctly handled in the 'after' dataset.

    Parameters
    ----------
    name : str
        Name if this rule instance.
    feature_type : fot.FeatureType
        Feature type to apply check to.
    ispreliminaryfunction : function(feature) returning bool
        Function accepting a feature returning True if the feature is preliminary.
    nearbymatcher : GeometryMatcher object
        Object like fot.geomutils.featurematcher.NearbyObjectsGeometryMatcher. This defines which 'after'-features
        are considered to be 'nearby' a preliminary 'before'-feature.
    sameobjectmatcher : GeometryMatcher object
        Object like fot.geomutils.featurematcher.OrientedHausdorffDistanceMatcher. This defines which 'after'-features
        are allowed to replace a preliminary 'before'-feature.

    """

    def __init__(self, name, feature_type, ispreliminaryfunction, nearbymatcher, sameobjectmatcher):
        super(PreliminaryObjectsRule, self).__init__(name)
        self.featuretype = feature_type
        self.idcolumn = self.featuretype.id_attribute

        if not hasattr(ispreliminaryfunction, '__call__'):
            raise TypeError("ispreliminary function must be a function")
        self.ispreliminary = ispreliminaryfunction
        self.nearbymatcher = nearbymatcher
        self.sameobjectmatcher = sameobjectmatcher

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        beforefeats = beforerepo.read(self.featuretype)
        afterfeats = afterrepo.read(self.featuretype)

        try:
            preliminary_objects = [x for x in beforefeats if self.ispreliminary(x)]
        except Exception as e:
            import sys
            raise FotException, \
                  FotException("'ispreliminary' fails for {} with error message: {}".format(self.featuretype, e.message)), \
                  sys.exc_info()[2]

        progressreporter.begintask(self.name, len(preliminary_objects))

        afterindex = FeatureIndex(afterfeats, usespatialindex=True, indexedattributes=[self.idcolumn])

        before_finder = MatchFinder(beforefeats)
        after_finder = MatchFinder(afterfeats)

        exactgeommatcher = ExactGeometryMatcher()

        for f in preliminary_objects:
            # Try to find the preliminary object in the 'after' dataset
            prelim_after = None
            fot_id = f[self.idcolumn] if f.fieldNameIndex(self.idcolumn) != -1 else None
            fot_id_matches = afterindex.attributeequals(self.idcolumn, fot_id) if fot_id else None
            if fot_id_matches:
                prelim_after = fot_id_matches[0]
            else:
                # No match on ID - try exact match on geometry. IDs may be screwed up
                m = after_finder.findmatching(f, exactgeommatcher)
                if m:
                    prelim_after = m[0].feature2

            # Find nearby objects of same type and geomstatus final
            nearby = after_finder.findmatching(f, self.nearbymatcher)
            # Sort by distance
            nearby = sorted(nearby, key=lambda m: m.matchscore)
            # Check if one of the (final) nearby objects is newly registered
            nearby_final = [m.feature2 for m in nearby if not self.ispreliminary(m.feature2)]
            nearby_edited_final_objects = []
            for matching_feature in nearby_final:
                # We are only interested in the nearest object which has been touched by the editor
                # The only way to figure out if the nearby object is newly registered is to do an exact geom match
                # against the 'before' situation.
                # match geom exactly against 'before'
                if not before_finder.findmatching(matching_feature, exactgeommatcher):
                    # This feature did not exist in the 'before' case. It has been touches by the editor
                    nearby_edited_final_objects.append(matching_feature)


            if prelim_after is not None:
                # The prelim object still exists
                if not self.ispreliminary(prelim_after):
                    # The object has been upgraded to final - all is good
                    pass
                else:
                    # It is still preliminary
                    changes = []
                    if not geometryequal(f, prelim_after):
                        changes.append('geometry changed')
                    changed_attributes = changedattributes(f, prelim_after)
                    if changed_attributes:
                        changes.append('attributes changed')
                    if changes:
                        # Something was changed - ERROR
                        message = 'Preliminary object ({0}="{1}") {2} but still preliminary'
                        message = message.format(self.idcolumn, fot_id,' and '.join(changes))
                        errorreporter.error( self.name, self.featuretype, message, f)
                    else:
                        # Preliminary object has not been changed at all
                        if len(nearby_edited_final_objects) == 0:
                            # Preliminary object hasnt been touched and no objects have been edited nearby - all good
                            pass
                        else:
                            # There is at least one final object nearby which has been edited
                            errorreporter.warning(
                                self.name,
                                self.featuretype,
                                'Preliminary object ({0}="{1}") not updated but new object registered nearby'.format(
                                    self.idcolumn, fot_id),
                                createlinemarker(f, nearby_edited_final_objects[0]))
            else:
                # The prelim object does not exist any more. It has been deleted (or geom changed and lost its ID)
                if len(nearby_edited_final_objects) == 0:
                    # No new object has replaced the prelim
                    errorreporter.error(
                        self.name,
                        self.featuretype,
                        'Preliminary object ({0}="{1}") deleted but no new object registered'.format(
                            self.idcolumn, fot_id),
                        f
                    )
                else:
                    # Prelim has been deleted and there IS at least one new object nearby
                    replacements_finder = MatchFinder(nearby_edited_final_objects)
                    # Features which are 'equal enough' to replace the prelim
                    replacement_objects = replacements_finder.findmatching(f, self.sameobjectmatcher)

                    if replacement_objects:
                        # At least one of the new objects replaces the prelim object. All is good
                        pass
                    else:
                        # None of the new objects replace the prelim object
                        errorreporter.error(
                            self.name,
                            self.featuretype,
                            'Preliminary object ({0}="{1}") deleted but no new object registered'.format(
                                self.idcolumn, fot_id),
                            f
                        )
            # Done checking this feature
            progressreporter.completed_one()









