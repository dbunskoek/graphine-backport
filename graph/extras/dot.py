#! /usr/bin/env python

"""
dot.py

Written by Geremy Condra

Licensed under GPLv3

Released 16 April 2009

This module contains the mechanisms needed to produce dot files
using Graphine.
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

def node_properties(n):
	"""Returns default properties for nodes adjusted by the contents of n."""
	defaults = {"label": n.name, "color": "black", "shape": "circle", "style": "filled", "fillcolor": "white"}
	data = n.data
	for k in defaults:
		try: defaults[k] = data[k]
		except: pass
	return defaults

def edge_properties(e):
	"""Returns default properties for edges adjusted by the contents of e."""
	defaults = {"label": "'" + str(e.name) + "'", "color": "black", "style": None}
	data = e.data
	for k in defaults:
		if k in data:
			defaults[k] = data[k]
	if defaults["style"] == None: defaults.pop("style")
	return defaults


class DotGenerator:

	"""This produces dot files for compatibility with other graph libraries."""

	def __init__(self, node_property_getter=node_properties, edge_property_getter=edge_properties, is_directed=True):
		"""Sets the general properties of the graph and how to get node and edge labels."""
		self.get_node_properties = node_property_getter
		self.get_edge_properties = edge_property_getter
		self.is_directed = is_directed

	def draw(self, graph, name):

		doc = ""

		if self.is_directed:
			doc += "digraph %s {\n" % name
			edge_marker = " -> "
		else:
			doc += "graph %s {\n" % name
			edge_marker = " -- "

		for node in graph.nodes:
			node_properties = self.get_node_properties(node)
			property_strings = []
			for k, v in node_properties.items():
				property_strings.append("%s=%s" % (k, v))
			property_strings = str(property_strings).replace("'", "")
			doc += "\t%s %s\n" % (node_properties["label"], property_strings)

		for edge in graph.edges:
			start = edge.start
			end = edge.end
			start_label = self.get_node_properties(start)["label"]
			end_label = self.get_node_properties(end)["label"]
			edge_properties = self.get_edge_properties(edge)
			property_strings = []
			for k, v in edge_properties.items():
				property_strings.append("%s=%s" % (k, v))
			property_strings = str(property_strings).replace("'", "")
			edge_string = "\t%s %s %s %s\n"
			edge_string %= (start_label, edge_marker, end_label, property_strings)
			doc += edge_string

		doc += "}"

		return doc
