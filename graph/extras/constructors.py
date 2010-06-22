#! /usr/bin/env python

"""
constructors.py

Written by Geremy Condra

Licensed under GPLv3

Released 16 April 2009

This module contains the mechanisms needed to produce special classes
of graphs using Graphine.
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

from graph.base import Graph

def K(n):
	"""Generates a completely connected undirected graph of size n.

	The verticies are numbered [0, n).

	The edges are named after the verticies they connect such that
	an edge connected verticies 1 and 2 is named (1,2).
	"""
	# create the graph
	k = Graph()
	# generate all the nodes
	for i in range(n):
		k.add_node(i)
	# generate all the edges
	for i in range(n):
		for j in range(i+1, n):
			k.add_edge(i, j, (i,j), is_directed=False)
	# return the graph
	return k

def cycle(n, is_directed=True):
	"""Generates a cycle of size n.

	The verticies are numbered [0, n).

	The edges are named after the verticies they connect such that
	an edge connecting verticies 1 and 2 is named (1,2).
	"""
	G = Graph()
	for i in range(n):
		G.add_node(i)
	for i in range(n):
		j = (i + 1) % n
		G.add_edge(i, j, (i,j), is_directed=is_directed)
	return G
