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
from fot.rules.dataset.singlelayer import UniqueAttributeValue
from fot.rules.dataset.singlelayer import AttributeRule
from fot.rules.dualdataset.compareattributes import AttributesMustNotBeChanged
from fot.rules.dualdataset.preliminaryobjects import PreliminaryObjectsRule
from fot.geomutils.featurematcher import ApproximatePolygonMatcher, ApproximateLineMatcher


rules_set = RulesSet('GeoDanmark Rules')

rules_set.add_rule_category('Preliminary')
rules_set.add_rule_category('Unique Attribute Value')

for t in fot.featuretype.featuretypes:
    rules_set.add_rule(
        'Preliminary',
        PreliminaryObjectsRule(
            t.name + ' preliminary objects',
            feature_type=t
        )
    )
    rules_set.add_rule(
        'Unique Attribute Value',
        UniqueAttributeValue(
            t.name + ' fot_id unique',
            feature_type=t,
            attributename='fot_id'
        )
    )

rules_set.add_rule_category('Vandloebstype')
rules_set.add_rule(
    'Vandloebstype',
    AttributeRule(
        'Stream.vandloebstype',
        fot.featuretype.VANDLOEBSMIDTE_BRUDT,
        attributename='vandloebstype',
        isvalidfunction=lambda val: val in [u'XXAlmindelig', u'Gennem sø', u'Rørlagt']
    )
)

rules_set.add_rule_category('Building UUID')
rules_set.add_rule(
    'Building UUID',
    AttributesMustNotBeChanged(
        'Unchanged building UUID',
        feature_type=fot.featuretype.BYGNING,
        unchangedattributes=['bygning_id'],
        featurematcher=ApproximatePolygonMatcher(relativeareadeviation=0.5),
        beforefilter='bygning_id IS NOT NULL'
    )
)

rules_set.add_rule_category('Unchanged road attribs')
vejmatchoptions = {'minimumintersectionlength': 1.0}
rules_set.add_rule(
    'Unchanged road attribs',
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
                'rundkoersel_brudt'],
        featurematcher=ApproximateLineMatcher(**vejmatchoptions),
        beforefilter='vejkode IS NOT NULL'
    )
)

rules_set = [rules_set, rules_set]