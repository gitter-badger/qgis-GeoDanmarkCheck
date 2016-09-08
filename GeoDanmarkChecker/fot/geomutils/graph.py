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

import heapq

from . import tocoordinates, tocoordinates3d
from collections import defaultdict
from qgis.core import QgsPoint, QgsGeometry


class Node2D(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def equals2D(self, other):
        return self.x == other.x and self.y == other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return '({0}, {1})'.format(self.x, self.y)

class Node3D(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def equals2D(self, other):
        return self.x == other.x and self.y == other.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __repr__(self):
        return '({0}, {1}, {2})'.format(self.x, self.y, self.z)

class Edge(object):
    def __init__(self, feature, cost, directed=False, reverse=False, ):
        self.feature = feature
        self.directed = directed
        self.reverse = reverse
        self.cost = cost

class Graph(object):
    def __init__(self):
        self.nodes = defaultdict(dict)
        self.edges = set()

    def add_edge(self, from_node, to_node, edge):
        self.nodes[from_node][to_node] = edge
        self.edges.add(edge)

    def get_edges_from_node(self, from_node):
        return self.nodes[from_node]

    def get_edge(self, from_node, to_node):
        return self.nodes[from_node][to_node]

    def get_nodes_of_degree(self, degree):
        for fromnode, connections in self.nodes.iteritems():
            if len(connections) == degree:
                yield fromnode

    def cost_sum(self):
        """The total sum of costs in this graph"""
        return sum([e.cost for e in self.edges])

    def shortest_path(self, fromnode, tonode=None):
        def flatten(L):  # Flatten linked list of form [0,[1,[2,[]]]]
            while len(L) > 0:
                yield L[0]
                L = L[1]

        q = [(0, fromnode, ())]  # Heap of (cost, path_head, path_rest).
        visited = set()  # Visited vertices.
        while True:
            try:
                (cost, v1, path) = heapq.heappop(q)
            except IndexError as e:
                # Ran out of nodes before reaching tonode -> No route found
                return None, None
            if v1 not in visited:
                visited.add(v1)
                if v1 == tonode:
                    return cost, list(flatten(path))[::-1] + [v1]
                path = (v1, path)
                for (v2, edge) in self.nodes[v1].iteritems():
                    cost2 = edge.cost
                    if v2 not in visited:
                        heapq.heappush(q, (cost + cost2, v2, path))

    def connected_components(self):
        seen = set()
        def component(node):
            nodes = set([node])
            subg = Graph()
            while nodes:
                node = nodes.pop()
                seen.add(node)
                for to_node, edge in self.nodes[node].iteritems():
                    subg.add_edge(node, to_node, edge)
                nodes |= set(self.nodes[node]) - seen
            return subg

        for node in self.nodes:
            if node not in seen:
                yield component(node)


class GraphBuilder(object):
    def __init__(self, accuracy = 0.01, snap3d = False, costfunction= lambda f: f.geometry().length()):
        """accuracy: Coordinates are rounded to this accuracy before being compared
           snap3d: Use 3D snap as opposed to 2D snap """
        self.accuracy = accuracy
        self.scale = 1.0 / accuracy
        self.snap3d = snap3d
        self.costfunction = costfunction

    def build(self, features):
        g = Graph()

        for f in features:
            e = self.get_edge(f)
            fromnode, tonode = self._get_nodes(e)
            if not e.directed:
                g.add_edge(fromnode, tonode, e)
                g.add_edge(tonode, fromnode, e)
            elif not e.reverse:
                g.add_edge(fromnode, tonode, e)
            else:
                g.add_edge(tonode, fromnode, e)
        return g

    def get_edge(self, feature):
        cost = self.costfunction(feature)
        e = Edge(feature, cost)
        return e

    def _get_nodes(self, edge):
        coords = tocoordinates3d(edge.feature)
        p0 = coords[0][0][0]
        p1 = coords[0][0][-1]
        if edge.reverse:
            tmp = p0
            p0 = p1
            p1 = tmp
        n0 = self.point_to_node(p0)
        n1 = self.point_to_node(p1)
        return n0, n1

    def point_to_node(self, point):
        """Returns the node corresponding to a point"""
        x = int(point.x() * self.scale)
        y = int(point.y() * self.scale)
        if not self.snap3d:
            return Node2D(x,y)
        else:
            z = int(point.z() * self.scale)
            return Node3D(x,y,z)

    def node_to_point(self, node):
        x = node.x / self.scale
        y = node.y / self.scale
        return QgsPoint(x,y)


def path_to_linestring(graph, builder, path):
    def get_edge_coordinates_from_node(start_node, builder, edge):
        coords = tocoordinates(edge.feature)
        node_point = builder.node_to_point(start_node)
        if node_point.sqrDist(coords[0]) > builder.scale:
            coords.reverse()
        return coords

    e = graph.get_edge(path[0], path[1])
    coords = get_edge_coordinates_from_node(path[0], builder, e)
    for i in range(1, len(path) - 1):
        e = graph.get_edge(path[i], path[i+1])
        coords += get_edge_coordinates_from_node(path[i], builder, e)
    return QgsGeometry.fromPolyline(coords)


if __name__ == '__main__':
    graph = {'a': {'w': 14, 'x': 7, 'y': 9},
            'b': {'w': 9, 'z': 6},
            'w': {'a': 14, 'b': 9, 'y': 2},
            'x': {'a': 7, 'y': 10, 'z': 15},
            'y': {'a': 9, 'w': 2, 'x': 10, 'z': 11},
            'z': {'b': 6, 'x': 15, 'y': 11}}

    g = Graph()
    for from_node, connections in graph.iteritems():
        for to_node, cost in connections.iteritems():
            e = Edge(None, cost)
            g.add_edge(from_node, to_node, e)
    print(g.shortest_path('a','b'))

    """
    Result:
        (20, ['a', 'y', 'w', 'b'])
        """



