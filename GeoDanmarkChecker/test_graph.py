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
from fot.repository import Repository
import os
from fot.geomutils.graph import *

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
    repo = Repository(os.path.join(testdata_dir, 'producentfil_med_fejl.gml'))
    roads = repo.read(fot.featuretype.VEJMIDTE_BRUDT)
    print('Building graph on {0} features'.format(len(roads)))
    builder = GraphBuilder(snap3d=True)
    g = builder.build(roads)
    print('Got graph with {0} nodes and {1} edges. Sum cost {2}'.format(len(g.nodes), len(g.edges), g.cost_sum()))
    nodes = list(g.nodes.keys())
    n0 = nodes[0]
    n1 = nodes[100]
    print('Routing from {0} to {1}'.format(n0,n1))
    cost, path = g.shortest_path(n0, n1)
    print('Path cost: {0}. Path: {1}'.format(cost, path))

    feats = []
    for i in range(len(path) - 1):
        feats.append(g.get_edge(path[i], path[i+1]).feature)
    print('Feats: {0}'.format(feats))

    print('Getting all nodes of dimension 2')
    print (list(g.get_nodes_of_degree(2)))

    print('Getting connected components as graphs')
    components = list(g.connected_components())
    for subgraph in components:
        print('Got graph with {0} nodes and {1} edges. Sum cost {2}'.format(len(subgraph.nodes), len(subgraph.edges), subgraph.cost_sum()))

    print('Routing from one sub graph to another. No route should be found')
    cost, path = g.shortest_path(components[0].nodes.keys()[0], components[1].nodes.keys()[0])
    print('Path cost: {0}. Path: {1}'.format(cost, path))


