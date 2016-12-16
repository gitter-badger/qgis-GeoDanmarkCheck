# coding=utf-8

import unittest

from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from ..fot.geomutils.segmentmatcher import SegmentMatchFinder


class TestInit(unittest.TestCase):
    a = QgsFeature()
    a.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 0, 10 0)"))
    b = QgsFeature()
    features = [a, b]

    def test_should_not_match_same_endpoints_and_large_diff_length(self):
        self.b.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 0, 0 100, 10 100, 10 0)"))

        smf = SegmentMatchFinder(self.features, segmentize=20)
        matches = len(smf.findmatching(self.a, maxdistance=0.1))

        self.assertEqual(matches, 0)

    def test_should_not_match_intersecting_and_large_diff_length(self):
        self.b.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 -100, 0 100, 10 100, 10 -100)"))

        smf = SegmentMatchFinder(self.features, segmentize=20)
        matches = len(smf.findmatching(self.a, maxdistance=0.1))

        self.assertEqual(matches, 0)

if __name__ == '__main__':
    unittest.main()