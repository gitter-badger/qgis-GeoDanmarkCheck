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

from qgis.core import QgsFeature, QgsGeometry, QGis, QgsRectangle, QgsAbstractGeometryV2


def togeometry(f):
    """If input is feature returns the geometry of the feature.
    If input is geometry returns the input.
    Fails otherwise"""
    if isinstance(f, QgsGeometry):
        return f
    elif isinstance(f, QgsFeature):
        return f.geometry()
    elif isinstance(f, QgsAbstractGeometryV2):
        return QgsGeometry(f)
    elif f is None:
        return None
    else:
        raise TypeError("Type was not QgsGeometry or QgsFeature. Type was {0}".format(str(type(f))))


def shortestline(f1, f2):
    """Returns the shortest line between two geometries or features"""
    g1 = togeometry(f1)
    g2 = togeometry(f2)
    return g1.shortestLine(g2)

def geometryequal(f1, f2, tolerance = 0.01):
    """Compares geometries coordinate by coordinate using specified tolerance"""
    g1 = togeometry(f1)
    g2 = togeometry(f2)
    wkb1 = g1.wkbType()
    wkb2 = g2.wkbType()
    if wkb1 != wkb2:
        return False
    # QgsGeometry.compare only supports lines, polygons and multipolygons
    if wkb1 in (QGis.WKBPoint, QGis.WKBPoint25D):
        return g1.distance(g2) < tolerance
    if wkb1 in (QGis.WKBPolygon, QGis.WKBPolygon25D):
        return QgsGeometry.compare(g1.asPolygon(), g2.asPolygon(), tolerance)
    if wkb1 in (QGis.WKBLineString, QGis.WKBLineString25D):
        return QgsGeometry.compare(g1.asPolyline(), g2.asPolyline(), tolerance)

def extractassingle(f):
    """
    :param self:
    :param geom:
    :return: a list of single geoms
    """
    geom = togeometry(f)
    multiGeom = QgsGeometry()
    geometries = []
    if geom.type() == QGis.Point:
        if geom.isMultipart():
            multiGeom = geom.asMultiPoint()
            for i in multiGeom:
                geometries.append(QgsGeometry().fromPoint(i))
        else:
            geometries.append(geom)
    elif geom.type() == QGis.Line:
        if geom.isMultipart():
            multiGeom = geom.asMultiPolyline()
            for i in multiGeom:
                geometries.append(QgsGeometry().fromPolyline(i))
        else:
            geometries.append(geom)
    elif geom.type() == QGis.Polygon:
        if geom.isMultipart():
            multiGeom = geom.asMultiPolygon()
            for i in multiGeom:
                geometries.append(QgsGeometry().fromPolygon(i))
        else:
            geometries.append(geom)
    elif geom.type() == QGis.UnknownGeometry:
        if geom.isMultipart():
            # Geometrycollection
            geomColl = geom.asGeometryCollection()
            for g in geomColl:
                copiedgeom = QgsGeometry(g)
                for g in extractassingle(copiedgeom):
                    geometries.append(g)
    return geometries

def extractlinestrings(f):
    """If input is a geometrycollection returns a linestring or multilinestring built from the the input"""
    g = togeometry(f)

    # Short circuit
    if g.type() == QGis.Line:
        return g

    singlegeoms = extractassingle(f)
    lines = [g for g in singlegeoms if g.type() == QGis.Line ]
    if lines:
        if len(lines) > 1:
            return QgsGeometry.fromMultiPolyline([g.asPolyline() for g in lines])
        else:
            return lines[0]
    return None

def tocoordinates(feature):
    g = togeometry(feature)
    type = QGis.flatType((g.wkbType()))
    if type == QGis.WKBPoint:
        return g.asPoint()
    if type == QGis.WKBLineString:
        return g.asPolyline()
    if type == QGis.WKBPolygon:
        return g.asPolygon()
    raise TypeError("Unknown geometry type: " + str(type))

def toflatcoordinates(feature):
    """Returns a flat list of all coordinates in the geometry"""
    g = togeometry(feature)
    type = QGis.flatType((g.wkbType()))
    if type == QGis.WKBPoint:
        return [g.asPoint()]
    if type == QGis.WKBLineString:
        return g.asPolyline()
    if type == QGis.WKBPolygon:
        return [coord for ring in g.asPolygon() for coord in ring]
    raise TypeError("Unknown geometry type: " + str(type))

def tocoordinates3d(feature):
    """
    Retrieves the sequence of geometries, rings and 3D vertices.
    Note: Doesnt use the same return structure as tocoordinates()
    :param feature:
    :return:
    """
    g = togeometry(feature)
    gv2 = g.geometry()  # V2 geometry
    return gv2.coordinateSequence()








