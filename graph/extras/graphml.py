#! /usr/bin/env python

"""
graphml.py

Written by Geremy Condra

Licensed under GPLv3

Released 15 April 2009

This module contains the machinery needed to load and store
graphs represented in the GraphML format.

It contains two functions of interest to the end user: load,
which takes a file as an argument and returns the parsed graph,
and store, which takes a graph and a file as arguments and
stores the graph in the given file.

It also contains Reader, a GraphML reader, and Writer, which
does its obvious opposite.
"""

# Copyright (C) 2009 Geremy Condra
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

from xml.sax.handler import ContentHandler
from xml.sax.saxutils import XMLGenerator
from xml.sax import parse

from pickle import loads, dumps

from collections import defaultdict


from graph.base import Graph

class Reader(ContentHandler):
	"""Generates a Graph from GraphML data."""

	def startDocument(self):
		"""Handles the beginning of a given document."""
		self.current_graph = None
		self.elements = []
		self.ids = {}
		self.defaults = {}

	def startElement(self, name, attrs):
		"""Dispatches opening tags to the appropriate handler."""
		try:
			handler = getattr(self, "handle_%s_start" % name)
		except AttributeError as error:
			print(error)
			print("Warning: ignoring unsupported tag %s" % name)
		handler(attrs)

	def endElement(self, name):
		"""Dispatches closing tags to the appropriate handler."""
		try:
			handler = getattr(self, "handle_%s_end" % name)
		except AttributeError as error:
			print(error)
			print("Warning: ignoring unsupported tag %s" % name)
		handler()

	def handle_graphml_start(self, attrs):
		pass

	def handle_graphml_end(self):
		pass

	def handle_graph_start(self, attrs):
		"""Creates a new node and puts it on the stack."""
		# create the new graph
		self.current_graph = Graph()
		# associate it with its id
		self.ids[attrs["id"]] = self.current_graph
		# set the default edge direction
		self.defaults["edgedefault"] = attrs["edgedefault"]
		# add it to the graphs stack
		self.elements.append(self.current_graph)

	def handle_graph_end(self):
		"""Pops the graph off the graph stack."""
		if isinstance(self.elements[-1], Graph):
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_node_start(self, attrs):
		"""Creates a new Node and puts it on the stack."""
		# get the id
		id = attrs["id"]
		# create the node
		node = self.current_graph.add_node(id)
		# associate it with its id
		self.ids[id] = node
		# put it on the stack
		self.elements.append(node)

	def handle_node_end(self):
		"""Ties off the node and removes it from the stack."""
		if isinstance(self.elements[-1], Graph.Node):
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_edge_start(self, attrs):
		"""Creates a new edge and puts it on the stack."""
		# get the edge's id
		id = attrs["id"]
		# get the edge's start and end
		start = self.ids[attrs["source"]]
		end = self.ids[attrs["target"]]
		# verify them
		if not isinstance(start, Graph.Node) or not isinstance(end, Graph.Node):
			raise ParseError("Encountered invalid node ids while parsing edge %s" % id)
		# get the edge's directed state
		is_directed = attrs.get("directed", self.defaults["edgedefault"])
		# build the edge
		edge = self.current_graph.add_edge(start, end, id, is_directed=is_directed)
		# associate its id with it
		self.ids[id] = edge
		# and push it onto the stack
		self.elements.append(edge)

	def handle_edge_end(self):
		"""Ties off the edge and removes it from the stack."""
		if isinstance(self.elements[-1], Graph.Edge):
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_key_start(self, attrs):
		"""Creates a new key and puts it on the stack."""
		# keys are represented as dictionaries
		key = {'_data_type': 'key'}
		# now, so are attrs
		attrs = dict(attrs.items())
		# with two attributes: id and for
		key["id"] = attrs.pop("id")
		key["for"] = attrs.pop("for")
		# now figure out the other ones
		for k, v in attrs.items():
			if k.startswith("attr."):
				key[k[5:]] = v
		# and put the miserable concoction on the stack
		self.elements.append(key)
		# and into the ids dict
		self.ids[key["id"]] = key

	def handle_key_end(self):
		"""Ties off the key and removes it from the stack."""
		if self.elements[-1]["_data_type"] == "key":
			self.elements.pop()
		else:
			raise ParseError("Invalid closing tag.")

	def handle_data_start(self, attrs):
		"""Creates a new data structure and puts it onto the stack."""
		data = {}
		key_id = attrs["key"]
		data["key"] = self.ids[key_id]
		self.elements.append(data)

	def handle_data_end(self):
		"""Ties off the data structure and removes it from the stack."""
		data = self.elements.pop()
		key = data["key"]
		data_name = key["name"]
		data_type = key["type"]
		default_value = key.get("default", False)
		data_value = data.get("default", default_value)
		types = {"obj": loads, "string": str, "boolean": bool, "int": int, "float": float, "double": float, "long": float}
		setattr(self.elements[-1], data_name, types[data_type](data_value))

	def handle_default_start(self, attrs):
		"""Creates a new default and attaches it to the parent key."""
		self.elements[-1]["default"] = None

	def handle_default_end(self):
		"""Ties off the default value."""
		pass

	def handle_desc_start(self):
		"""Creates a new key and puts it on the stack."""
		print("Warning: ignoring description")

	def handle_desc_end(self):
		"""Ties off the key and removes it from the stack."""
		print("Warning: ignoring description")

	def characters(self, data):
		"""If valid, associates the characters with the last element on the stack."""
		try:
			data = data.strip()
			if data:
				self.elements[-1]["default"] = data.strip()
		except:
			pass


