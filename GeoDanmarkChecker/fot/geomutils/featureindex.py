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

from qgis.core import QgsFeature, QgsRectangle, QgsGeometry
from collections import defaultdict
from .pyqtree import Index
from . import togeometry

def bbox(f):
    """Returns the bbox [xmin,ymin,xmax,ymax] for a feature, a geometry, a bbox or a list of those"""
    if isinstance(f, QgsFeature) or isinstance(f, QgsGeometry):
        g = togeometry(f)
        rect = g.boundingBox()
        return [rect.xMinimum(), rect.yMinimum(), rect.xMaximum(), rect.yMaximum()]

    if isinstance(f, QgsRectangle):
        return [f.xMinimum(), f.yMinimum(), f.xMaximum(), f.yMaximum()]

    # Potentially a bbox or list of geoms or features
    if isinstance(f, (list, tuple)) and len(f) > 0:
        if len(f) == 4 and all([isinstance(n, (int, float)) for n in f]):
            # This is a bbox itself
            return f
        bboxes = [bbox(o) for o in f]
        xmins, ymins, xmaxs, ymaxs = zip(*bboxes)
        return [min(xmins), min(ymins), max(xmaxs), max(ymaxs)]


def bboxoverlaps(f1, f2):
    """Inputs are either QgsGeometry, QgsFeature or a bbox [xmin,ymin,xmax,ymax]"""
    b1 = bbox(f1)
    b2 = bbox(f2)
    return b1[0] < b2[2] and b1[2] > b2[0] and b1[1] < b2[3] and b1[3] > b2[1]

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

        self.features = list(features)
        self._updatespatialindex(features)
        self._updateattributeindexes(features)

    def _updatespatialindex(self, features):
        if self.usespatialindex:
            if not self.spatialindex:
                # Can be optimized wrgt bbox calculations being repeated later
                box = bbox(features)
                self.bbox = box if box else (0,0,0,0)
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
                    if f.fieldNameIndex(a) != -1:
                        value = f[a]
                        index[value].append(f)


