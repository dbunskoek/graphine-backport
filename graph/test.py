#! /usr/bin/env python3

"""
test.py

Written by Geremy Condra and Patrick Laban

Licensed under GPLv3

Released 17 Feb 2009

This contains all the test data for Graphine.
"""

# Copyright (C) 2009 Geremy Condra and Patrick Laban
#
# This file is part of Graphine.
#
# Graphine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Graphine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Graphine.  If not, see <http://www.gnu.org/licenses/>.


import unittest
import timeit
import copy

from base import Graph, Node, Edge, GraphElement

#########################################################################################
#                                    COMPONENT TESTS                                    #       
#########################################################################################

class BaseGraphTest(unittest.TestCase):

	def build_graph(self):
		return Graph()


class GraphCreationTest(BaseGraphTest):

	def testGraphCreation(self):
		self.g = Graph()
		self.failUnlessEqual(self.g.order, 0)
		self.failUnlessEqual(self.g.size, 0)
		self.g = Graph(nodes=['a', 'b', 'c'], edges=[('a', 'b'), ('a', 'c')])
		self.failUnlessEqual(self.g.order, 3)
		self.failUnlessEqual(self.g.size, 2)
		self.failUnlessEqual(self.g[('a','b')].is_directed, True)
		self.failUnlessEqual(self.g[('a','c')].is_directed, True)
		self.g = Graph(nodes=['a', 'b', 'c'], edges={('a', 'b'):{'is_directed':False}, ('a', 'c'):{'is_directed':False}})
		self.failUnlessEqual(self.g.order, 3)
		self.failUnlessEqual(self.g.size, 2)
		self.failUnlessEqual(self.g[frozenset(('a','b'))].is_directed, False)
		self.failUnlessEqual(self.g[frozenset(('a','c'))].is_directed, False)
		self.failUnlessEqual(self.g[frozenset(('b','a'))].is_directed, False)
		self.failUnlessEqual(self.g[frozenset(('c','a'))].is_directed, False)


class NodeCreationTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.node_1 = self.g.add_node() # basic node
		self.node_2 = self.g.add_node("node2") # node with name, no data
		self.node_3 = self.g.add_node(foo="stuff") # data, no name
		self.node_4 =  self.g.add_node("node4", foo="stuff") # data and name
		self.node_5 =  self.g.add_node("node5", foo="stuff", hello="world") # mutiple data attributes and name

	def testNodeCreation(self):
		# test Graph.add_node fully
		self.failUnlessEqual(self.node_1.data, {}) # data is empty
		self.failUnlessEqual(self.node_2.name, "node2")
		self.failUnlessEqual(self.node_2.data, {})
		self.failUnlessEqual(self.node_3.data, {"foo": "stuff"})
		self.failUnlessEqual(self.node_4.name, "node4")
		self.failUnlessEqual(self.node_4.data, {"foo": "stuff"})
		self.failUnlessEqual(self.node_5.name, "node5")
		self.failUnlessEqual(self.node_5.data, {"foo": "stuff", "hello":"world"})
		self.failUnlessEqual(self.node_5.incoming, []) # no edges connected
		self.failUnlessEqual(self.node_5.outgoing, [])
		self.failUnlessEqual(self.node_5.incoming, [])
		self.failUnlessEqual(self.node_5.bidirectional, [])
		self.failUnlessEqual(self.node_5.degree, 0)
		self.failUnlessEqual(self.node_5.get_adjacent(), []) # no adjacent nodes

	def testNodeCreationFailPoints(self):
		# ensure that node creation fails when it's supposed to
		self.failUnlessRaises(TypeError, self.g.add_node, "two", "names")
		self.test_dict = {"a":"b", "b":"c"}
		self.failUnlessRaises(TypeError, self.g.add_node, self.test_dict)

class EdgeCreationTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.node_1 = self.g.add_node()
		self.node_2 = self.g.add_node()
		self.node_3 = self.g.add_node("node3", foo="stuff")
		self.node_4 = self.g.add_node("node4", hello="world")
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2)
		self.edge_2 = self.g.add_edge(self.node_1, self.node_2, "edge2")
		self.edge_3 = self.g.add_edge(self.node_1, self.node_2, foo="stuff")
		self.edge_4 = self.g.add_edge(self.node_1, self.node_2, "edge4", foo="stuff")
		self.edge_5 = self.g.add_edge(self.node_1, self.node_2, "edge5", foo="stuff", hello="world")
		self.edge_6 = self.g.add_edge(self.node_1, self.node_2, "edge6", False, foo="stuff", hello="world")
		self.edge_7 = self.g.add_edge(self.node_1, self.node_1, "edge7", False, foo="stuff", hello="world")
		self.edge_8 = self.g.add_edge("node3", "node4", "edge8", foo="stuff", hello="world")
		self.edge_9 = self.g.add_edge("node_5", "node_6", "5->6")

	def testEdgeCreation(self):
		# test Graph.add_edge fully
		self.failUnlessEqual(self.edge_1.start, self.node_1)
		self.failUnlessEqual(self.edge_1.end, self.node_2)
		self.failUnless(self.edge_1 in self.node_1.outgoing)
		self.failUnlessEqual(self.edge_1 in self.node_1.incoming, False)
		self.failUnless(self.edge_1 in self.node_2.incoming)
		self.failUnlessEqual(self.edge_1 in self.node_2.outgoing, False)
		self.failUnlessEqual(self.edge_1.data, {})
		self.failUnlessEqual(self.edge_2.name, "edge2")
		self.failUnlessEqual(self.edge_2.data, {})
		self.failUnlessEqual(self.edge_3.data, {"foo": "stuff"})
		self.failUnlessEqual(self.edge_4.data, {"foo": "stuff"})
		self.failUnlessEqual(self.edge_4.name, "edge4")
		self.failUnlessEqual(self.edge_5.name, "edge5")
		self.failUnlessEqual(self.edge_5.data, {"foo": "stuff", "hello":"world"})
		self.failUnlessEqual(self.edge_5.start, self.node_1)
		self.failUnlessEqual(self.edge_5.end, self.node_2)
		self.failUnless(self.edge_5 in self.node_1.outgoing)
		self.failUnlessEqual(self.edge_5 in self.node_1.incoming, False)
		self.failUnless(self.edge_5 in self.node_2.incoming)
		self.failUnlessEqual(self.edge_5 in self.node_2.outgoing, False)
		self.failUnlessEqual(self.edge_5 in self.node_3.outgoing, False)
		self.failUnlessEqual(self.edge_5 in self.node_3.incoming, False)
		self.failUnlessEqual(self.edge_6.name, "edge6")
		self.failUnlessEqual(self.edge_6.data, {"foo": "stuff", "hello":"world"})
		self.failUnlessEqual(self.edge_6.start, self.node_1)
		self.failUnlessEqual(self.edge_6.end, self.node_2)
		self.failUnless(self.edge_6 in self.node_1.outgoing)
		self.failUnless(self.edge_6 in self.node_1.incoming)
		self.failUnless(self.edge_6 in self.node_2.incoming)
		self.failUnless(self.edge_6 in self.node_2.outgoing)
		self.failUnlessEqual(self.edge_7.name, "edge7")
		self.failUnlessEqual(self.edge_7.data, {"foo": "stuff", "hello":"world"})
		self.failUnlessEqual(self.edge_7.start, self.node_1)
		self.failUnlessEqual(self.edge_7.end, self.node_1)
		self.failUnless(self.edge_7 in self.node_1.outgoing)
		self.failUnless(self.edge_7 in self.node_1.incoming)
		self.failUnlessEqual(self.edge_7 in self.node_2.incoming, False)
		self.failUnlessEqual(self.edge_7 in self.node_2.outgoing, False)
		self.failUnlessEqual(self.edge_8.name, "edge8")
		self.failUnlessEqual(self.edge_8.data, {"foo": "stuff", "hello":"world"})
		self.failUnlessEqual(self.edge_8.start, self.node_3)
		self.failUnlessEqual(self.edge_8.end, self.node_4)
		self.failUnless(self.edge_8 in self.node_3.outgoing)
		self.failUnlessEqual(self.edge_8 in self.node_1.incoming, False)
		self.failUnless(self.edge_8 in self.node_4.incoming)
		self.failUnlessEqual(self.edge_8 in self.node_4.outgoing, False)
		self.failUnlessEqual(self.edge_8 in self.node_1.outgoing, False)
		self.failUnlessEqual(self.edge_8 in self.node_1.incoming, False)
		self.failUnlessEqual(set(self.node_2.bidirectional), set([self.edge_6]))
		self.failUnlessEqual(self.edge_9.start, self.g["node_5"])
		self.failUnlessEqual(self.edge_9.end, self.g["node_6"])

	def testEdgeCreationFailPoints(self):
		# ensure that edge creation fails when it's supposed to
		self.test_dict = {"a":"b", "b":"c"}
		self.failUnlessRaises(TypeError, self.g.add_edge, self.node_1, self.node_2, self.test_dict)


class EdgeUnpackTest(EdgeCreationTest):

	def testUnpacking(self):
		edges = [getattr(self, "edge_%i" % i) for i in range(1, 9)]
		# make sure that the first one is always start
		self.failUnless(all([edge[0] == edge.start for edge in edges]), True)
		# make sure that the second one is always end
		self.failUnless(all([edge[1] == edge.end for edge in edges]), True)
		# make sure that the third one fails
		self.failUnlessRaises(IndexError, edges[0].__getitem__, 2)
		# and the negative first
		self.failUnlessRaises(IndexError, edges[0].__getitem__, -1)


class AdjacencyTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.node_1 = self.g.add_node("node1")
		self.node_2 = self.g.add_node("node2")
		self.node_3 = self.g.add_node("node3")
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1")
		self.edge_2 = self.g.add_edge(self.node_1, self.node_3, "edge2", is_directed=False)
		self.edge_3 = self.g.add_edge(self.node_2, self.node_2, "edge3")

	def testAdjacency(self):
		# test the node.get_adjacent
		self.failUnlessEqual(set(self.node_1.get_adjacent()), set([self.node_2, self.node_3]))
		self.failUnlessEqual(set(self.node_2.get_adjacent()), set([self.node_2]))
		self.failUnlessEqual(set(self.node_3.get_adjacent()), set([self.node_1]))
		self.failUnlessEqual(set(self.node_1.get_adjacent(False, True)), set([self.node_3]))
		self.failUnlessEqual(set(self.node_2.get_adjacent(False, True)), set([self.node_1, self.node_2]))
		self.failUnlessEqual(set(self.node_3.get_adjacent(False, True)), set([self.node_1]))
		self.failUnlessEqual(set(self.node_1.get_adjacent(True, True)), set([self.node_2, self.node_3]))
		self.failUnlessEqual(set(self.node_2.get_adjacent(True, True)), set([self.node_1, self.node_2]))
		self.failUnlessEqual(set(self.node_3.get_adjacent(True, True)), set([self.node_1]))


class RemovalTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.node_1 = self.g.add_node("node1")
		self.node_2 = self.g.add_node("node2")
		self.node_3 = self.g.add_node("node3")

	def testRemoveNodeDirected(self):
		# remove an node with a directed edge
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1")
		self.edge_2 = self.g.add_edge(self.node_2, self.node_3, "edge2")
		self.g.remove_node(self.node_1)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_2, self.node_3]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2]))
		self.node_1 = self.g.add_node("node1")
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1")
		self.g.remove_node(self.node_2)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1, self.node_3]))
		self.failUnlessEqual(set(self.g.edges), set())
		self.edge_3 = self.g.add_edge(self.node_3, self.node_3, "edge3")
		self.g.remove_node(self.node_3)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1]))
		self.failUnlessEqual(set(self.g.edges), set())

	def testRemoveNodeUndirected(self):
		# remove an node with a undirected edge
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1", False)
		self.edge_2 = self.g.add_edge(self.node_2, self.node_3, "edge2", False)
		self.g.remove_node(self.node_1)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_2, self.node_3]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2]))
		self.node_1 = self.g.add_node("node1")
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1", False)
		self.g.remove_node(self.node_2)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1, self.node_3]))
		self.failUnlessEqual(set(self.g.edges), set())
		self.edge_3 = self.g.add_edge(self.node_3, self.node_3, "edge3", False)
		self.g.remove_node(self.node_3)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1]))
		self.failUnlessEqual(set(self.g.edges), set())

	def testRemoveEdgeDirected(self):
		# remove a directed edge
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1")
		self.edge_2 = self.g.add_edge(self.node_2, self.node_3, "edge2")
		self.g.remove_edge(self.edge_1)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1, self.node_2, self.node_3]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2]))
		self.edge_3 = self.g.add_edge(self.node_3, self.node_3, "edge3")
		self.g.remove_edge(self.edge_3)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1, self.node_3, self.node_2]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2]))

	def testRemoveNodeUndirected(self):
		# remove a undirected edge
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1", False)
		self.edge_2 = self.g.add_edge(self.node_2, self.node_3, "edge2", False)
		self.g.remove_edge(self.edge_1)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1, self.node_2, self.node_3]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2]))
		self.edge_3 = self.g.add_edge(self.node_3, self.node_3, "edge3", False)
		self.g.remove_edge(self.edge_3)
		self.failUnlessEqual(set(self.g.nodes), set([self.node_1, self.node_3, self.node_2]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2]))


class OverwriteTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.node_1 = self.g.add_node("node1")
		self.node_2 = self.g.add_node("node2")
		self.edge_1 = self.g.add_edge("node1", "node2", "edge1")
		self.edge_2 = self.g.add_edge("node2", "node2", "edge2")

	def testOverwriteNode(self):
		# test node overwriting behavior
		self.node_3 = self.g.add_node("node1")
		self.failUnlessEqual(set(self.g.nodes), set([self.node_3, self.node_2]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2]))
		self.node_4 = self.g.add_node("node2")
		self.failUnlessEqual(set(self.g.nodes), set([self.node_3, self.node_4]))
		self.failUnlessEqual(set(self.g.edges), set())
		self.failUnlessEqual(self.node_1.edges, [])
		self.failUnlessEqual(self.node_1.incoming, [])
		self.failUnlessEqual(self.node_1.outgoing, [])
		self.failUnlessEqual(self.node_1.bidirectional, [])
		self.edge_3 = self.g.add_edge("node1", "node2", "edge1")
		self.failUnlessEqual(self.node_3.edges, [self.edge_3])
		self.failUnlessEqual(self.node_1.edges, [])
		self.failUnlessEqual(self.node_1.incoming, [])
		self.failUnlessEqual(self.node_1.outgoing, [])
		self.failUnlessEqual(self.node_1.bidirectional, [])

	def testOverwriteEdge(self):
		# test edge overwriting behavior
		self.node_3 = self.g.add_node("node3")
		self.edge_3 = self.g.add_edge(self.node_1, self.node_3, "edge3")
		self.edge_4 = self.g.add_edge(self.node_2, self.node_1, "edge3")
		self.failUnlessEqual(set(self.g.nodes), set([self.node_3, self.node_1, self.node_2]))
		self.failUnlessEqual(set(self.g.edges), set([self.edge_2, self.edge_3, self.edge_1]))
		self.failUnlessEqual(self.node_3.edges, [])
		self.failUnlessEqual(self.node_3.incoming, [])
		self.failUnlessEqual(self.node_3.outgoing, [])
		self.failUnlessEqual(self.node_3.bidirectional, [])
		self.failUnlessEqual(self.node_2.edges, [self.edge_1, self.edge_2, self.edge_4])


class GraphPropertiesTest(BaseGraphTest):

	def setUp(self):
		self.g1 = self.build_graph()
		self.g2 = self.build_graph()
		self.g1_node_1 = self.g1.add_node("node1")
		self.g1_node_2 = self.g1.add_node("node2")
		self.g1_node_3 = self.g1.add_node("node3")
		self.g1_edge_1 = self.g1.add_edge(self.g1_node_1, self.g1_node_2, "edge1")
		self.g1_edge_2 = self.g1.add_edge(self.g1_node_2, self.g1_node_3, "edge2")
		self.g1_edge_3 = self.g1.add_edge(self.g1_node_3, self.g1_node_3, "edge3")
		self.g1.remove_node(self.g1_node_1)
		self.g2_node_1 = self.g2.add_node("node1")
		self.g2_node_2 = self.g2.add_node("node2")
		self.g2_node_3 = self.g2.add_node("node3")
		self.g2_edge_1 = self.g2.add_edge(self.g2_node_1, self.g2_node_2, "edge1")
		self.g2_edge_2 = self.g2.add_edge(self.g2_node_2, self.g2_node_3, "edge2")
		self.g2_edge_3 = self.g2.add_edge(self.g2_node_3, self.g2_node_3, "edge3")
		self.g2.remove_node(self.g2_node_1)

	def testEqual(self):
		# test == between nodes and edges of different graphs
		self.failUnlessEqual(self.g1_node_2 == self.g2_node_2, True)
		self.failUnlessEqual(self.g2_node_3 == self.g1_node_3, True)
		self.failUnlessEqual(self.g1_node_2 == self.g2_node_3, False)
		self.failUnlessEqual(self.g1_edge_2 == self.g2_edge_2, True)
		self.failUnlessEqual(self.g2_edge_3 == self.g1_edge_3, True)
		self.failUnlessEqual(self.g1_edge_2 == self.g2_edge_3, False)

	def testNotEqual(self):
		# test != between nodes and edges
		self.failUnlessEqual(self.g1_node_2 != self.g2_node_2, False)
		self.failUnlessEqual(self.g2_node_3 != self.g1_node_3, False)
		self.failUnlessEqual(self.g1_node_2 != self.g2_node_3, True)
		self.failUnlessEqual(self.g1_edge_2 != self.g2_edge_2, False)
		self.failUnlessEqual(self.g2_edge_3 != self.g1_edge_3, False)
		self.failUnlessEqual(self.g1_edge_2 != self.g2_edge_3, True)

	def testIn(self):
		""" test functionality of 'in' against known values """
		self.failUnlessEqual(self.g1_node_1 in self.g1, False)
		self.failUnlessEqual(self.g1_node_2 in self.g1, True)
		self.failUnlessEqual(self.g1_node_3 in self.g1, True)
		self.failUnlessEqual(self.g1_edge_1 in self.g1, False)
		self.failUnlessEqual(self.g1_edge_2 in self.g1, True)
		self.failUnlessEqual(self.g1_edge_3 in self.g1, True)
		self.failUnlessEqual(self.g1_node_2 in self.g2, True)
		self.failUnlessEqual(self.g1_edge_2 in self.g2, True)

	def testGetItem(self):
		# test retreiving items from graphs
		self.failUnlessEqual(self.g1[self.g1_node_2.name], self.g1_node_2)
		self.failUnlessEqual(self.g2[self.g2_edge_2.name], self.g2_edge_2)
		self.failUnlessRaises(KeyError, lambda: self.g1[self.g1_edge_1.name])

	def testOrder(self):
		# test order against known amount
		self.failUnlessEqual(self.g1.order, 2)
		self.failUnlessEqual(self.g2.order, 2)
		self.g1.remove_node(self.g1_node_2)
		self.failUnlessEqual(self.g1.order, 1)
		self.g2.remove_edge(self.g2_edge_3)
		self.failUnlessEqual(self.g2.order, 2)

	def testSize(self):
		# test size against known amount
		self.failUnlessEqual(self.g1.size, 2)
		self.failUnlessEqual(self.g2.size, 2)
		self.g2.remove_node(self.g2_node_2)
		self.failUnlessEqual(self.g2.size, 1)
		self.g2.remove_edge(self.g2_edge_3)
		self.failUnlessEqual(self.g2.size, 0)


class GraphSearchTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.node_1 = self.g.add_node("node1", first_name="Bob", last_name="Bobson")
		self.node_2 = self.g.add_node("node2", first_name="Tom", last_name="Tompson")
		self.node_3 = self.g.add_node("node3", first_name="Bill", last_name="Billson")
		self.node_4 = self.g.add_node("node4", first_name="Will", last_name="Bobson")
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1", distance=50, friends=True)
		self.edge_2 = self.g.add_edge(self.node_2, self.node_3, "edge2", distance=50, friends=False)
		self.edge_3 = self.g.add_edge(self.node_4, self.node_3, "edge3", distance=10, friends=True)
		self.edge_4 = self.g.add_edge(self.node_4, self.node_4, "edge4", distance=0, friends=False)

	def testNodeSearch(self):
		# test node searching behavior
		l = list(self.g.search_nodes(first_name="Geremy"))
		self.failUnlessEqual(l, [])
		l = list(self.g.search_nodes(name="Bob"))
		self.failUnlessEqual(l, [])
		l = list(self.g.search_nodes(name="node2"))
		self.failUnlessEqual(set(l), set([self.node_2]))
		l = list(self.g.search_nodes(first_name="Bob"))
		self.failUnlessEqual(set(l), set([self.node_1]))
		l = list(self.g.search_nodes(last_name="Bobson"))
		self.failUnlessEqual(set(l), set([self.node_4, self.node_1]))
		l = list(self.g.search_nodes(first_name="Bill", last_name="Billson"))
		self.failUnlessEqual(set(l), set([self.node_3]))

	def testEdgeSearch(self):
		# test edge searching behavior
		l = list(self.g.search_edges(weight=5))
		self.failUnlessEqual(l, [])
		s = set(self.g.search_edges(name="edge2"))
		self.failUnlessEqual(s, set([self.edge_2]))
		s = set(self.g.search_edges(end=self.node_2))
		self.failUnlessEqual(s, set([self.edge_1]))
		s = set(self.g.search_edges(start=self.node_4))
		self.failUnlessEqual(s, set([self.edge_3, self.edge_4]))
		s = set(self.g.search_edges(distance=50))
		self.failUnlessEqual(s, set([self.edge_1, self.edge_2]))
		s = set(self.g.search_edges(distance=50, friends=True))
		self.failUnlessEqual(s, set([self.edge_1]))


class EdgeMovementTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.node_1 = self.g.add_node("node1", first_name="Bob", last_name="Bobson")
		self.node_2 = self.g.add_node("node2", first_name="Tom", last_name="Tompson")
		self.node_3 = self.g.add_node("node3", first_name="Bill", last_name="Billson")
		self.edge_1 = self.g.add_edge(self.node_1, self.node_2, "edge1", distance=50, friends=True)
		self.edge_2 = self.g.add_edge(self.node_1, self.node_3, "edge2", False, distance=50, friends=False)
		self.edge_3 = self.g.add_edge(self.node_3, self.node_3, "edge3", False, distance=0, friends=False)

	def testEdgeMoving(self):
		# test the behavior of edge movement
		self.g.move_edge("edge1")
		self.failUnlessEqual(self.edge_1.start, self.node_1)
		self.failUnlessEqual(self.edge_1.end, self.node_2)
		self.g.move_edge("edge1", self.node_2, self.node_1)
		self.failUnlessEqual(self.edge_1.start, self.node_2)
		self.failUnlessEqual(self.edge_1.end, self.node_1)
		self.g.move_edge("edge2", self.node_2, self.node_3)
		self.failUnlessEqual(self.edge_2.start, self.node_2)
		self.failUnlessEqual(self.edge_2.end, self.node_3)
		self.g.move_edge("edge3", self.node_1, self.node_2)
		self.failUnlessEqual(self.edge_3.start, self.node_1)
		self.failUnlessEqual(self.edge_3.end, self.node_2)
		self.failUnlessEqual(set(self.node_1.incoming), set([self.edge_1, self.edge_3]))
		self.failUnlessEqual(set(self.node_1.outgoing), set([self.edge_3]))
		self.failUnlessEqual(set(self.node_2.incoming), set([self.edge_2, self.edge_3]))
		self.failUnlessEqual(set(self.node_2.outgoing), set([self.edge_2, self.edge_1, self.edge_3]))
		self.failUnlessEqual(set(self.node_3.incoming), set([self.edge_2]))
		self.failUnlessEqual(set(self.node_3.outgoing), set([self.edge_2]))


class GetElementsTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.jimmy = self.g.add_node(city="New York")
		self.ted = self.g.add_node(city="Atlanta")
		self.dan = self.g.add_node(city="Seattle")
		self.paul = self.g.add_node(city="Austin")
		self.j_to_t = self.g.add_edge(self.jimmy, self.ted, distance=850)
		self.t_to_d = self.g.add_edge(self.ted, self.dan, distance=2150)
		self.d_to_p = self.g.add_edge(self.dan, self.paul, distance=2850)

	def testNodeGetting(self):
		# test for equivalence
		self.failUnless(all(node in [self.jimmy, self.ted, self.dan, self.paul] for node in self.g.nodes))
		self.failUnless(all(node in self.g.nodes for node in [self.jimmy, self.ted, self.dan, self.paul]))
		self.failUnlessEqual([n for n in self.g.search_nodes(city="New York")], [self.jimmy])

	def testEdgeGetting(self):
		# test for equivalence
		self.failUnless(all(edge in set([self.j_to_t, self.t_to_d, self.d_to_p]) for edge in self.g.edges))
		self.failUnless(all(edge in self.g.edges for edge in set([self.j_to_t, self.t_to_d, self.d_to_p])))
		self.failUnlessEqual([e for e in self.g.search_edges(distance=2850)], [self.d_to_p])


class TraversalTest(BaseGraphTest):

	def setUp(self):
		g = self.build_graph()
		nodes = {}
		edges = []
		nodes["A"] = g.add_node(first_name="A")
		nodes["B"] = g.add_node(first_name="B")
		nodes["C"] = g.add_node(first_name="C")
		nodes["D"] = g.add_node(first_name="D")
		nodes["E"] = g.add_node(first_name="E")
		nodes["F"] = g.add_node(first_name="F")
		nodes["G"] = g.add_node(first_name="G")
		edges += [g.add_edge(nodes["A"], nodes["B"])]
		edges += [g.add_edge(nodes["B"], nodes["D"])]
		edges += [g.add_edge(nodes["B"], nodes["F"])]
		edges += [g.add_edge(nodes["F"], nodes["E"])]
		edges += [g.add_edge(nodes["A"], nodes["C"])]
		edges += [g.add_edge(nodes["C"], nodes["G"])]
		edges += [g.add_edge(nodes["A"], nodes["E"])]
		self.g = g
		self.nodes = nodes
		self.edges = edges

	def testDepthFirstTraversal(self):
		nodes = self.nodes
		edges = self.edges
		g = self.g
		positions = {}
		for pos, node in enumerate(g.depth_first_traversal(nodes["A"])):
			positions[node.first_name] = pos
		self.failUnless(positions["A"] < positions["B"])
		self.failUnless(positions["A"] < positions["C"])
		self.failUnless(positions["A"] < positions["E"])
		self.failUnless(positions["B"] < positions["D"])
		self.failUnless(positions["C"] < positions["G"])
		self.failUnless(positions["F"] > min(positions["B"], positions["E"]))

		# test for equivalence problem
		a = g.add_node(first_name="A")
		b1 = g.add_node(first_name="B")
		b2 = g.add_node(first_name="B")
		c = g.add_node(first_name="C")
		d = g.add_node(first_name="D")
		g.add_edge(a, b1)
		g.add_edge(a, b2)
		g.add_edge(b1, c)
		g.add_edge(b2, d)
		self.failUnlessEqual(set((node for node in g.depth_first_traversal(a))), set([a, b1, b2, c, d]))


	def testBreadthFirstTraversal(self):
		g = self.g
		nodes = self.nodes
		edges = self.edges
		positions = {}
		for pos, node in enumerate(g.breadth_first_traversal(nodes["A"])):
			positions[node.first_name] = pos
		self.failUnless(positions["A"] < min(positions["B"], positions["C"], positions["E"]))
		self.failUnless(max(positions["B"], positions["C"], positions["E"]) < min(positions["D"], positions["F"], positions["G"]))

	def testLevelTraversal(self):
		g = self.g
		ab = g.add_edge('a', 'b', is_directed=False)
		bc = g.add_edge('b', 'c', is_directed=False)
		cd = g.add_edge('c', 'd', is_directed=False)
		ad = g.add_edge('a', 'd', is_directed=False)
		ef = g.add_edge('e', 'f', is_directed=False)
		ff = g.add_edge('f', 'f')
		a_levels = [level for level in g.level_traversal('a')]
		b_levels = [level for level in g.level_traversal('b')]
		c_levels = [level for level in g.level_traversal('c')]
		d_levels = [level for level in g.level_traversal('d')]
		e_levels = [level for level in g.level_traversal('e')]
		f_levels = [level for level in g.level_traversal('f')]
		self.failUnlessEqual(a_levels, [set([g['a']]), set([g['b'], g['d']]), set([g['c']])])
		self.failUnlessEqual(b_levels, [set([g['b']]), set([g['a'], g['c']]), set([g['d']])])
		self.failUnlessEqual(c_levels, [set([g['c']]), set([g['b'], g['d']]), set([g['a']])])
		self.failUnlessEqual(d_levels, [set([g['d']]), set([g['a'], g['c']]), set([g['b']])])
		self.failUnlessEqual(e_levels, [set([g['e']]), set([g['f']])])
		self.failUnlessEqual(f_levels, [set([g['f']]), set([g['e']])])

class InductionTest(BaseGraphTest):

	def setUp(self):
		g = self.build_graph()
		kirk = g.add_node(first_name="kirk")
		spock = g.add_node(first_name="spock")
		bones = g.add_node(first_name="bones")
		uhura = g.add_node(first_name="uhura")
		self.e1 = g.add_edge(kirk, spock)
		self.e2 = g.add_edge(kirk, bones)
		self.e3 = g.add_edge(kirk, uhura)
		self.e4 = g.add_edge(uhura, spock)
		self.e5 = g.add_edge(uhura, bones)
		self.g = g
		self.kirk = kirk
		self.spock = spock
		self.bones = bones
		self.uhura = uhura

	def testNodeInduction(self):
		g = self.g
		kirk = self.kirk
		spock = self.spock
		bones = self.bones
		uhura = self.uhura
		new_mission = g.induce_subgraph(spock, bones, uhura)
		self.failUnlessEqual(set([node.first_name for node in new_mission.nodes]), set(["spock", "bones", "uhura"]))
		spock = list(new_mission.search_nodes(first_name="spock"))[0]
		bones = list(new_mission.search_nodes(first_name="bones"))[0]
		uhura = list(new_mission.search_nodes(first_name="uhura"))[0]
		self.failUnless("spock" in set([edge.end.first_name for edge in uhura.outgoing]))
		self.failUnless("bones" in set([edge.end.first_name for edge in uhura.outgoing]))
		self.failIf("kirk" in set([edge.end.first_name for edge in uhura.outgoing]))

	def testEdgeInduction(self):
		g = self.g
		kirk = self.kirk
		spock = self.spock
		bones = self.bones
		uhura = self.uhura
		new_mission = g.edge_induce_subgraph(self.e4, self.e5)
		self.failUnlessEqual(set([node.first_name for node in new_mission.nodes]), set(["spock", "bones", "uhura"]))
		spock = set(new_mission.search_nodes(first_name="spock")).pop()
		bones = set(new_mission.search_nodes(first_name="bones")).pop()
		uhura = set(new_mission.search_nodes(first_name="uhura")).pop()
		self.failUnlessEqual(uhura.outgoing[0].end.first_name, "spock")
		self.failUnlessEqual(uhura.outgoing[1].end.first_name, "bones")


class GraphFailureTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()

	"""
	Tests to be written:
	unnamed node or edge removal
	nonexistant node or edge removal
	"""


class GraphCorrectnessTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()

	def testGetCommonEdges(self):
		""" Testing common edges correctness """
		g = self.g
		n1 = g.add_node()
		n2 = g.add_node()
		n3 = g.add_node()
		n4 = g.add_node()
		e1 = g.add_edge(n1, n2)
		e2 = g.add_edge(n2, n1)
		e3 = g.add_edge(n1, n3)
		e4 = g.add_edge(n2, n3)
		e5 = g.add_edge(n4, n4)
		e6 = g.add_edge(n4, n4)
		self.failUnlessEqual(g.get_common_edges(n1, n2), set([e1, e2]))
		self.failUnlessEqual(g.get_common_edges(n4, n4), set([e5, e6]))
		self.failUnlessEqual(g.get_common_edges(n1, n1), set([e1, e2, e3]))

	def testEdgeContraction(self):
		g = self.g
		n1 = g.add_node(1)
		n2 = g.add_node(2)
		n3 = g.add_node(3)
		n4 = g.add_node(4)
		n5 = g.add_node(6)
		n6 = g.add_node(7)
		# n1-n3 are completely connected
		g.add_edge(n1, n2)
		i1 = g.add_edge(n1, n3)
		g.add_edge(n2, n1)
		i2 = g.add_edge(n2, n3)
		o1 = g.add_edge(n3, n1)
		o2 = g.add_edge(n3, n2)
		# n4-n6 are completely connected
		o3 = g.add_edge(n4, n5)
		o4 = g.add_edge(n4, n6)
		i3 = g.add_edge(n5, n4)
		g.add_edge(n5, n6)
		i4 = g.add_edge(n6, n4)
		g.add_edge(n6, n5)
		# n3 and n4 have one edge between them
		e = g.add_edge(n3, n4)
		# you'll add the values of the two nodes
		# together to get the new value
		getter = lambda s: s.name
		get_new_data = lambda x, y: {"value": getter(x) + getter(y)}
		# contract the graph
		n = g.contract_edge(e, get_new_data)
		# test n's properties
		self.failUnlessEqual(set(n.incoming), set([i1, i2, i3, i4]))
		self.failUnlessEqual(set(n.outgoing), set([o1, o2, o3, o4]))
		self.failUnlessEqual(n.value, 7)
		# test the graph's properties
		self.failUnlessEqual(g.order, 5)
		self.failUnlessEqual(g.size, 12)

	def testUnion(self):
		g1 = self.build_graph()
		g2 = self.build_graph()
		g1.add_node(1)
		g1.add_node(2)
		g1.add_node(3)
		g1.add_edge(1, 2, 12)
		g1.add_edge(2, 3, 23)
		g1.add_edge(3, 1, 31)
		g2.add_node(3)
		g2.add_node(4)
		g2.add_node(5)
		g2.add_edge(3, 4, 34)
		g2.add_edge(4, 5, 45)
		g2.add_edge(5, 3, 53, color='red')
		union = g1 | g2
		self.failUnlessEqual(set([1, 2, 3, 4, 5]), set([node.name for node in union.nodes]))
		self.failUnlessEqual(set([12, 23, 31, 34, 45, 53]), set([edge.name for edge in union.edges]))
		self.failUnlessEqual(union.order, 5)
		self.failUnlessEqual(union.size, 6)
		self.failUnlessEqual(union[53].color, 'red')

	def testIntersection(self):
		g1 = self.build_graph()
		g2 = self.build_graph()
		one = g1.add_node(1)
		two = g1.add_node(2)
		three = g1.add_node(3)
		g1.add_edge(one, two, 12)
		g1.add_edge(two, three, 13)
		g1.add_edge(three, one, 31)
		one_2 = g2.add_node(1)
		three_2 = g2.add_node(3)
		five = g2.add_node(5)
		g2.add_edge(one_2, five, 15)
		g2.add_edge(five, three_2, 53)
		g2.add_edge(three_2, one_2, 31)
		one_and_three = g1 & g2
		self.failUnlessEqual(set([1, 3]), set([node.name for node in one_and_three.nodes]))
		self.failUnlessEqual(one_and_three.order, 2)
		self.failUnlessEqual(one_and_three.size, 1)

	def testDifference(self):
		g1 = self.build_graph()
		g2 = self.build_graph()
		zero = g1.add_node(0)
		one = g1.add_node(1)
		two = g1.add_node(2)
		three = g1.add_node(3)
		g1.add_edge(zero, two)
		g1.add_edge(one, two)
		g1.add_edge(two, three)
		g1.add_edge(three, one)
		one_2 = g2.add_node(1)
		three_2 = g2.add_node(3)
		five = g2.add_node(5)
		g2.add_edge(one_2, five)
		g2.add_edge(five, three_2)
		g2.add_edge(three_2, one_2)
		diff = g1 - g2
		self.failUnlessEqual(set([0, 2]), set([node.name for node in diff.nodes]))
		self.failUnlessEqual(diff.order, 2)
		self.failUnlessEqual(diff.size, 1)

	def testGetAllConnected(self):
		# setup
		g = self.build_graph()
		# one connected component
		n1 = g.add_node(first_name="Bob")
		n2 = g.add_node(first_name="Bill")
		g.add_edge(n1, n2)
		component_1 = frozenset([n1, n2])
		# one solitary component
		n3 = g.add_node(first_name="Dan")
		component_2 = frozenset([n3])
		# one looped component
		n4 = g.add_node(first_name="John")
		g.add_edge(n4, n4)
		component_3 = frozenset([n4])
		# and test
		components = set([component_1, component_2, component_3])
		self.failUnlessEqual(set(frozenset(i) for i in g.get_connected_components()), components)

	def testGetShortestPaths(self):
		# trivial graph
		g = self.build_graph()
		n1 = g.add_node(first_name="Geremy")
		paths = g.get_shortest_paths(n1, pretty=False)
		self.failUnlessEqual(paths, {n1: (0, [])})
		# less trivial graph
		g = self.build_graph()
		n1 = g.add_node(first_name="Geremy")
		n2 = g.add_node(first_name="Bob")
		n3 = g.add_node(first_name="Snowflake")
		e1 = g.add_edge(n1, n2, weight=4)
		e2 = g.add_edge(n1, n3, weight=5)
		paths = g.get_shortest_paths(n1, get_weight=lambda e: e.weight, pretty=False)
		self.failUnlessEqual(paths, {n1: (0, []), n2: (4, [e1]), n3: (5, [e2])})
		# tricksy graph
		g = self.build_graph()
		n1 = g.add_node(first_name="Geremy")
		n2 = g.add_node(first_name="Bob")
		n3 = g.add_node(first_name="Snowflake")
		# normal edges
		e1 = g.add_edge(n1, n2, weight=5)
		e2 = g.add_edge(n2, n3, weight=1)
		# notice that the path from n1 to n2 to n3 is
		# shorter than the path from n1 to n3
		e3 = g.add_edge(n1, n3, weight=7)
		# form a loop
		e4 = g.add_edge(n3, n3, weight=1)
		# form a cycle
		e5 = g.add_edge(n3, n2, weight=1)
		paths = g.get_shortest_paths(n1, get_weight=lambda e: e.weight, pretty=False)
		self.failUnlessEqual(paths, {n1: (0, []), n2: (5, [e1]), n3: (6, [e1, e2])})

	def testStronglyConnectedComponents(self):
		g = self.build_graph()
		n1 = g.add_node(value=1)
		n2 = g.add_node(value=2)
		n3 = g.add_node(value=3)
		n4 = g.add_node(value=4)
		n5 = g.add_node(value=6)
		n6 = g.add_node(value=7)
		# n1-n3 are completely connected
		g.add_edge(n1, n2)
		g.add_edge(n1, n3)
		g.add_edge(n2, n1)
		g.add_edge(n2, n3)
		g.add_edge(n3, n1)
		g.add_edge(n3, n2)
		# n4-n6 are completely connected
		g.add_edge(n4, n5)
		g.add_edge(n4, n6)
		g.add_edge(n5, n4)
		g.add_edge(n5, n6)
		g.add_edge(n6, n4)
		g.add_edge(n6, n5)
		# get strongly connected components
		comp = g.get_strongly_connected()
		self.failUnlessEqual(set([frozenset([n1, n2, n3]), frozenset([n4, n5, n6])]), set([frozenset(i) for i in comp]))