class Writer:
	"""Generates a GraphML representation of a given graph."""

	def __init__(self, filename, obj_extension=False):
		self.xml = XMLGenerator(open(filename, "w"), "utf-8")
		self.ids = {}
		self.node_keys = {}
		self.edge_keys = {}
		self.nodes = []
		self.type_map = {"str": ("string", str), "float": ("float", str), "int": ("int", str), "bool": ("boolean", lambda b: "1" if b else "0")}
		if obj_extension:
			self.type_map = defaultdict(self.type_map, lambda s: ("obj", pickle.dumps))

	def handle_graph(self, graph):
		# start the document
		self.xml.startDocument()

		# build attributes
		attrs =  {"xmlns": "http://graphml.graphdrawing.org/xmlns",
			  "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
			  "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns"}

		# attach the graphml root element
		attrs = self.xml.startElement("graphml", attrs)

		# accumulates all unique node data as threeples of (name, type, "node")
		node_data = set()
		for node in graph.nodes:
			for k, v in node.data.items():
				# get the data type and conversion function
				data_type, converter = self.type_map[str(type(v).__name__)]
				data_threeple = (k, data_type, "node")
				# add the threeple to node_data
				node_data.add(data_threeple)

		# accumulates all unique edge data as threeples of (name, type, "edge")
		edge_data = set()
		for edge in graph.edges:
			for k, v in edge.data.items():
				# get the data type and conversion function
				data_type, converter = self.type_map[str(type(v).__name__)]
				data_threeple = (k, data_type, "edge")
				# add the threeple to edge_data
				edge_data.add(data_threeple)

		# process all threeples into keys and map their (name, type) to their id
		for pos, threeple in enumerate(node_data):
			self.node_keys[(threeple[0], threeple[1])] = self.handle_key(pos, *threeple)
		for pos, threeple in enumerate(edge_data):
			self.edge_keys[(threeple[0], threeple[1])] = self.handle_key(pos, *threeple)

		print(self.node_keys)
		print(self.edge_keys)

		# attach the graph element, with edges directed by default
		self.xml.startElement("graph", {"edgedefault": "directed"})

		# for each node, attach it and record its id
		for pos, node in enumerate(graph.nodes):
			self.nodes.append((node, self.handle_node(pos, node)))

		# for each edge, attach it and record its id
		for pos, edge in enumerate(graph.edges):
			self.handle_edge(pos, edge)

		# close the graph element
		self.xml.endElement("graph")
		# close the graphml element
		self.xml.endElement("graphml")
		# close the document
		self.xml.endDocument()

	def handle_key(self, id, name, var_type, attaches_to):
		# make the id unique to keys by prefixing "k"
		id = "k" + str(id)
		# build the attrs object
		attrs = {"id": id, "for": attaches_to, "attr.name": name, "attr.type": var_type}
		# attach the start tag
		self.xml.startElement("key", attrs)
		# attach the end tag
		self.xml.endElement("key")
		# return the id
		return id

	def handle_data(self, name, value, attaches_to):
		# get the data's type
		t = str(type(value).__name__)
		# find the appropriate key
		if attaches_to == "node": key = self.node_keys[(name, self.type_map[t][0])]
		elif attaches_to == "edge": key = self.edge_keys[(name, self.type_map[t][0])]
		# build the attrs object
		attrs = {"key": key}
		# place the data tag
		self.xml.startElement("data", attrs)
		# place the data
		converter = self.type_map[t][1]
		data = converter(value)
		self.xml.characters(data)
		# place the end tag
		self.xml.endElement("data")

	def handle_node(self, id, node):
		# make the id unique to nodes by prefixing "n"
		id = "n" + str(id)
		# build the attrs object
		attrs = {"id": id}
		# attach the start tag
		self.xml.startElement("node", attrs)
		# for each attribute the node has
		for k, v in node.data.items():
			# write its data
			self.handle_data(k, v, "node")
		# close the tag
		self.xml.endElement("node")
		# return the id
		return id

	def handle_edge(self, id, edge):
		# make the id unique to edges by prefixing "e"
		id = "e" + str(id)
		# find the start and end ids
		start = None
		end = None
		for node, id in self.nodes:
			if node == edge.start:
				start = id
			if node == edge.end:
				end = id
		# determine if it is directional
		if edge.is_directed: directed="true"
		else: directed="false"
		# build the attrs object
		attrs = {"id": id, "source": start, "target": end, "directed": directed}
		# attach the start tag
		self.xml.startElement("edge", attrs)
		# for each attribute the edge has
		for k, v in edge.data.items():
			# write the data
			self.handle_data(k, v, "edge")
		# close the tag
		self.xml.endElement("edge")
		# return the id
		return id


def load(filename):
	"""Loads a graph from a GraphML file specified by filename."""
	r = Reader()
	parse(open(filename), r)
	return r.current_graph

def store(graph, filename, obj_extension=False):
	"""Writes a graph to the file given by filename in GraphML.

	The optional argument obj_extension indicates whether to use
	the object extension, which stores arbitrary Python objects
	via pickle if a Java type does not exist to handle it.
	"""
	w = Writer(filename, obj_extension=obj_extension)
	w.handle_graph(graph)
