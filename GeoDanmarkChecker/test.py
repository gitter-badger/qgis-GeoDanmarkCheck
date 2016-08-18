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
from fot.rules.validate.singlelayer import UniqueAttributeValue
from fot.rules.validate.singlelayer import AttributeRule
from fot.rules.compare.compareattributes import AttributesMustNotBeChanged, SegmentAttributesMustNotBeChanged
from fot.rules.compare.preliminaryobjects import PreliminaryObjectsRule
from fot.rules.compare.piperule import PipeRule
from fot.repository import Repository
from fot.consolereporter import ConsoleReporter
from fot.progress import ProgressReporter
from fot.geomutils.featurematcher import ApproximatePolygonMatcher, ApproximateLineMatcher, NearbyObjectsGeometryMatcher
from fot.rules import RuleExecutor
from fot.reporter import Reporter
from fot.gmlimporter import gml_to_spatialite
import os

rules = []
if False:

    # Rules applying to ALL featuretypes
    for t in fot.featuretype.featuretypes:
        rules.append(
            PreliminaryObjectsRule(
                name=t.name + ' preliminary objects',
                feature_type=t,
                ispreliminaryfunction=lambda feature: feature['Geometri_status'] == u'Foreløbig',
                nearbymatcher=NearbyObjectsGeometryMatcher(distancewithin=5.0)
            )
        )
if False:
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
    pipe_no_touch_attributes = ['Ejer_vandloebsmidte',
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
    rules.append(
        PipeRule(
            'Pipes unchanged',
            feature_type=fot.featuretype.VANDLOEBSMIDTE_BRUDT,
            ispipefunction=lambda feature: feature['Vandloebstype'] == u'Rørlagt',
            isshortfunction=lambda geom: geom.length() < 50,
            unchangedattributes=pipe_no_touch_attributes
        )
    )
    rules.append(
        PreliminaryObjectsRule(
            name='Vandloebsmidte preliminary objects',
            feature_type=fot.featuretype.VANDLOEBSMIDTE_BRUDT,
            ispreliminaryfunction=lambda feature: feature['Geometri_status'] == u'Foreløbig',
            nearbymatcher=NearbyObjectsGeometryMatcher(distancewithin=5.0)
        )
    )

rules.append(
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
            # 'niveau'
        ],
        maxdist=10.0,
        segmentize=5.0
    )
)

rules.append(
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