#########################################################################################################################################
#                                                               SCENARIO TESTS                                                          #
#########################################################################################################################################

"""
TODO:
	- 2 node directed edge test
	- 2 node undirected edge test
	- 3 node directed cycle test
	- 3 node undirected cycle test
	- 3 node disconnected test
	- 5 node directed cycle component
	- k5 component
	- 5 node undirected cycle with a loop on each node
	- five node directed tree
	- five node undirected tree
"""

class ZeroNodeTest(BaseGraphTest):
	# tests all applicable operations with the zero node case

	def setUp(self):
		self.g = self.build_graph()

	def testContainers(self):
		# test to make sure that the containers are okay
		self.failUnlessEqual({}, self.g._nodes)
		self.failUnlessEqual({}, self.g._edges)

	def testIn(self):
		# tests the in operator for names
		self.failUnlessEqual("A" in self.g, False)
		# tests the in operator for elements
		n = Node("B")
		self.failUnlessEqual(n in self.g, False)

	def testGetItem(self):
		# tests the [] operator for names
		self.failUnlessRaises(KeyError, self.g.__getitem__, "A")
		# and for elements
		n = Node("B")
		self.failUnlessRaises(KeyError, self.g.__getitem__, n)

	def testNodes(self):
		# test to ensure that the nodes property works
		self.failUnlessEqual(list(self.g.nodes), [])

	def testEdges(self):
		# test to ensure that the edges property works
		self.failUnlessEqual(list(self.g.edges), [])

	def testSearchNodes(self):
		self.failUnlessEqual(list(self.g.search_nodes(value="bob")), [])

	def testSearchEdges(self):
		self.failUnlessEqual(list(self.g.search_edges(value="bob")), [])

	def testGetConnectedComponents(self):
		self.failUnlessEqual(self.g.get_connected_components(), [])

	def testGetStronglyConnected(self):
		self.failUnlessEqual(self.g.get_strongly_connected(), [])

	def testSize(self):
		self.failUnlessEqual(self.g.size, 0)

	def testOrder(self):
		self.failUnlessEqual(self.g.order, 0)

	def testEdgeContraction(self):
		# test it on a bad edge
		self.failUnlessRaises(KeyError, self.g.contract_edge, "A", lambda x, y: dict())
		self.failUnlessRaises(KeyError, self.g.contract_edge, Edge(Node("A"), Node("B")), lambda x, y: dict())

	def testTranspose(self):
		tmp = copy.copy(self.g)
		tmp.transpose()
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(tmp.nodes), set(tmp.edges)))

	def testInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with a bad node
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, Node("A"))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, "A")

	def testEdgeInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.edge_induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with a bad node
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, Edge(Node("A"), Node("B")))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, "A")

	def testUnion(self):
		# test it on ourselves
		G = self.g | self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testIntersection(self):
		# test it on ourselves
		G = self.g & self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testDifference(self):
		# test it on ourselves
		G = self.g - self.g
		self.failUnlessEqual((set(G.nodes), set(G.edges)), (set(), set()))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testContains(self):
		# test it on ourselves
		self.failUnlessEqual(self.g.contains(self.g), True)
		self.failUnlessEqual(self.g > self.g, False)
		self.failUnlessEqual(self.g < self.g, False)
		self.failUnlessEqual(self.g, self.g)
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, True)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, True)
		self.failIfEqual(G, self.g)
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, True)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, True)
		self.failIfEqual(G, self.g)
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, True)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, True)
		self.failIfEqual(G, self.g)
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, True)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, True)
		self.failIfEqual(G, self.g)


class OneNodeDirectedTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.A = self.g.add_node("A")
		self.AA = self.g.add_edge("A", "A", "AA")

	def testContainers(self):
		self.failUnlessEqual(self.g._nodes, {"A": self.A})
		self.failUnlessEqual(self.g._edges, {"AA": self.AA})

	def testIn(self):
		# make sure that node membership by name works
		self.failUnlessEqual("A" in self.g, True)
		# make sure that edge membership by name works
		self.failUnlessEqual("AA" in self.g, True)
		# make sure that a name not in the graph does not work
		self.failUnlessEqual("B" in self.g, False)
		# make sure that node membership by node works
		self.failUnlessEqual(self.A in self.g, True)
		# make sure that edge membership by edge works
		self.failUnlessEqual(self.AA in self.g, True)
		# make sure that an element not in the graph does not work
		n = Node("Z")
		self.failUnlessEqual(n in self.g, False)
		# make sure that an element matching one in the graph
		# will still return true
		n = Node("A")
		self.failUnlessEqual(n in self.g, True)

	def testGetItem(self):
		# make sure that getting nodes by name works
		self.failUnlessEqual(self.g["A"], self.A)
		# make sure that getting edges by name works
		self.failUnlessEqual(self.g["AA"], self.AA)
		# make sure that getting nodes by element works
		self.failUnlessEqual(self.g[self.A], self.A)
		# make sure that getting edges by element works
		self.failUnlessEqual(self.g[self.AA], self.AA)
		# make sure that getting a nonexistant element by name fails
		self.failUnlessRaises(KeyError, self.g.__getitem__, "B")
		# and that getting a nonmember element by element fails
		n = Node("B")
		self.failUnlessRaises(KeyError, self.g.__getitem__, n)
		# test to make sure that a nonmember element which tests equal
		# to a member element will retrieve the member element
		n = Node("A")
		e = Edge(self.g["A"], self.g["A"], "AA")
		self.failUnless(self.g[n] is self.A)
		self.failUnless(self.g[e] is self.AA)

	def testNodes(self):
		self.failUnlessEqual(list(self.g.nodes), [self.A])

	def testEdges(self):
		self.failUnlessEqual(list(self.g.edges), [self.AA])

	def testAddNode(self):
		# make sure that making a new node succeeds
		B = self.g.add_node("B")
		self.failUnlessEqual(self.g["B"], B)
		self.failUnless(self.g["B"] is B)
		self.failUnlessEqual(self.g.order, 2)
		self.failUnlessEqual(B in set(self.g.nodes), True)
		# make sure that adding a new node overwrites the old one
		# if they share a name
		A = self.g.add_node("A")
		# equality
		self.failUnlessEqual(self.g["A"], A)
		# identity
		self.failUnless(self.g["A"] is A)
		# membership
		self.failUnlessEqual(A in self.g, True)
		# data store membership
		self.failUnlessEqual(A in self.g._nodes.values(), True)
		# order- it should have added B, then replaced self.A with A,
		# thus 2
		self.failUnlessEqual(self.g.order, 2)

	def testAddEdge(self):
		# make sure that adding a new edge by node names succeeds
		aa = self.g.add_edge("A", "A", "aa")
		self.failUnlessEqual(self.g["aa"], aa)
		self.failUnless(self.g["aa"] is aa)
		self.failUnlessEqual(aa in self.g, True)
		self.failUnlessEqual("aa" in self.g, True)
		self.failUnlessEqual(self.g.size, 2)
		self.failUnlessEqual(aa in set(self.g.edges), True)
		self.failUnlessEqual(aa in self.g._edges.values(), True)
		# make sure that adding a new edge by node succeeds
		# also check to make sure that overwriting occurs
		aa = self.g.add_edge(self.A, self.A, "aa")
		self.failUnlessEqual(self.g["aa"], aa)
		self.failUnless(self.g["aa"] is aa)
		self.failUnlessEqual(aa in self.g, True)
		self.failUnlessEqual("aa" in self.g, True)
		self.failUnlessEqual(self.g.size, 2)
		self.failUnlessEqual(aa in set(self.g.edges), True)
		self.failUnlessEqual(aa in self.g._edges.values(), True)

	def testRemoveNode(self):
		# make sure node removal works by name
		A = self.g.remove_node("A")
		self.failUnlessEqual(self.A, A)
		self.failUnlessEqual(self.g.order, 0)
		self.failIf(A in self.g)
		self.failIf(A.name in self.g)
		self.failUnlessRaises(KeyError, self.g.__getitem__, "A")
		self.failUnlessRaises(KeyError, self.g.__getitem__, self.A)
		# make sure it removes all the edges
		self.failUnlessEqual(self.g.size, 0)

	def testSearchNodes(self):
		self.failUnlessEqual(list(self.g.search_nodes(name="A")), [self.A])
		self.failUnlessEqual(list(self.g.search_nodes(value="bob")), [])

	def testSearchEdges(self):
		self.failUnlessEqual(list(self.g.search_edges(name="AA")), [self.AA])
		self.failUnlessEqual(list(self.g.search_edges(start="A")), [self.AA])
		self.failUnlessEqual(list(self.g.search_edges(end="A")), [self.AA])
		self.failUnlessEqual(list(self.g.search_edges(start=self.A)), [self.AA])
		self.failUnlessEqual(list(self.g.search_edges(end=self.A)), [self.AA])
		self.failUnlessEqual(list(self.g.search_edges(name="AA", start=self.A, end=self.A)), [self.AA])

	def testGetCommonEdges(self):
		self.failUnlessEqual(self.g.get_common_edges(self.A, self.A), set(self.A.edges))
		self.failUnlessEqual(self.g.get_common_edges("A", "A"), set(self.A.edges))
		self.failUnlessRaises(KeyError, self.g.get_common_edges, self.A, Node("B"))
		self.failUnlessRaises(KeyError, self.g.get_common_edges, "A", "B")

	def testWalkNodes(self):
		w = self.g.walk_nodes(self.A)
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(candidates, [self.A])
				w.send(candidates.pop())
			else:
				break
		w = self.g.walk_nodes("A")
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(candidates, [self.A])
				w.send(candidates.pop())
			else:
				break
		w1 = self.g.walk_nodes("B")
		w2 = self.g.walk_nodes(Node("B"))
		self.failUnlessRaises(KeyError, next, w1)
		self.failUnlessRaises(KeyError, next, w2)

	def testWalkEdges(self):
		w = self.g.walk_edges(self.AA)
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(candidates, [self.AA])
				w.send(candidates.pop())
			else:
				break
		w = self.g.walk_edges("AA")
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(candidates, [self.AA])
				w.send(candidates.pop())
			else:
				break
		w1 = self.g.walk_edges("B")
		w2 = self.g.walk_edges(Node("B"))
		self.failUnlessRaises(KeyError, next, w1)
		self.failUnlessRaises(KeyError, next, w2)

	def testHeuristicWalk(self):
		class Heuristic:
			def __init__(self):
				self.iterations = 0
				self.iter_max = 5
			def __call__(self, candidates):
				if self.iterations < self.iter_max:
					if candidates:
						self.iterations += 1
						return candidates.pop()
				return None
		self.failUnlessEqual(list(self.g.heuristic_walk(self.A, Heuristic())), [self.A, self.A, self.A, self.A, self.A])
		self.failUnlessEqual(list(self.g.heuristic_walk("A", Heuristic())), [self.A, self.A, self.A, self.A, self.A])
		self.failUnlessEqual(list(self.g.heuristic_walk(self.A, Heuristic(), reverse=True)), [self.A, self.A, self.A, self.A, self.A])
		self.failUnlessEqual(list(self.g.heuristic_walk("A", Heuristic(), reverse=True)), [self.A, self.A, self.A, self.A, self.A])
		self.failUnlessEqual(list(self.g.heuristic_walk(Node("A"), Heuristic(), reverse=True)), [self.A, self.A, self.A, self.A, self.A])
		w = self.g.heuristic_walk("B", Heuristic())
		w2 = self.g.heuristic_walk(Node("B"), Heuristic())
		self.failUnlessRaises(KeyError, list, w)
		self.failUnlessRaises(KeyError, list, w2)

	def testHeuristicTraversal(self):
		# should only yield one node, no matter what
		self.failUnlessEqual(list(self.g.heuristic_traversal(self.A, lambda s: s.pop())), [self.A])
		self.failUnlessEqual(list(self.g.heuristic_traversal("A", lambda s: s.pop())), [self.A])
		self.failUnlessEqual(list(self.g.heuristic_traversal(self.A, lambda s: s.pop(0))), [self.A])
		self.failUnlessEqual(list(self.g.heuristic_traversal("A", lambda s: s.pop(0))), [self.A])
		self.failUnlessEqual(list(self.g.heuristic_traversal(Node("A"), lambda s: s.pop())), [self.A])
		t = self.g.heuristic_traversal("B", lambda s: s.pop())
		t2 = self.g.heuristic_traversal(Node("B"), lambda s: s.pop())
		self.failUnlessRaises(KeyError, list, t)
		self.failUnlessRaises(KeyError, list, t2)

	def testDepthFirstTraversal(self):
		# should only yield one node, no matter what
		self.failUnlessEqual(list(self.g.depth_first_traversal(self.A)), [self.A])
		self.failUnlessEqual(list(self.g.depth_first_traversal("A")), [self.A])
		self.failUnlessEqual(list(self.g.depth_first_traversal(Node("A"))), [self.A])
		t = self.g.depth_first_traversal("B")
		t2 = self.g.depth_first_traversal(Node("B"))
		self.failUnlessRaises(KeyError, list, t)
		self.failUnlessRaises(KeyError, list, t2)

	def testBreadthFirstTraversal(self):
		# should only yield one node, no matter what
		self.failUnlessEqual(list(self.g.breadth_first_traversal(self.A)), [self.A])
		self.failUnlessEqual(list(self.g.breadth_first_traversal("A")), [self.A])
		self.failUnlessEqual(list(self.g.breadth_first_traversal(Node("A"))), [self.A])
		t = self.g.breadth_first_traversal("B")
		t2 = self.g.breadth_first_traversal(Node("B"))
		self.failUnlessRaises(KeyError, list, t)
		self.failUnlessRaises(KeyError, list, t2)

	def testGetConnectedComponents(self):
		self.failUnlessEqual(list(self.g.get_connected_components()), [set([self.A])])

	def testGetStronglyConnected(self):
		self.failUnlessEqual(list(self.g.get_strongly_connected()), [set([self.A])])

	def testGetShortestPaths(self):
		self.failUnlessEqual(self.g.get_shortest_paths(self.A, pretty=False), {self.A: (0, [])})
		self.failUnlessEqual(self.g.get_shortest_paths("A", pretty=False), {self.A: (0, [])})
		self.failUnlessEqual(self.g.get_shortest_paths(Node("A"), pretty=False), {self.A: (0, [])})
		self.failUnlessRaises(KeyError, self.g.get_shortest_paths, Node("B"), pretty=False)
		self.failUnlessRaises(KeyError, self.g.get_shortest_paths, "B", pretty=False)

	def testOrder(self):
		self.failUnlessEqual(self.g.order, 1)

	def testSize(self):
		self.failUnlessEqual(self.g.size, 1)

	def testEdgeContraction(self):
		# in this case, it should delete one node and add one node
		def node_initializer(x, y):
			d = x.data
			d["name"] = x.name + "2"
			return d
		n = self.g.contract_edge(self.AA, node_initializer)
		# make sure that the new node is data equivalent
		self.failUnlessEqual(self.A.data, n.data)
		# make sure its name is related as specified
		self.failUnlessEqual(n.name, self.A.name + "2")
		# make sure that there are the same number of nodes
		self.failUnlessEqual(self.g.order, 1)
		# make sure that there are no edges
		self.failUnlessEqual(self.g.size, 0)
		# test it on a bad edge
		self.failUnlessRaises(KeyError, self.g.contract_edge, "BB", lambda x, y: dict())
		self.failUnlessRaises(KeyError, self.g.contract_edge, Edge(Node("A"), Node("B")), lambda x, y: dict())

	def testTranspose(self):
		tmp = copy.copy(self.g)
		tmp.transpose()
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(tmp.nodes), set(tmp.edges)))

	def testInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with our only node
		g1 = self.g.induce_subgraph(self.A)
		self.failUnlessEqual(list(g1.nodes), [self.A])
		self.failUnlessEqual(list(g1.edges), [self.AA])
		# test it with a bad node
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, Node("B"))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, "B")

	def testEdgeInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.edge_induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with our only edge
		g1 = self.g.edge_induce_subgraph(self.AA)
		self.failUnlessEqual(list(g1.nodes), [self.A])
		self.failUnlessEqual(list(g1.edges), [self.AA])
		# test it with a bad node
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, Edge(Node("A"), Node("B")))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, "B")

	def testUnion(self):
		# test it on ourselves
		G = self.g | self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testIntersection(self):
		# test it on ourselves
		G = self.g & self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testDifference(self):
		# test it on ourselves
		G = self.g - self.g
		self.failUnlessEqual((set(G.nodes), set(G.edges)), (set(), set()))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testContains(self):
		# test it on the zero node case
		G = self.build_graph()
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(self.g > G, True)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(G < self.g, True)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node("A")
		G.add_edge("A", "A", "AA")
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failUnlessEqual(G, self.g)
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node("A")
		G.add_node("B")
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node("A")
		G.add_node("B")
		G.add_node("C")
		G.add_edge("A", "B", "AB")
		G.add_edge("B", "C", "BC")
		G.add_edge("C", "A", "CA")
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)


class OneNodeUndirectedTest(OneNodeDirectedTest):

	def setUp(self):
		self.g = self.build_graph()
		self.A = self.g.add_node("A")
		self.AA = self.g.add_edge("A", "A", "AA", is_directed=False)


class OneNodeDoubleUndirectedTest(OneNodeDirectedTest):

	def setUp(self):
		self.g = self.build_graph()
		self.A = self.g.add_node("A")
		self.AA = self.g.add_edge("A", "A", "AA", is_directed=False)
		self.AA_2 = self.g.add_edge("A", "A", "AA_2", is_directed=False)

	def testEdges(self):
		self.failUnlessEqual(set(self.g.edges), set([self.AA, self.AA_2]))

	def testContainers(self):
		self.failUnlessEqual(self.g._nodes, {"A": self.A})
		self.failUnlessEqual(self.g._edges, {"AA": self.AA, "AA_2": self.AA_2})

	def testAddEdge(self):
		# make sure that adding a new edge by node names succeeds
		aa = self.g.add_edge("A", "A", "aa")
		self.failUnlessEqual(self.g["aa"], aa)
		self.failUnless(self.g["aa"] is aa)
		self.failUnlessEqual(aa in self.g, True)
		self.failUnlessEqual("aa" in self.g, True)
		self.failUnlessEqual(self.g.size, 3)
		self.failUnlessEqual(aa in set(self.g.edges), True)
		self.failUnlessEqual(aa in self.g._edges.values(), True)
		# make sure that adding a new edge by node succeeds
		# also check to make sure that overwriting occurs
		aa = self.g.add_edge(self.A, self.A, "aa")
		self.failUnlessEqual(self.g["aa"], aa)
		self.failUnless(self.g["aa"] is aa)
		self.failUnlessEqual(aa in self.g, True)
		self.failUnlessEqual("aa" in self.g, True)
		self.failUnlessEqual(self.g.size, 3)
		self.failUnlessEqual(aa in set(self.g.edges), True)
		self.failUnlessEqual(aa in self.g._edges.values(), True)

	def testSearchEdges(self):
		self.failUnlessEqual(list(self.g.search_edges(name="B")), [])
		self.failUnlessEqual(list(self.g.search_edges(name="AA")), [self.AA])
		self.failUnlessEqual(set(self.g.search_edges(start="A")), set([self.AA, self.AA_2]))
		self.failUnlessEqual(set(self.g.search_edges(end="A")), set([self.AA, self.AA_2]))
		self.failUnlessEqual(set(self.g.search_edges(start=self.A)), set([self.AA, self.AA_2]))
		self.failUnlessEqual(set(self.g.search_edges(end=self.A)), set([self.AA, self.AA_2]))
		self.failUnlessEqual(list(self.g.search_edges(name="AA", start=self.A, end=self.A)), [self.AA])

	def testSize(self):
		self.failUnlessEqual(self.g.size, 2)

	def testInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(set(g1.edges), set())
		# test it with our only node
		g1 = self.g.induce_subgraph(self.A)
		self.failUnlessEqual(list(g1.nodes), [self.A])
		self.failUnlessEqual(set(g1.edges), set([self.AA, self.AA_2]))
		# test it with a bad node
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, Node("B"))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, "B")

	def testEdgeContraction(self):
		# in this case, it should delete one node and add one node
		def node_initializer(x, y):
			d = x.data
			d["name"] = x.name + "2"
			return d
		n = self.g.contract_edge(self.AA, node_initializer)
		# make sure that the new node is data equivalent
		self.failUnlessEqual(self.A.data, n.data)
		# make sure its name is related as specified
		self.failUnlessEqual(n.name, self.A.name + "2")
		# make sure that there are the same number of nodes
		self.failUnlessEqual(self.g.order, 1)
		# make sure that only the other loop remains
		self.failUnlessEqual(self.g.size, 1)
		# test it on a bad edge
		self.failUnlessRaises(KeyError, self.g.contract_edge, "BB", lambda x, y: dict())
		self.failUnlessRaises(KeyError, self.g.contract_edge, Edge(Node("A"), Node("B")), lambda x, y: dict())

	def testWalkNodes(self):
		w = self.g.walk_nodes(self.A)
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(candidates, [self.A])
				w.send(candidates.pop())
			else:
				break
		w = self.g.walk_nodes("A")
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(candidates, [self.A])
				w.send(candidates.pop())
			else:
				break
		w1 = self.g.walk_nodes("B")
		w2 = self.g.walk_nodes(Node("B"))
		self.failUnlessRaises(KeyError, next, w1)
		self.failUnlessRaises(KeyError, next, w2)

	def testWalkEdges(self):
		w = self.g.walk_edges(self.AA)
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(set(candidates), set([self.AA, self.AA_2]))
				w.send(candidates.pop())
			else:
				break
		w = self.g.walk_edges("AA")
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(set(candidates), set([self.AA, self.AA_2]))
				w.send(candidates.pop())
			else:
				break
		w1 = self.g.walk_edges("B")
		w2 = self.g.walk_edges(Node("B"))
		self.failUnlessRaises(KeyError, next, w1)
		self.failUnlessRaises(KeyError, next, w2)

	def testWalkPath(self):
		w = self.g.walk_path(self.A)
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(set(candidates), set([self.AA, self.AA_2]))
				w.send(candidates.pop())
			else:
				break
		w = self.g.walk_edges("AA")
		iteration = 0
		for candidates in w:
			if iteration < 5:
				iteration += 1
				self.failUnlessEqual(set(candidates), set([self.AA, self.AA_2]))
				w.send(candidates.pop())
			else:
				break
		w1 = self.g.walk_edges("B")
		w2 = self.g.walk_edges(Node("B"))
		self.failUnlessRaises(KeyError, next, w1)
		self.failUnlessRaises(KeyError, next, w2)

	def testContains(self):
		# test it on the zero node case
		G = self.build_graph()
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(self.g > G, True)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(G < self.g, True)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node("A")
		G.add_edge("A", "A", "AA")
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, True)
		self.failUnlessEqual(G < self.g, True)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node("A")
		G.add_node("B")
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)


