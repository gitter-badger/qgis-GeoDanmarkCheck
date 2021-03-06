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
from fot.rules.compare.networkbroken import NetworkBroken
from fot.repository import Repository
from fot.consolereporter import ConsoleReporter
from fot.progress import ProgressReporter
from fot.geomutils.featurematcher import ApproximatePolygonMatcher, ApproximateLineMatcher, NearbyObjectsGeometryMatcher
from fot.rules import RuleExecutor
from fot.reporter import Reporter
from fot.gmlimporter import gml_to_spatialite
import os

rules = []
# Get rules from rules.py
from rules import single_file_rules, update_rules
for cat, lst in single_file_rules.rules.iteritems():
    pass
    #if cat == 'Road network':
        #rules += lst
        #rules += [r for r in lst if r.name == 'Road network island' ]
    #rules += lst

for cat, lst in update_rules.rules.iteritems():
    if cat == 'Preliminary':
        rules += lst
    #rules += [r for r in lst if r.name == 'VEJMIDTE_BRUDT preliminary objects'] #isinstance(r, NetworkBroken)]
    #rules += lst
    pass

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
    outfile = os.path.join(testdata_dir, 'output.gpkg')
    if os.path.isfile(outfile):
        os.remove(outfile)
    # gml_file = os.path.join(testdata_dir, '607_Fredericia_fot5_fra_prod.gml')
    # gml_to_spatialite(gml_file)
    reporter = Reporter(outfile)
    #reporter = ConsoleReporter('log')
    progress = ProgressReporter()
    before = Repository(os.path.join(testdata_dir, '0787_Thisted_original.sqlite'))
    after = Repository(os.path.join(testdata_dir, '0787_Thisted_edited.sqlite'))
    exe = RuleExecutor(before, after)
    exe.execute(rules, reporter, progress)
    del exe
    del after
    del before
    del progress
    del reporter

print 'Done! Waiting 5secs'
import time
time.sleep(5)
print 'Really done :-)'
