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

from qgis.core import QgsPoint, QgsGeometry, QGis
from math import sqrt, ceil
from . import togeometry, toflatcoordinates, tocoordinates

# TODO: Write tests. Use https://github.com/postgis/postgis/blob/svn-trunk/regress/hausdorff.sql

def discretehausdorffdistance(g1,g2):
    """Calculates the discrete hausdorff distance between two geometries.
        Discrete meaning that it only considers vertices as origins.
        When the segment length goes towards zero this measure goes toward the non-discrete hausdorf distance
        """
    g1 = togeometry(g1)
    g2 = togeometry(g2)
    odist1 = orienteddistance(g1, g2)
    odist2 = orienteddistance(g2, g1)
    if odist1[0] >= odist2[0]:
        return odist1
    else:
        return odist2

def orienteddistance(g1, g2):
    """Calculates the maximum distance one must travel if you need to go from a vertex in g1 to the nearest point in g2"""
    coords1 = toflatcoordinates(g1)
    maxsqrddist = -1
    frompoint = None
    topoint = None
    for c1 in coords1:
        sqrddist, closestsegmentpoint, indexofclosestvertexafter = g2.closestSegmentWithContext(c1)
        if sqrddist < 0:
            raise Exception('closestSegmentWithContext failed')
        if sqrddist > maxsqrddist:
            maxsqrddist = sqrddist
            frompoint = QgsPoint(c1)
            topoint = closestsegmentpoint
    return sqrt(maxsqrddist), frompoint, topoint


def densify(geometry, maxsegmentlength):
    """Densifies geometry vertices, so no segment is longer than maxsegmentlength
    Only implemented for linestring at the time being"""
    g = togeometry(geometry)
    type = QGis.flatType((g.wkbType()))
    if not type == QGis.WKBLineString:
        raise NotImplementedError("Densify is only implemented for LineStrings at the moment")
    input_coords = tocoordinates(g)
    output_coords = []
    maxsegmentlength = float(maxsegmentlength)
    for ix in xrange(len(input_coords) - 1):
        p0 = input_coords[ix]
        p1 = input_coords[ix + 1]
        output_coords.append(QgsPoint(p0))
        # Avoid calculating these values at the cost of performace.
        in_segment = QgsGeometry.fromPolyline([p0, p1])
        in_segment_length = in_segment.length()
        segcount = int(ceil(in_segment_length / maxsegmentlength))
        if segcount > 1:
            new_seg_length = float(in_segment_length) / segcount
            for i in xrange(1,segcount):
                new_p = in_segment.interpolate(new_seg_length * i).asPoint()
                output_coords.append(new_p)
    # Add last coord
    output_coords.append(input_coords[-1])
    return QgsGeometry.fromPolyline(output_coords)


def line_locate_point(geometry, point):
    coords = tocoordinates(geometry)

    assert QGis.flatType((geometry.wkbType())) == QGis.WKBLineString, 'Expected a LineString'
    assert len(point) == 2, 'Expected a point'

    sqrddist, closestsegmentpoint, indexofclosestvertexafter = geometry.closestSegmentWithContext(point)

    sum_length = 0

    # Length of segments before the segment, where the point is located
    for ix in range(1, indexofclosestvertexafter):
        p0 = coords[ix - 1]
        p1 = coords[ix]
        segment = QgsGeometry.fromPolyline([p0, p1])
        sum_length += segment.length()

    # Part of segment where the points is located
    p0 = coords[indexofclosestvertexafter - 1]
    segment = QgsGeometry.fromPolyline([p0, closestsegmentpoint])
    sum_length += segment.length()

    return sum_length