class OneNodeDoubleDirectedTest(OneNodeDoubleUndirectedTest):

	def setUp(self):
		self.g = self.build_graph()
		self.A = self.g.add_node("A")
		self.AA = self.g.add_edge("A", "A", "AA")
		self.AA_2 = self.g.add_edge("A", "A", "AA_2")


class TwoNodeUnconnectedTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.A = self.g.add_node("A")
		self.B = self.g.add_node("B")

	def testContainers(self):
		self.failUnlessEqual(self.g._nodes, {"A": self.A, "B": self.B})
		self.failUnlessEqual(self.g._edges, {})

	def testNodes(self):
		self.failUnlessEqual(set(self.g.nodes), set([self.A, self.B]))

	def testEdges(self):
		self.failUnlessEqual(set(self.g.edges), set())

	def testIn(self):
		self.failUnlessEqual(self.A in self.g, True)
		self.failUnlessEqual(self.B in self.g, True)
		self.failUnlessEqual("A" in self.g, True)
		self.failUnlessEqual("B" in self.g, True)
		self.failUnlessEqual(Node("A") in self.g, True)
		self.failUnlessEqual(Node("B") in self.g, True)
		self.failUnlessEqual("C" in self.g, False)
		self.failUnlessEqual(Node("C") in self.g, False)

	def testGetItem(self):
		self.failUnless(self.A is self.g[self.A])
		self.failUnless(self.B is self.g[self.B])
		self.failUnless(self.A is self.g["A"])
		self.failUnless(self.B is self.g["B"])
		self.failUnless(self.A is self.g[Node("A")])
		self.failUnless(self.B is self.g[Node("B")])
		self.failUnlessRaises(KeyError, self.g.__getitem__, "C")
		self.failUnlessRaises(KeyError, self.g.__getitem__, Node("C"))
		self.failUnlessRaises(KeyError, self.g.__getitem__, Edge(self.A, self.B, "C"))

	def testSearchNodes(self):
		self.failUnlessEqual(set(self.g.search_nodes(name="A")), set([self.A]))
		self.failUnlessEqual(set(self.g.search_nodes(name="B")), set([self.B]))
		self.failUnlessEqual(set(self.g.search_nodes(name="C")), set())
		self.failUnlessEqual(set(self.g.search_nodes(value=5)), set())

	def testSearchEdges(self):
		self.failUnlessEqual(set(self.g.search_edges(name="AA")), set())
		self.failUnlessEqual(set(self.g.search_edges(value=5)), set())

	def testGetCommonEdges(self):
		self.failUnlessEqual(self.g.get_common_edges(self.A, self.B), set())
		self.failUnlessEqual(self.g.get_common_edges("A", "B"), set())
		self.failUnlessEqual(self.g.get_common_edges(self.B, self.A), set())
		self.failUnlessEqual(self.g.get_common_edges(self.A, self.A), set())
		self.failUnlessEqual(self.g.get_common_edges("A", "A"), set())
		self.failUnlessEqual(self.g.get_common_edges(self.B, self.B), set())
		self.failUnlessEqual(self.g.get_common_edges("B", "B"), set())
		self.failUnlessRaises(KeyError, self.g.get_common_edges, Node("C"), Node("D"))

	def testWalkNodes(self):
		# should die right off for either node
		w1 = self.g.walk_nodes(self.A)
		w2 = self.g.walk_nodes(self.B)
		w3 = self.g.walk_nodes("A")
		w4 = self.g.walk_nodes("B")
		w5 = self.g.walk_nodes(Node("A"))
		w6 = self.g.walk_nodes(Node("B"))
		w7 = self.g.walk_nodes("C")
		w8 = self.g.walk_nodes(Node("C"))
		for candidates in w1:
			self.failIf(candidates)
		for candidates in w2:
			self.failIf(candidates)
		for candidates in w3:
			self.failIf(candidates)
		for candidates in w4:
			self.failIf(candidates)
		for candidates in w5:
			self.failIf(candidates)
		for candidates in w6:
			self.failIf(candidates)
		self.failUnlessRaises(KeyError, next, w7)
		self.failUnlessRaises(KeyError, next, w8)

	def testWalkEdges(self):
		# no edges- should be easy
		w = self.g.walk_edges(Edge("A", "B", "AB"))
		self.failUnlessRaises(KeyError, next, w)
		w = self.g.walk_edges("AB")
		self.failUnlessRaises(KeyError, next, w)

	def testHeuristicWalk(self):
		# no edges- should be easy
		def heuristic(nodes):
			return nodes.pop()
		w1 = self.g.walk_nodes(self.A, heuristic)
		w2 = self.g.walk_nodes(self.B, heuristic)
		w3 = self.g.walk_nodes("A", heuristic)
		w4 = self.g.walk_nodes("B", heuristic)
		w5 = self.g.walk_nodes(Node("A"), heuristic)
		w6 = self.g.walk_nodes(Node("B"), heuristic)
		w7 = self.g.walk_nodes("C", heuristic)
		w8 = self.g.walk_nodes(Node("C"), heuristic)
		for candidates in w1:
			self.failIf(candidates)
		for candidates in w2:
			self.failIf(candidates)
		for candidates in w3:
			self.failIf(candidates)
		for candidates in w4:
			self.failIf(candidates)
		for candidates in w5:
			self.failIf(candidates)
		for candidates in w6:
			self.failIf(candidates)
		self.failUnlessRaises(KeyError, next, w7)
		self.failUnlessRaises(KeyError, next, w8)

	def testDepthFirstTraversal(self):
		self.failUnlessEqual(list(self.g.depth_first_traversal(self.A)), [self.A])
		self.failUnlessEqual(list(self.g.depth_first_traversal(self.B)), [self.B])
		self.failUnlessEqual(list(self.g.depth_first_traversal("A")), [self.A])
		self.failUnlessEqual(list(self.g.depth_first_traversal("B")), [self.B])
		t = self.g.depth_first_traversal("C")
		t2 = self.g.depth_first_traversal(Node("C"))
		self.failUnlessRaises(KeyError, next, t)
		self.failUnlessRaises(KeyError, next, t2)

	def testDepthFirstTraversal(self):
		self.failUnlessEqual(list(self.g.breadth_first_traversal(self.A)), [self.A])
		self.failUnlessEqual(list(self.g.breadth_first_traversal(self.B)), [self.B])
		self.failUnlessEqual(list(self.g.breadth_first_traversal("A")), [self.A])
		self.failUnlessEqual(list(self.g.breadth_first_traversal("B")), [self.B])
		t = self.g.breadth_first_traversal("C")
		t2 = self.g.breadth_first_traversal(Node("C"))
		self.failUnlessRaises(KeyError, next, t)
		self.failUnlessRaises(KeyError, next, t2)

	def testConnectedComponents(self):
		self.failUnlessEqual(set([frozenset(component) for component in self.g.get_connected_components()]), set([frozenset([self.A]), frozenset([self.B])]))

	def testStronglyConnectedComponents(self):
		self.failUnlessEqual(set([frozenset(component) for component in self.g.get_connected_components()]), set([frozenset([self.A]), frozenset([self.B])]))

	def testGetShortestPath(self):
		self.failUnlessEqual(self.g.get_shortest_paths(self.A, pretty=False), {self.A: (0, [])})
		self.failUnlessEqual(self.g.get_shortest_paths(self.B, pretty=False), {self.B: (0, [])})
		self.failUnlessEqual(self.g.get_shortest_paths("A", pretty=False), {self.A: (0, [])})
		self.failUnlessEqual(self.g.get_shortest_paths("B", pretty=False), {self.B: (0, [])})
		self.failUnlessEqual(self.g.get_shortest_paths(Node("A"), pretty=False), {self.A: (0, [])})
		self.failUnlessEqual(self.g.get_shortest_paths(Node("B"), pretty=False), {self.B: (0, [])})
		self.failUnlessRaises(KeyError, self.g.get_shortest_paths, "C", pretty=False)
		self.failUnlessRaises(KeyError, self.g.get_shortest_paths, Node("C"), pretty=False)

	def testOrder(self):
		self.failUnlessEqual(self.g.order, 2)

	def testSize(self):
		self.failUnlessEqual(self.g.size, 0)

	def testMoveEdge(self):
		self.failUnlessRaises(KeyError, self.g.move_edge, Edge("A", "B", "AB"), "B", "A")
		self.failUnlessRaises(KeyError, self.g.move_edge, "AB", "B", "A")

	def testContractEdge(self):
		self.failUnlessRaises(KeyError, self.g.contract_edge, Edge("A", "B", "AB"), lambda x,y: {})
		self.failUnlessRaises(KeyError, self.g.contract_edge, "AB", lambda x,y: {})

	def testTranspose(self):
		g = self.g
		g.transpose()
		self.failUnlessEqual(g, self.g)

	def testInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(set(g1.edges), set())
		# test it with node A
		g1 = self.g.induce_subgraph(self.A)
		self.failUnlessEqual(list(g1.nodes), [self.A])
		self.failUnlessEqual(set(g1.edges), set())
		# test it with node A by name
		g1 = self.g.induce_subgraph("A")
		self.failUnlessEqual(list(g1.nodes), [self.A])
		self.failUnlessEqual(set(g1.edges), set())
		# test it with node B
		g1 = self.g.induce_subgraph(self.B)
		self.failUnlessEqual(list(g1.nodes), [self.B])
		self.failUnlessEqual(set(g1.edges), set())
		# test it with node B by name
		g1 = self.g.induce_subgraph("B")
		self.failUnlessEqual(list(g1.nodes), [self.B])
		self.failUnlessEqual(set(g1.edges), set())
		# test it with both nodes
		g1 = self.g.induce_subgraph(self.A, self.B)
		self.failUnlessEqual(set(g1.nodes), set([self.A, self.B]))
		self.failUnlessEqual(set(g1.edges), set())
		# test it with a bad node
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, Node("C"))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, "C")

	def testEdgeInduceSubgraph(self):
		# test it without edges
		g1 = self.g.edge_induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with a bad edge
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, Edge(Node("A"), Node("B")))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, "C")

	def testUnion(self):
		# test it on ourselves
		G = self.g | self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testIntersection(self):
		# test it on ourselves
		G = self.g & self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testDifference(self):
		# test it on ourselves
		G = self.g - self.g
		self.failUnlessEqual((set(G.nodes), set(G.edges)), (set(), set()))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testContains(self):
		# test it on the zero node case
		G = self.build_graph()
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(self.g > G, True)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(G < self.g, True)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node("A")
		G.add_edge("A", "A", "AA")
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node("A")
		G.add_node("B")
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failUnlessEqual(G, self.g)
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node("A")
		G.add_node("B")
		G.add_node("C")
		G.add_edge("A", "B", "AB")
		G.add_edge("B", "C", "CB")
		G.add_edge("C", "A", "CA")
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, True)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, True)
		self.failIfEqual(G, self.g)
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)


