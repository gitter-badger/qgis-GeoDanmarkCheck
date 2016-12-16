# coding=utf-8

import unittest

from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from ..fot.geomutils.segmentmatcher import SegmentMatchFinder


class TestInit(unittest.TestCase):
    def test_SegmentMatchFinder(self):

        a = QgsFeature()
        b = QgsFeature()
        a.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 0, 10 0)"))
        b.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 0, 0 100, 10 100, 10 0)"))
        features = [a, b]

        smf = SegmentMatchFinder(features, segmentize=20)

        sms = smf.findmatching(a, maxdistance=0.1)

        self.assertEqual(len(sms), 0)

if __name__ == '__main__':
    unittest.main()