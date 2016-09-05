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

from .datasetrule import DatasetRule
from ...geomutils.graph import GraphBuilder
from ...geomutils import tocoordinates
from qgis.core import QgsGeometry

class NetworkIslands(DatasetRule):

    def __init__(self, name, feature_types, minnodes, minlength, filters=None):
        """feature_types is list of feature types
           filters is list of filters for each feature type"""
        super(NetworkIslands, self).__init__(name)

        self.feature_types = list(feature_types)
        if filters:
            f = list(filters)
            assert len(f) == len(feature_types)
            self.filters = dict(zip(self.feature_types, f))
        else:
            self.filters = dict.fromkeys(self.feature_types)

        self.minnodes = int(minnodes)
        self.minsumcost = float(minlength) * 2.0  # Graph is directed so actual length is approx 0.5*sumcost

    def execute(self, repo, errorreporter, progressreporter):
        features = {}
        for ftype in self.feature_types:
            features[ftype] = set(repo.read(ftype, geometry=True, feature_filter=self.filters[ftype]))

        # flat list of all features from all feature_types
        all_features = [f for l in features.values() for f in l]

        # Graph
        builder = GraphBuilder(snap3d=True)
        graph = builder.build(all_features)

        # Loop over connected components and mark suspicious ones
        for component in graph.connected_components():
            if len(component.nodes) < self.minnodes or component.cost_sum() < self.minsumcost:
                geom = self._polygon_outline(component, builder)
                errorreporter.error(self.name, ','.join(map(str, self.feature_types)), "Network island", geom)


    def _convex_hull(self, graph, builder):
        points = [builder.node_to_point(n) for n in graph.nodes]
        multipoint = QgsGeometry.fromMultiPoint(points)
        return multipoint.convexHull().buffer(0.5, 8)

    def _polygon_outline(self, graph, builder):
        lines = [tocoordinates(e.feature.geometry()) for e in graph.edges]
        multiline = QgsGeometry.fromMultiPolyline(lines)
        return multiline.buffer(0.5, 8)