class ThreeNodeCycleTest(BaseGraphTest):

	def setUp(self):
		self.g = self.build_graph()
		self.A = self.g.add_node("A")
		self.B = self.g.add_node("B")
		self.C = self.g.add_node("C")
		self.AB = self.g.add_edge("A", "B", "AB")
		self.BC = self.g.add_edge("B", "C", "BC")
		self.CA = self.g.add_edge("C", "A", "CA")

	def testIn(self):
		# test the three nodes and three edges
		self.failUnless(self.A in self.g)
		self.failUnless("A" in self.g)
		self.failUnless(self.B in self.g)
		self.failUnless("B" in self.g)
		self.failUnless(self.C in self.g)
		self.failUnless("C" in self.g)
		self.failUnless(self.AB in self.g)
		self.failUnless("AB" in self.g)
		self.failUnless(self.BC in self.g)
		self.failUnless("BC" in self.g)
		self.failUnless(self.CA in self.g)
		self.failUnless("CA" in self.g)
		self.failUnless(Node("A") in self.g)
		self.failUnless(Node("B") in self.g)
		self.failUnless(Node("C") in self.g)
		self.failUnless(Edge(self.A, self.B, "AB") in self.g)
		self.failUnless(Edge(self.B, self.C, "BC") in self.g)
		self.failUnless(Edge(self.C, self.A, "CA") in self.g)
		# test a bad node and node name

	def testGetItem(self):
		# test the three nodes and three edges
		self.failUnless(self.g[self.A] is self.A)
		self.failUnless(self.g[self.B] is self.B)
		self.failUnless(self.g[self.C] is self.C)
		self.failUnless(self.g[self.AB] is self.AB)
		self.failUnless(self.g[self.BC] is self.BC)
		self.failUnless(self.g[self.CA] is self.CA)
		self.failUnless(self.g["A"] is self.A)
		self.failUnless(self.g["B"] is self.B)
		self.failUnless(self.g["C"] is self.C)
		self.failUnless(self.g["AB"] is self.AB)
		self.failUnless(self.g["BC"] is self.BC)
		self.failUnless(self.g["CA"] is self.CA)
		self.failUnless(self.g[Node("A")] is self.A)
		self.failUnless(self.g[Node("B")] is self.B)
		self.failUnless(self.g[Node("C")] is self.C)
		self.failUnless(self.g[Edge(self.A, self.B, "AB")] is self.AB)
		self.failUnless(self.g[Edge(self.B, self.C, "BC")] is self.BC)
		self.failUnless(self.g[Edge(self.C, self.A, "CA")] is self.CA)
		# test the bad node case
		self.failUnlessRaises(KeyError, self.g.__getitem__, Node("D"))
		self.failUnlessRaises(KeyError, self.g.__getitem__, "D")
		# and the bad edge case
		self.failUnlessRaises(KeyError, self.g.__getitem__, Edge(self.B, self.A, "BA"))
		self.failUnlessRaises(KeyError, self.g.__getitem__, "BA")

	def testContains(self):
		# test it on the zero node case
		G = self.build_graph()
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(self.g > G, True)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(G < self.g, True)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node("A")
		G.add_edge("A", "A", "AA")
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node("A")
		G.add_node("B")
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, True)
		self.failUnlessEqual(G < self.g, True)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node("A")
		G.add_node("B")
		G.add_node("C")
		G.add_edge("A", "B", "AB")
		G.add_edge("B", "C", "BC")
		G.add_edge("C", "A", "CA")
		self.failUnlessEqual(self.g.contains(G), True)
		self.failUnlessEqual(G.contains(self.g), True)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failUnlessEqual(G, self.g)
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		self.failUnlessEqual(self.g.contains(G), False)
		self.failUnlessEqual(G.contains(self.g), False)
		self.failUnlessEqual(self.g < G, False)
		self.failUnlessEqual(self.g > G, False)
		self.failUnlessEqual(G < self.g, False)
		self.failUnlessEqual(G > self.g, False)
		self.failIfEqual(G, self.g)

	def testSearchNodes(self):
		self.failUnlessEqual(set(self.g.search_nodes(name="A")), set([self.A]))
		self.failUnlessEqual(set(self.g.search_nodes(name="B")), set([self.B]))
		self.failUnlessEqual(set(self.g.search_nodes(name="C")), set([self.C]))
		self.failUnlessEqual(set(self.g.search_nodes(name="D")), set())
		self.failUnlessEqual(set(self.g.search_nodes(value=5)), set())

	def testSearchEdges(self):
		self.failUnlessEqual(set(self.g.search_edges(name="AB")), set([self.AB]))
		self.failUnlessEqual(set(self.g.search_edges(name="BC")), set([self.BC]))
		self.failUnlessEqual(set(self.g.search_edges(name="CA")), set([self.CA]))
		self.failUnlessEqual(set(self.g.search_edges(start="A")), set([self.AB]))
		self.failUnlessEqual(set(self.g.search_edges(start=self.A)), set([self.AB]))
		self.failUnlessEqual(set(self.g.search_edges(end="A")), set([self.CA]))
		self.failUnlessEqual(set(self.g.search_edges(end=self.C)), set([self.BC]))
		self.failUnlessEqual(set(self.g.search_edges(name="AB", start="A", end="B")), set([self.AB]))
		self.failUnlessEqual(list(self.g.search_edges(name="AA", start=self.A, end=self.A)), [])

	def testGetCommonEdges(self):
		# test each actual path
		self.failUnlessEqual(self.g.get_common_edges(self.A, self.B), set([self.AB]))
		self.failUnlessEqual(self.g.get_common_edges("A", "B"), set([self.AB]))
		self.failUnlessEqual(self.g.get_common_edges(Node("A"), Node("B")), set([self.AB]))
		self.failUnlessEqual(self.g.get_common_edges(self.B, self.C), set([self.BC]))
		self.failUnlessEqual(self.g.get_common_edges("B", "C"), set([self.BC]))
		self.failUnlessEqual(self.g.get_common_edges(Node("B"), Node("C")), set([self.BC]))
		self.failUnlessEqual(self.g.get_common_edges(self.C, self.A), set([self.CA]))
		self.failUnlessEqual(self.g.get_common_edges("C", "A"), set([self.CA]))
		self.failUnlessEqual(self.g.get_common_edges(Node("C"), Node("A")), set([self.CA]))
		# now test them backwards
		self.failUnlessEqual(self.g.get_common_edges(self.B, self.A), set([self.AB]))
		self.failUnlessEqual(self.g.get_common_edges("B", "A"), set([self.AB]))
		self.failUnlessEqual(self.g.get_common_edges(Node("B"), Node("A")), set([self.AB]))
		self.failUnlessEqual(self.g.get_common_edges(self.C, self.B), set([self.BC]))
		self.failUnlessEqual(self.g.get_common_edges("C", "B"), set([self.BC]))
		self.failUnlessEqual(self.g.get_common_edges(Node("C"), Node("B")), set([self.BC]))
		self.failUnlessEqual(self.g.get_common_edges(self.C, self.A), set([self.CA]))
		self.failUnlessEqual(self.g.get_common_edges("A", "C"), set([self.CA]))
		self.failUnlessEqual(self.g.get_common_edges(Node("A"), Node("C")), set([self.CA]))
		# test bad start node
		self.failUnlessRaises(KeyError, self.g.get_common_edges, "D", "B")
		self.failUnlessRaises(KeyError, self.g.get_common_edges, Node("D"), "B")
		# test bad end node
		self.failUnlessRaises(KeyError, self.g.get_common_edges, "A", "D")
		self.failUnlessRaises(KeyError, self.g.get_common_edges, "A", Node("D"))

	def testWalkNodes(self):
		correctCycle = [self.B, self.C, self.A, self.B, self.C]
		w = self.g.walk_nodes(self.A)
		iteration = 0
		for candidates in w:
			if iteration < 5:
				self.failUnlessEqual(candidates, [correctCycle[iteration]])
				iteration += 1
				w.send(candidates.pop())
			else:
				break
		w = self.g.walk_nodes("A")
		iteration = 0
		for candidates in w:
			if iteration < 5:
				self.failUnlessEqual(candidates, [correctCycle[iteration]])
				iteration += 1
				w.send(candidates.pop())
			else:
				break
		w1 = self.g.walk_nodes("D")
		w2 = self.g.walk_nodes(Node("D"))
		self.failUnlessRaises(KeyError, next, w1)
		self.failUnlessRaises(KeyError, next, w2)

	def testWalkEdges(self):
		correctCycle = [self.BC, self.CA, self.AB, self.BC, self.CA]
		w = self.g.walk_edges(self.AB)
		iteration = 0
		for candidates in w:
			if iteration < 5:
				self.failUnlessEqual(candidates, [correctCycle[iteration]])
				iteration += 1
				w.send(candidates.pop())
			else:
				break
		w = self.g.walk_edges("AB")
		iteration = 0
		for candidates in w:
			if iteration < 5:
				self.failUnlessEqual(candidates, [correctCycle[iteration]])
				iteration += 1
				w.send(candidates.pop())
			else:
				break
		w1 = self.g.walk_edges("CB")
		w2 = self.g.walk_edges(Node("CB"))
		self.failUnlessRaises(KeyError, next, w1)
		self.failUnlessRaises(KeyError, next, w2)

	def testHeuristicWalk(self):
		class Heuristic:
			def __init__(self):
				self.iterations = 0
				self.iter_max = 5
			def __call__(self, candidates):
				if self.iterations < self.iter_max:
					if candidates:
						self.iterations += 1
						return candidates.pop()
				return None
		correct_cycle = [self.B, self.C, self.A, self.B, self.C]
		reverse_cycle = copy.copy(correct_cycle)
		reverse_cycle.reverse()
		self.failUnlessEqual(list(self.g.heuristic_walk(self.A, Heuristic())), correct_cycle)
		self.failUnlessEqual(list(self.g.heuristic_walk("A", Heuristic())), correct_cycle)
		self.failUnlessEqual(list(self.g.heuristic_walk(self.A, Heuristic(), reverse=True)), reverse_cycle)
		self.failUnlessEqual(list(self.g.heuristic_walk("A", Heuristic(), reverse=True)), reverse_cycle)
		self.failUnlessEqual(list(self.g.heuristic_walk(Node("A"), Heuristic(), reverse=True)), reverse_cycle)
		w = self.g.heuristic_walk("D", Heuristic())
		w2 = self.g.heuristic_walk(Node("D"), Heuristic())
		self.failUnlessRaises(KeyError, list, w)
		self.failUnlessRaises(KeyError, list, w2)

	def testHeuristicTraversal(self):
		# should only yield one node, no matter what
		self.failUnlessEqual(list(self.g.heuristic_traversal(self.A, lambda s: s.pop())), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.heuristic_traversal("A", lambda s: s.pop())), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.heuristic_traversal(self.A, lambda s: s.pop(0))), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.heuristic_traversal("A", lambda s: s.pop(0))), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.heuristic_traversal(Node("A"), lambda s: s.pop())), [self.A, self.B, self.C])
		t = self.g.heuristic_traversal("D", lambda s: s.pop())
		t2 = self.g.heuristic_traversal(Node("D"), lambda s: s.pop())
		self.failUnlessRaises(KeyError, list, t)
		self.failUnlessRaises(KeyError, list, t2)

	def testDepthFirstTraversal(self):
		# should only yield one node, no matter what
		self.failUnlessEqual(list(self.g.depth_first_traversal(self.A)), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.depth_first_traversal("A")), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.depth_first_traversal(Node("A"))), [self.A, self.B, self.C])
		t = self.g.depth_first_traversal("D")
		t2 = self.g.depth_first_traversal(Node("D"))
		self.failUnlessRaises(KeyError, list, t)
		self.failUnlessRaises(KeyError, list, t2)

	def testBreadthFirstTraversal(self):
		# should only yield one node, no matter what
		self.failUnlessEqual(list(self.g.breadth_first_traversal(self.A)), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.breadth_first_traversal("A")), [self.A, self.B, self.C])
		self.failUnlessEqual(list(self.g.breadth_first_traversal(Node("A"))), [self.A, self.B, self.C])
		t = self.g.breadth_first_traversal("D")
		t2 = self.g.breadth_first_traversal(Node("D"))
		self.failUnlessRaises(KeyError, list, t)
		self.failUnlessRaises(KeyError, list, t2)

	def testGetConnectedComponents(self):
		self.failUnlessEqual(list(self.g.get_connected_components()), [set([self.A, self.B, self.C])])

	def testGetStronglyConnected(self):
		self.failUnlessEqual(list(self.g.get_strongly_connected()), [set([self.A, self.B, self.C])])

	def testGetShortestPaths(self):
		self.failUnlessEqual(self.g.get_shortest_paths(self.A, pretty=False), {self.A: (0, []), self.B: (1, [self.AB]), self.C: (2, [self.AB, self.BC])})
		self.failUnlessEqual(self.g.get_shortest_paths("A", pretty=False), {self.A: (0, []), self.B: (1, [self.AB]), self.C: (2, [self.AB, self.BC])})
		self.failUnlessEqual(self.g.get_shortest_paths(Node("A"), pretty=False), {self.A: (0, []), self.B: (1, [self.AB]), self.C: (2, [self.AB, self.BC])})
		self.failUnlessRaises(KeyError, self.g.get_shortest_paths, Node("D"), pretty=False)
		self.failUnlessRaises(KeyError, self.g.get_shortest_paths, "D", pretty=False)

	def testOrder(self):
		self.failUnlessEqual(self.g.order, 3)

	def testSize(self):
		self.failUnlessEqual(self.g.size, 3)

	def testEdgeContraction(self):
		# in this case, it should delete two nodes and add one node
		def node_initializer(x, y):
			d = x.data
			d["name"] = x.name + "2"
			return d
		n = self.g.contract_edge(self.AB, node_initializer)
		# make sure that the new node is data equivalent
		self.failUnlessEqual(self.A.data, n.data)
		# make sure its name is related as specified
		self.failUnlessEqual(n.name, self.A.name + "2")
		self.failUnlessEqual(self.g.order, 2)
		self.failUnlessEqual(self.g.size, 2)
		# test it on a bad edge
		self.failUnlessRaises(KeyError, self.g.contract_edge, "BB", lambda x, y: dict())
		self.failUnlessRaises(KeyError, self.g.contract_edge, Edge(Node("A"), Node("B")), lambda x, y: dict())

	def testTranspose(self):
		tmp = copy.copy(self.g)
		tmp.transpose()
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(tmp.nodes), set(tmp.edges)))

	def testInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with node A
		g1 = self.g.induce_subgraph(self.A)
		self.failUnlessEqual(list(g1.nodes), [self.A])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with nodes A and B
		# test it with nodes B and C
		# test it with nodes C and A
		# test it with a bad node
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, Node("D"))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.induce_subgraph, "D")

	def testEdgeInduceSubgraph(self):
		# test it without nodes
		g1 = self.g.edge_induce_subgraph()
		self.failUnlessEqual(list(g1.nodes), [])
		self.failUnlessEqual(list(g1.edges), [])
		# test it with edge AB
		g1 = self.g.edge_induce_subgraph(self.AB)
		self.failUnlessEqual(set(g1.nodes), set([self.A, self.B]))
		self.failUnlessEqual(list(g1.edges), [self.AB])
		# test it with edge BC
		# test it with edge CA
		# test it with edges AB and BC
		# test it with edges BC and CA
		# test it with edges CA and AB
		# test it with a bad edge
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, Edge(Node("A"), Node("C")))
		# test it with a bad label
		self.failUnlessRaises(KeyError, self.g.edge_induce_subgraph, "D")

	def testUnion(self):
		# test it on ourselves
		G = self.g | self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g | G
		self.failUnlessEqual((set(self.g.nodes) | set(G.nodes), set(self.g.edges) | set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testIntersection(self):
		# test it on ourselves
		G = self.g & self.g
		self.failUnlessEqual((set(self.g.nodes), set(self.g.edges)), (set(G.nodes), set(G.edges)))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g & G
		self.failUnlessEqual((set(self.g.nodes) & set(G.nodes), set(self.g.edges) & set(G.edges)), (set(G2.nodes), set(G2.edges)))

	def testDifference(self):
		# test it on ourselves
		G = self.g - self.g
		self.failUnlessEqual((set(G.nodes), set(G.edges)), (set(), set()))
		# test it on a graph with one node with a loop
		G = self.build_graph()
		G.add_node(1)
		G.add_edge(1, 1, 11)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with two nodes
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with three nodes in a directed cycle
		G = self.build_graph()
		G.add_node(1)
		G.add_node(2)
		G.add_node(3)
		G.add_edge(1, 2, (1,2))
		G.add_edge(2, 3, (2,3))
		G.add_edge(3, 1, (3,1))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))
		# test it on a graph with five nodes in an undirected cycle
		G = self.build_graph()
		for i in range(5):
			G.add_node(i)
		for i in range(5):
			j = (i + 1) % 5
			G.add_edge(i, j, (i,j))
		G2 = self.g - G
		self.failUnlessEqual((set(self.g.nodes) - set(G.nodes), set(self.g.edges) - set(G.edges)), (set(G2.nodes), set(G2.edges)))


