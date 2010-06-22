#! /usr/bin/env python3

import sys
import os.path
from html.parser import HTMLParser

from graph.base import Graph

G = Graph()

class UrlGetter(HTMLParser):
	"""Extracts all the links from the given html"""
	links = None
	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if tag == "a":
			href = attrs.get("href", False)
			if href:
				if not self.links:
					self.links = []
				self.links.append(href)


def get_urls(filename):
	"""Extracts all the links from the given file."""
	parser = UrlGetter()
	txt = str(open(filename).read())
	parser.feed(txt)
	parser.close()
	return parser.links

if __name__ == "__main__":
	
	# get the starting point
	start = sys.argv[1]

	# get the files we're interested in
	files = sys.argv[1:]

	# build the pagename -> node mappings
	nodes = {}

	# add nodes
	nodes[start] = G.add_node(name=start)
	for f in files:
		nodes[f] = G.add_node(name=f)

	# get all their links
	for f1 in files:
		links = get_urls(f1)
		# filter them against the files list
		for link in links:
			for f2 in files:
				if link == f2:
					try: G.add_edge(nodes[f1], nodes[f2])
					except: pass

	# get the shortest paths
	shortest_paths = G.get_shortest_paths(nodes[start], lambda e: 1)

	# print the results
	for node, path in shortest_paths.items():
		print("The shortest path from %s to %s is %d clicks" % (start, node.name, path[0]))
