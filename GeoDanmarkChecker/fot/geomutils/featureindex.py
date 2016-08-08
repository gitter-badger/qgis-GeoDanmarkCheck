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

from qgis.core import QgsFeature
from collections import defaultdict
from . import togeometry, bbox, bboxoverlaps
from .pyqtree import Index

class FeatureIndex():
    # http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html#using-spatial-index

    def __init__(self, features, usespatialindex=False, indexedattributes=[]):
        # validate wrt featuretype?
        # insert all features into index
        self.features = features
        self.spatialindex = None
        self.indexedattributes = set(indexedattributes)
        self.attributeindexes = {}
        self.usespatialindex = usespatialindex
        self.bbox = None
        self.insert(features)

    def geometryintersects(self, geom_or_feature):
        box = bbox(geom_or_feature)
        return self.spatialindex.intersect(box)

    def attributeequals(self, attributename, value):
        index = self.attributeindexes[attributename]
        return index[value]

    def insert(self, features):
        if isinstance(features, QgsFeature):
            features = [features]
        if not all(isinstance(f, QgsFeature) for f in features):
            raise TypeError("All features must be of type QgsFeature")

        self.features += [f for f in features]
        self._updatespatialindex(features)
        self._updateattributeindexes(features)

    def _updatespatialindex(self, features):
        if self.usespatialindex:
            if not self.spatialindex:
                # Can be optimized wrgt bbox calculations being repeated later
                self.bbox = bbox(features)
                # QgsSpatialIndex only returns FID of intersecting features. When we dont have FIDs this is not good
                self.spatialindex = Index(bbox=self.bbox)
            else:
                # Before updating we need to check if the new geoms are within the index bbox
                # If they are not - we have to rebuild
                raise NotImplementedError("Updating has not been implemented yet")
            for f in self.features:
                self.spatialindex.insert(f, bbox(f))

    def _updateattributeindexes(self, features):
        if self.indexedattributes:
            for a in self.indexedattributes:
                if not a in self.attributeindexes:
                    self.attributeindexes[a] = defaultdict(list)
                index = self.attributeindexes[a]
                for f in features:
                    value = f[a]
                    index[value].append(f)


