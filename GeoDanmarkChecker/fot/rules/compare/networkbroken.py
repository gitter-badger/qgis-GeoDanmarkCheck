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

from ... import Repository
from ... import FeatureType
from ...geomutils.featurematcher import MatchFinder, ExactGeometryMatcher, NearbyObjectsGeometryMatcher
from ...geomutils.segmentmatcher import SegmentMatchFinder
from ...geomutils.graph import GraphBuilder, path_to_linestring
from .comparerule import CompareRule


class NetworkBroken(CompareRule):
    def __init__(self, name, feature_type, maxcostfactor, beforefilter=None, afterfilter=None):
        """
        :param name:
        :param feature_type:
        :param maxcostfactor: Raises an error if cost_after * maxcostfactor > cost_before
        :param beforefilter:
        :param afterfilter:
        """
        super(NetworkBroken, self).__init__(name, beforefilter, afterfilter)
        if not isinstance(feature_type, FeatureType):
            raise TypeError()
        self.featuretype = feature_type
        self.maxcostfactor = float(maxcostfactor)
        self.deletewithin = 1.0

    def execute(self, beforerepo, afterrepo, errorreporter, progressreporter):
        if not isinstance(beforerepo, Repository):
            raise TypeError()
        if not isinstance(afterrepo, Repository):
            raise TypeError()

        # Strategy is to find geometries which has been changes between "before" and "after"
        # Then for we find the end nodes of the changed geometries and try routing between them in
        # bot before and after scenario. We see trouble if route is a lot longer in the after situation

        beforefeats = beforerepo.read(self.featuretype, feature_filter=self.beforefilter)
        afterfeats = afterrepo.read(self.featuretype, feature_filter=self.afterfilter)

        # Features that appear to be changed
        changed_before_features = list(beforefeats)

        # Figure out which features from the before scenario havent got an exact match in the after scenario
        progressreporter.begintask(self.name, len(afterfeats))
        finder = MatchFinder(beforefeats)
        exactMatcher = ExactGeometryMatcher()
        for f in afterfeats:
            matches = finder.findmatching(f, exactMatcher)
            match_found = False
            for match in matches:
                match_found = True
                # Remove from changed if exists (Duplicate geometries forces us to use this check)
                if match.feature2 in changed_before_features:
                    changed_before_features.remove(match.feature2)
            progressreporter.completed_one()

        progressreporter.begintask(self.name, 3)
        # Find end points of the features which have been changed
        gbuilder = GraphBuilder(snap3d=True)
        changed_lines_graph = gbuilder.build(changed_before_features)
        progressreporter.completed_one()

        # graph of network after
        after_graph = gbuilder.build(afterfeats)
        progressreporter.completed_one()
        segment_matcher = SegmentMatchFinder(afterfeats, segmentize=5.0)
        # Now look at each set of connected lines
        for component in changed_lines_graph.connected_components():
            # graph is a connected set of lines which do not exist in afterfeats
            # Check, if removing/changing these features has mean significantly longer routes
            end_nodes = list(component.get_nodes_of_degree(1))  # end points of the graph
            for i in range(len(end_nodes) - 1):
                nodei = end_nodes[i]
                if not nodei in after_graph.nodes:
                    continue
                for j in range(i + 1, len(end_nodes)):
                    nodej = end_nodes[j]
                    if not nodej in after_graph.nodes:
                        continue
                    before_cost, before_path = component.shortest_path(nodei, nodej)
                    after_cost, after_path = after_graph.shortest_path(nodei, nodej)
                    if not after_path or after_cost > before_cost * self.maxcostfactor:
                        pathgeom = path_to_linestring(component, gbuilder, before_path)
                        # Delete path where there actually is a network component nearby in the after scenario
                        for segment_match in segment_matcher.findmatching(pathgeom, self.deletewithin):
                            matching_geom = segment_match.togeometry()
                            buffered = matching_geom.buffer(self.deletewithin, 8, 2, 1, 100.0)  # endCapStyle=2, joinStyle=1, mitreLimit=100.0)
                            pathgeom = pathgeom.difference(buffered)
                        errorreporter.error(self.name, self.featuretype, "Network possibly broken along this path", pathgeom)







        # Compare nonexact geometry matches
        # progressreporter.begintask(self.name, len(changed_after_features))
        # segmentmatchfinder = SegmentMatchFinder(changed_before_features, segmentize=self.segmentize)
        # for f in changed_after_features:
        #     for sm in segmentmatchfinder.findmatching(f, maxdistance=self.maxdist):
        #         f2 = sm.nearestfeature
        #         self._check(errorreporter, f2, f, sm.togeometry())
        #     progressreporter.completed_one()