#################################################################################################################################
#                                                       PERFORMANCE TESTS                                                       #
#################################################################################################################################

"""
TODO:

	- totally redo these tests to use cProfile rather than the inaccurate timeit.
	- add tests for walks, all traversals, etc.
"""

class GraphPerformanceTest(BaseGraphTest):

	graph_setup = "from base import Graph; g = self.build_graph(); n = g.add_node(first_name='');"

	def testNodeAdditionPerformance(self):
		setup = self.graph_setup
		test = "for i in range(1000): g.add_node(first_name=i)"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		test = "for i in range(1000000): g.add_node(first_name=i)"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 5, msg="Performance check failed: it took %s seconds to add 1M nodes" % t1)
		self.failUnless(t2 < 5, msg="Performance check failed: it took %s seconds to add 1M nodes" % t2)

	def testNodeIterationPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_node(first_name=i)"
		test = "for i in g.nodes: pass"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_node(first_name=i)"
		test = "for i in g.nodes: pass"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t1)
		self.failUnless(t2 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t2)

	def testNodeSearchPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_node(first_name=i)"
		test = "[i for i in g.search_nodes(first_name=999)]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_node(first_name=i)"
		test = "[i for i in g.search_nodes(first_name=999999)]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t1)
		self.failUnless(t2 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M nodes" % t2)

	def testEdgeAdditionPerformance(self):
		setup = self.graph_setup
		test = "for i in range(1000): g.add_edge(n, n, first_name='a')"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		test = "for i in range(1000000): g.add_edge(n, n, first_name='a')"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 5, msg="Performance check failed: it took %s seconds to add 1M edges" % t1)
		self.failUnless(t2 < 5, msg="Performance check failed: it took %s seconds to add 1M edges" % t2)

	def testEdgeIterationPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, first_name='a')"
		test = "for i in g.edges: pass"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, first_name='a')"
		test = "for i in g.edges: pass"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t1)
		self.failUnless(t2 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t2)

	def testEdgeSearchPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, first_name='a')"
		test = "[i for i in g.search_edges(start='')]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, first_name='a')"
		test = "[i for i in g.search_edges(start='')]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t1)
		self.failUnless(t2 < 5, msg="Performance check failed: it took %s seconds to iterate through 1M edges" % t2)

	def testTraversalPerformance(self):
		setup = self.graph_setup + "\nfor i in range(1000): \n\tg.add_edge(n, n, first_name='a')"
		test = "[i for i in g.depth_first_traversal(n)]"
		t1 = timeit.timeit(setup=setup, stmt=test, number=1000)
		setup = self.graph_setup + "\nfor i in range(1000000): \n\tg.add_edge(n, n, first_name='a')"
		test = "[i for i in g.depth_first_traversal(n)]"
		t2 = timeit.timeit(setup=setup, stmt=test, number=1)
		tdiff = max(t1, t2) - min(t1, t2)
		self.failUnless(tdiff < max(t1, t2)/10, msg="Performance check failed: nonlinear performance (%s, %s)" % (t1, t2))
		self.failUnless(t1 < 5, msg="Performance check failed: it took %s seconds to traverse 1M node graphs" % t1)
		self.failUnless(t2 < 5, msg="Performance check failed: it took %s seconds to traverse 1M node graphs" % t2)


if __name__ == "__main__":
	GraphCorrectnessTest = unittest.TestLoader().loadTestsFromTestCase(GraphCorrectnessTest)
	GraphPropertiesTest = unittest.TestLoader().loadTestsFromTestCase(GraphPropertiesTest)
	GraphFailureTest = unittest.TestLoader().loadTestsFromTestCase(GraphFailureTest)
	GraphSearchTest = unittest.TestLoader().loadTestsFromTestCase(GraphSearchTest)
	GraphCreationTest = unittest.TestLoader().loadTestsFromTestCase(GraphCreationTest)
	NodeCreationTest = unittest.TestLoader().loadTestsFromTestCase(NodeCreationTest)
	EdgeCreationTest = unittest.TestLoader().loadTestsFromTestCase(EdgeCreationTest)
	EdgeMovementTest = unittest.TestLoader().loadTestsFromTestCase(EdgeMovementTest)
	GetElementsTest = unittest.TestLoader().loadTestsFromTestCase(GetElementsTest)
	TraversalTest = unittest.TestLoader().loadTestsFromTestCase(TraversalTest)
	InductionTest = unittest.TestLoader().loadTestsFromTestCase(InductionTest)
	ZeroNodeTest = unittest.TestLoader().loadTestsFromTestCase(ZeroNodeTest)
	AdjacencyTest = unittest.TestLoader().loadTestsFromTestCase(AdjacencyTest)
	OneNodeDirectedTest = unittest.TestLoader().loadTestsFromTestCase(OneNodeDirectedTest)
	OneNodeUndirectedTest = unittest.TestLoader().loadTestsFromTestCase(OneNodeUndirectedTest)
	OneNodeDoubleUndirectedTest = unittest.TestLoader().loadTestsFromTestCase(OneNodeDoubleUndirectedTest)
	OneNodeDoubleDirectedTest = unittest.TestLoader().loadTestsFromTestCase(OneNodeDoubleDirectedTest)
	TwoNodeUnconnectedTest = unittest.TestLoader().loadTestsFromTestCase(TwoNodeUnconnectedTest)
	ThreeNodeCycleTest = unittest.TestLoader().loadTestsFromTestCase(ThreeNodeCycleTest)
	RemovalTest = unittest.TestLoader().loadTestsFromTestCase(RemovalTest)
	OverwriteTest = unittest.TestLoader().loadTestsFromTestCase(OverwriteTest)
	EdgeUnpackTest = unittest.TestLoader().loadTestsFromTestCase(EdgeUnpackTest)
	suites = [GraphCorrectnessTest, GraphCreationTest, NodeCreationTest, EdgeCreationTest, GraphPropertiesTest, GraphSearchTest, EdgeMovementTest, GetElementsTest]
	suites += [ZeroNodeTest, RemovalTest, OverwriteTest, TraversalTest, InductionTest, GraphFailureTest, AdjacencyTest]
	suites += [OneNodeDirectedTest]
	suites += [OneNodeUndirectedTest]
	suites += [OneNodeDoubleUndirectedTest]
	suites += [OneNodeDoubleDirectedTest]
	suites += [TwoNodeUnconnectedTest]
	suites += [ThreeNodeCycleTest]
	suites += [EdgeUnpackTest]
	CorrectnessTest = unittest.TestSuite(suites)
	unittest.main()
