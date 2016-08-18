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
from fot.rules.compare.compareattributes import AttributesMustNotBeChanged
from fot.rules.compare.preliminaryobjects import PreliminaryObjectsRule
from fot.geomutils.featurematcher import ApproximatePolygonMatcher, ApproximateLineMatcher, NearbyObjectsGeometryMatcher
from fot.rules.compare.piperule import PipeRule


rules_set = RulesSet('GeoDanmark Rules')

rules_set.add_rule_category('Preliminary')
rules_set.add_rule_category('Unique Attribute Value')

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

# TODO: use segmentwise matching here instead of approximatelinematcher which tries to match entire geometry
# Maybe start with a hausdorff distance to catch the cases where nothing changed much
vejmatchoptions = {'minimumintersectionlength': 3, 'relativeintersectionlength':0.20, 'linebuffer': 0.2}  # Vi gider ikke høre om stykker kortere end 1 meter
rules_set.add_rule(
    'Unchanged network attribs',
    AttributesMustNotBeChanged(
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
                #'niveau'
        ],
        featurematcher=ApproximateLineMatcher(**vejmatchoptions),
        beforefilter='vejkode IS NOT NULL'
    )
)

railmatchoptions = {'minimumintersectionlength': 3, 'relativeintersectionlength':0.20, 'linebuffer': 0.2}  # Vi gider ikke høre om stykker kortere end 1 meter
rules_set.add_rule(
    'Unchanged network attribs',
    AttributesMustNotBeChanged(
        'Unchanged rail attribs',
        feature_type=fot.featuretype.JERNBANE_BRUDT,
        unchangedattributes=[
                'ejer_jernbane',
                'sportype',
        ],
        featurematcher=ApproximateLineMatcher(**vejmatchoptions),
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
