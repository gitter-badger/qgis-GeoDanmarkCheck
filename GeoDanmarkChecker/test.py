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

import fot.featuretype
import fot.qgisapp
from fot.rules.dataset.singlelayer import UniqueAttributeValue
from fot.rules.dataset.singlelayer import AttributeRule
from fot.rules.dualdataset.compareattributes import AttributesMustNotBeChanged
from fot.rules.dualdataset.preliminaryobjects import PreliminaryObjectsRule
from fot.repository import Repository
from fot.consolereporter import ConsoleReporter
from fot.progress import ProgressReporter
from fot.geomutils.featurematcher import ApproximatePolygonMatcher, ApproximateLineMatcher
from fot.rules import RuleExecutor
from fot.reporter import Reporter
from fot.gmlimporter import gml_to_spatialite
import os

rules = []
if True:

    # Rules applying to ALL featuretypes
    for t in fot.featuretype.featuretypes:
        rules.append(
            PreliminaryObjectsRule(
                t.name + ' preliminary objects',
                feature_type=t
            )
        )
        # rules.append(
        #     UniqueAttributeValue(
        #         t.name + ' fot_id unique',
        #         feature_type=t,
        #         attributename='FOT_ID',
        #         filter='FOT_ID IS NOT NULL'
        #     )
        # )
    # End for all t

    rules.append(
        AttributeRule(
            'Stream.vandloebstype',
            fot.featuretype.VANDLOEBSMIDTE_BRUDT,
            attributename='vandloebstype',
            isvalidfunction=lambda val: val in [u'Almindelig', u'Gennem sø', u'Rørlagt']
            # validvalues=[u'XXAlmindelig', u'Gennem sø', u'Rørlagt'] #[u'Almindelig', u'Gennem sø', u'Rørlagt']
        )
    )

    rules.append(
        UniqueAttributeValue(
            'Building UUID unique',
            feature_type=fot.featuretype.BYGNING,
            attributename='bygning_id',
            filter='bygning_id IS NOT NULL'
        )
    )

    rules.append(
        AttributesMustNotBeChanged(
            'Unchanged building UUID',
            feature_type=fot.featuretype.BYGNING,
            unchangedattributes=['bygning_id'],
            featurematcher=ApproximatePolygonMatcher(relativeareadeviation=0.5),
            beforefilter='bygning_id IS NOT NULL'
        )
    )

vejmatchoptions = {'minimumintersectionlength': 3, 'relativelengthdeviation':0.20, 'linebuffer': 0.2}  # Vi gider ikke høre om stykker kortere end 1 meter
rules.append(
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

railmatchoptions = {'minimumintersectionlength': 3, 'relativelengthdeviation':0.20, 'linebuffer': 0.2}  # Vi gider ikke høre om stykker kortere end 1 meter
rules.append(
    AttributesMustNotBeChanged(
        'Unchanged rail attribs',
        feature_type=fot.featuretype.JERNBANE_BRUDT,
        unchangedattributes=[
                'ejer_jernbane',
                'sportype',
        ],
        featurematcher=ApproximateLineMatcher(**vejmatchoptions),
        #beforefilter='vejkode IS NOT NULL'
    )
)

with fot.qgisapp.QgisStandaloneApp(True) as app:
    print "App initialised"
    # Get current dir, get parent, and join with 'testdata'
    testdata_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.pardir
        ),
        'testdata'
    )
    outfile = os.path.join(testdata_dir, 'output.sqlite')
    if os.path.isfile(outfile):
        os.remove(outfile)
    # gml_file = os.path.join(testdata_dir, '607_Fredericia_fot5_fra_prod.gml')
    # gml_to_spatialite(gml_file)
    reporter = Reporter(outfile)
    #reporter = ConsoleReporter('log')
    progress = ProgressReporter()
    before = Repository(os.path.join(testdata_dir, 'original_fil.gml'))
    after = Repository(os.path.join(testdata_dir, 'producentfil_med_fejl.gml'))
    exe = RuleExecutor(before, after)
    exe.execute(rules, reporter, progress)

    # from fot.geomutils import FeatureIndex
    # feats = after.read(fot.featuretype.BYGNING)
    # ix = FeatureIndex(feats, usespatialindex=True)
    # result = ix.geometryintersects( feats[0] )
    # print result

