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
class RulesSet(object):
    """ Contains a rules set, a dict of 'category_name' : [list of rules] """

    def __init__(self, name):
        self.name = name
        self.rules = {}

    def __len__(self):
        return len(self.rules)

    def add_rule_category(self, category_name):
        self.rules[category_name] = []

    def add_rule(self, category_name, rule):
        self.rules[category_name].append(rule)


# TODO: We delete all this, it's just for temporary tests.
import fot.featuretype
from fot.rules.validate.singlelayer import UniqueAttributeValue
from fot.rules.validate.singlelayer import AttributeRule
from fot.rules.compare.compareattributes import AttributesMustNotBeChanged, SegmentAttributesMustNotBeChanged
from fot.rules.compare.preliminaryobjects import PreliminaryObjectsRule
from fot.geomutils.featurematcher import ApproximatePolygonMatcher, ApproximateLineMatcher, NearbyObjectsGeometryMatcher
from fot.rules.compare.piperule import PipeRule
from fot.rules.validate.singlelayer.duplicategeom import DuplicateLineStringLayerGeometries


rules_set = RulesSet('GeoDanmark Rules')

rules_set.add_rule_category('Preliminary')
for t in fot.featuretype.featuretypes:
    rules_set.add_rule(
        'Preliminary',
        PreliminaryObjectsRule(
            name=t.name + ' preliminary objects',
            feature_type=t,
            ispreliminaryfunction=lambda feature: feature['Geometri_status'] == u'Foreløbig',
            nearbymatcher=NearbyObjectsGeometryMatcher(distancewithin=5.0)
        )
    )

rules_set.add_rule_category('Building UUID')
rules_set.add_rule(
    'Building UUID',
    AttributesMustNotBeChanged(
        'Unchanged building UUID',
        feature_type=fot.featuretype.BYGNING,
        unchangedattributes=['bygning_id'],
        featurematcher=ApproximatePolygonMatcher(relativeintersectionarea=0.8), # TODO: Consider hausdorffdistance here!
        beforefilter='bygning_id IS NOT NULL'
    )
)

rules_set.add_rule(
    'Building UUID',
    UniqueAttributeValue(
        'Building UUID unique',
        feature_type=fot.featuretype.BYGNING,
        attributename='bygning_id',
        filter='bygning_id IS NOT NULL'
    )
)

rules_set.add_rule_category('Unchanged network attribs')

rules_set.add_rule(
    'Unchanged network attribs',
    SegmentAttributesMustNotBeChanged(
        'Unchanged road attribs',
        feature_type=fot.featuretype.VEJMIDTE_BRUDT,
        unchangedattributes=[
            'kommunekode',
            'vejkode',
            'vejmyndighed',
            'vejmidtetype',
            'vejklasse_brudt',
            'trafikart_brudt',
            'overflade_brudt',
            'plads_brudt',
            'fiktiv_brudt',
            'tilogfrakoer_brudt',
            'rundkoersel_brudt',
            'niveau'
        ],
        maxdist=10.0,
        segmentize=5.0
    )
)

rules_set.add_rule(
    'Unchanged network attribs',
    SegmentAttributesMustNotBeChanged(
        'Unchanged rail attribs',
        feature_type=fot.featuretype.JERNBANE_BRUDT,
        unchangedattributes=[
                'ejer_jernbane',
                'sportype',
        ],
        maxdist=10.0,
        segmentize=5.0,
    )
)

rules_set.add_rule_category('Stream centrelines')
pipe_no_touch_attributes=['Ejer_vandloebsmidte',
                                    'Fra_dato_fot',
                                    'Geometri_status',
                                    'Hovedforloeb',
                                    'Midtbredde_brudt',
                                    'ModerFOTID',
                                    'ModerFOTversion',
                                    'Netvaerk',
                                    'Objekt_status',
                                    'Startknude_Vandloebsmidte',
                                    'Slutknude_vandloebsmidte',
                                    'Synlig_Vandloebsmidte',
                                    'Vandloebstype']
rules_set.add_rule(
    'Stream centrelines',
    PipeRule(
        'Pipes unchanged',
        feature_type=fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        ispipefunction=lambda feature: feature['Vandloebstype'] == u'Rørlagt',
        isshortfunction=lambda geom: geom.length() < 50,
        unchangedattributes=pipe_no_touch_attributes
    )
)

rules_set.add_rule(
    'Stream centrelines',
    AttributeRule(
        'Stream.vandloebstype',
        fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        attributename='vandloebstype',
        isvalidfunction=lambda val: val in [u'Almindelig', u'Gennem sø', u'Rørlagt']
    )
)

rules_set.add_rule_category('Duplicate geometry')
rules_set.add_rule(
    'Duplicate geometry',
    DuplicateLineStringLayerGeometries(
        'Duplicate road centreline',
        fot.featuretype.VEJMIDTE_BRUDT,
        equalstolerance=0.1,
        segmentize=5.0
    )
)

rules_set.add_rule(
    'Duplicate geometry',
    DuplicateLineStringLayerGeometries(
        'Duplicate railroad centreline',
        fot.featuretype.JERNBANE_BRUDT,
        equalstolerance=0.1,
        segmentize=5.0
    )
)

rules_set.add_rule(
    'Duplicate geometry',
    DuplicateLineStringLayerGeometries(
        'Duplicate stream centreline',
        fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        equalstolerance=0.1,
        segmentize=5.0
    )
)
