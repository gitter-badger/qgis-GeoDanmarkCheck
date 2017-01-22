# coding=utf-8

import unittest

from qgis.core import QgsGeometry
from qgis.core import QgsFeature
from ...fot.geomutils.segmentmatcher import SegmentMatchFinder


class TestIssue43(unittest.TestCase):
    a = QgsFeature()
    b = QgsFeature()
    features = [a, b]

    def test_should_not_match_perpendicular_segments(self):
        self.a.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 0, 5 105)"))
        self.b.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 50, 105 55)"))

        smf = SegmentMatchFinder(self.features, segmentize=5)
        matches = smf.findmatching(self.b, maxdistance=10)

        self.assertEqual(len(matches), 0)

    def test_should_not_match_perpendicular_segments2(self):
        self.a.setGeometry(QgsGeometry.fromWkt(
            "LineStringZ (569592.43999999994412065 6290849.37000000011175871 3, 569591.93000000005122274 6290842.05999999959021807 3, 569587.55000000004656613 6290824.67999999970197678 3, 569577.81999999994877726 6290786.66000000014901161 3.60000000000000009, 569572.72999999998137355 6290765.58000000007450581 3.60000000000000009, 569564.66000000003259629 6290732.62999999988824129 3.79999999999999982, 569557.71999999997206032 6290703.67999999970197678 3.85000000000000009, 569554.53000000002793968 6290691.41999999992549419 3.97999999999999998, 569550.83999999996740371 6290675.74000000022351742 3.85000000000000009, 569541.0400000000372529 6290634.58000000007450581 4.5)"
        ))
        self.b.setGeometry(QgsGeometry.fromWkt("LineStringZ (569604.7900000000372529 6290683.5 4.37999999999999989, 569590.43999999994412065 6290686.29999999981373549 4.30999999999999961, 569570.86999999999534339 6290689.01999999955296516 4.28000000000000025, 569554.53000000002793968 6290691.41999999992549419 3.97999999999999998)"))

        smf = SegmentMatchFinder(self.features, segmentize=5)
        matches = len(smf.findmatching(self.b, maxdistance=10))

        self.assertEqual(matches, 0)

    def test_should_match_parallel_segments(self):
        self.a.setGeometry(QgsGeometry.fromWkt("LINESTRING(0 0, 100 20)"))
        self.b.setGeometry(QgsGeometry.fromWkt("LINESTRING(5 0, 105 20)"))

        smf = SegmentMatchFinder(self.features, segmentize=5)
        matches = len(smf.findmatching(self.a, maxdistance=10))

        self.assertEqual(matches, 1)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestIssue43)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
