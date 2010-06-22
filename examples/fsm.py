#! /usr/bin/env python3

from graph.base import Graph
import sys

def walk_fsm(data):
	fsm = Graph()
	fsm.add_edge("consume_one", "loop_on_zero", consumes="1", accept=False)
	fsm.add_edge("loop_on_zero", "loop_on_zero", consumes="0", accept=False)
	fsm.add_edge("loop_on_zero", "end_with_one", consumes="1", accept=True)
	accept = False
	w = fsm.walk_path("consume_one")
	for edges in w:
		try:
			next = {e.consumes: e for e in edges}[data.pop(0)]
			accept = next.accept
			w.send(next)
		except:
			return False
	return accept and not data


if __name__ == "__main__":
	accept = walk_fsm(list(sys.argv[1]))
	if accept: print("Accepted!")
	else: print("Not accepted!")
