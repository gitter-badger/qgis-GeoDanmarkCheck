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
from collections import defaultdict


class RulesSet(object):
    """ Contains a rules set, a dict of 'category_name' : [list of rules] """

    def __init__(self, name):
        self.name = name
        self.rules = defaultdict(list)

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
from fot.rules.validate.networkislands import NetworkIslands
from fot.rules.compare.networkbroken import NetworkBroken


single_file_rules = RulesSet('GeoDanmark Rules')
update_rules = RulesSet('GeoDanmark Update Rules')

"""
* ***************************************************
*   Rules concerning only one version of the data
* ***************************************************
"""

single_file_rules.add_rule(
    'Building UUID',
    UniqueAttributeValue(
        'Building UUID unique',
        feature_type=fot.featuretype.BYGNING,
        attributename='Bygning_ID',
        filter='Bygning_ID IS NOT NULL'
    )
)

single_file_rules.add_rule(
    'Stream centrelines',
    AttributeRule(
        'Stream.vandloebstype',
        fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        attributename='Vandloebstype',
        isvalidfunction=lambda val: val in [u'Almindelig', u'Gennem sø', u'Rørlagt']
    )
)

single_file_rules.add_rule(
    'Duplicate geometry',
    DuplicateLineStringLayerGeometries(
        'Duplicate road centreline',
        fot.featuretype.VEJMIDTE_BRUDT,
        equalstolerance=0.1,
        segmentize=5.0
    )
)

single_file_rules.add_rule(
    'Duplicate geometry',
    DuplicateLineStringLayerGeometries(
        'Duplicate railroad centreline',
        fot.featuretype.JERNBANE_BRUDT,
        equalstolerance=0.1,
        segmentize=5.0
    )
)

single_file_rules.add_rule(
    'Duplicate geometry',
    DuplicateLineStringLayerGeometries(
        'Duplicate stream centreline',
        fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        equalstolerance=0.1,
        segmentize=5.0
    )
)

single_file_rules.add_rule(
    'Road network',
    NetworkIslands(
        'Road network island',
        [fot.featuretype.VEJMIDTE_BRUDT],
        minlength=500,
        minnodes=10
    )
)

"""
* ***************************************************
*   Rules comparing two versions of the data
* ***************************************************
"""
for t in fot.featuretype.featuretypes:
    update_rules.add_rule(
        'Preliminary',
        PreliminaryObjectsRule(
            name=t.name + ' preliminary objects',
            feature_type=t,
            ispreliminaryfunction=lambda feature: feature['Geometri_status'] == u'Foreløbig',
            nearbymatcher=NearbyObjectsGeometryMatcher(distancewithin=5.0)
        )
    )

update_rules.add_rule(
    'Building UUID',
    AttributesMustNotBeChanged(
        'Unchanged building UUID',
        feature_type=fot.featuretype.BYGNING,
        unchangedattributes=['Bygning_ID'],
        featurematcher=ApproximatePolygonMatcher(relativeintersectionarea=0.8), # TODO: Consider hausdorffdistance here!
        beforefilter='Bygning_ID IS NOT NULL'
    )
)

update_rules.add_rule(
    'Unchanged network attribs',
    SegmentAttributesMustNotBeChanged(
        'Unchanged road attribs',
        feature_type=fot.featuretype.VEJMIDTE_BRUDT,
        unchangedattributes=[
            'Kommunekode',
            'Vejkode',
            'Vejmyndighed',
            'Vejmidtetype',
            'Vejklasse_BRUDT',
            'Trafikart_BRUDT',
            'Overflade_BRUDT',
            'Plads_BRUDT',
            'Fiktiv_BRUDT',
            'Tilogfrakoer_BRUDT',
            'Rundkoersel_BRUDT',
            #'Niveau_BRUDT'
        ],
        maxdist=10.0,
        segmentize=5.0
    )
)

update_rules.add_rule(
    'Unchanged network attribs',
    SegmentAttributesMustNotBeChanged(
        'Unchanged rail attribs',
        feature_type=fot.featuretype.JERNBANE_BRUDT,
        unchangedattributes=[
                'Ejer_Jernbane',
                'Sportype',
        ],
        maxdist=10.0,
        segmentize=5.0,
    )
)

pipe_no_touch_attributes=[
    'Ejer_Vandloebsmidte',
    'Fra_dato_FOT',
    'Geometri_status',
    'Hovedforloeb',
    'Midtebredde_BRUDT',
    'ModerFOTID',
    'ModerFOTversion',
    'Netvaerk',
    'Objekt_status',
    'Slutknude_Vandloebsmidte',
    'Startknude_Vandloebsmidte',
    'Synlig_Vandloebsmidte_BRUDT',
    'Til_dato_FOT',
    'Vandloebstype'
]
update_rules.add_rule(
    'Stream centrelines',
    PipeRule(
        'Pipes unchanged',
        feature_type=fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        ispipefunction=lambda feature: feature['Vandloebstype'] == u'Rørlagt',
        isshortfunction=lambda geom: geom.length() < 50,
        unchangedattributes=pipe_no_touch_attributes
    )
)

update_rules.add_rule(
    'Stream centrelines',
    NetworkBroken(
        'Stream network broken',
        feature_type=fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        maxcostfactor=2.0   # Error if route has become more than 2 times longer
    )

)

update_rules.add_rule(
    'Road centrelines',
    NetworkBroken(
        'Road network broken',
        feature_type=fot.featuretype.VEJMIDTE_BRUDT,
        maxcostfactor=2.0   # Error if route has become more than 2 times longer
    )

)

rules_set = [single_file_rules, update_rules]