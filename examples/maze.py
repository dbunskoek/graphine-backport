#! /usr/bin/env python3

import random

from graph.base import Graph

NUM_ROOMS = 25
NUM_DOORS = 4

def build_maze():
	"""Creates the maze."""
	maze = Graph()
	# add the player's starting positions and the end
	p1_start = maze.add_node(name="p1_start")
	p2_start = maze.add_node(name="p2_start")
	end = maze.add_node(name="END")
	# create a list of connected components
	nodes = [[p1_start], [p2_start], [end]]
	# add all the rooms, making each its own component
	for i in range(NUM_ROOMS):
		nodes.append([maze.add_node(name=i)])
	# while some components are unconnected
	while len(nodes) > 1:
		# choose two components at random
		component_1, component_2 = random.sample(list(nodes), 2)
		# and one node from each component
		node_1 = random.choice(component_1)
		node_2 = random.choice(component_2)
		# and if they don't have too many doors...
		if len(node_1.outgoing) < NUM_DOORS and len(node_2.outgoing) < NUM_DOORS:
			# connect them
			maze.add_edge(node_1, node_2, is_directed=False)
			# then merge the components
			component_1.extend(component_2)
			nodes.remove(component_2)
	# finally, make sure that the start and end points have doors.
	choices = random.sample(list(maze.nodes), 3)
	if len(p1_start.outgoing) < NUM_DOORS: maze.add_edge(p1_start, choices[0], is_directed=False)
	if len(p2_start.outgoing) < NUM_DOORS: maze.add_edge(p2_start, choices[1], is_directed=False)
	if len(end.outgoing) < NUM_DOORS: maze.add_edge(end, choices[2], is_directed=False)
	return p1_start, p2_start, maze

def ai_path(start, maze):
	"""Defines the AI's heuristic and finds the path it will take."""
	# selector is the selection heuristic that the AI will use
	def selector(candidates):
		best = (0, -1, None)
		for pos, room in enumerate(candidates):
			if room.name == "END": return candidates.pop(pos)
			num_doors = len(room.outgoing)
			if num_doors > best[0]:
				best = (num_doors, pos, room)
		return candidates.pop(best[1])
	# the total distance traveled
	distance = 0
	previous = start
	# traverse the maze, using selector() as your heuristic
	for node in maze.heuristic_traversal(start, selector):
		# take all the steps between dead ends
		distance += maze.get_shortest_paths(previous)[node][0]
		# and end if you're at the end
		if node.name == "END": return distance
		previous = node

def player_select(options):
	"""Prints the player's options and gets their choice."""
	selections = {}
	print("You have %s options:" % (len(options)))
	for pos, option in enumerate(options):
		selections[pos] = option
		print("%d. Room %s, with %s doors" % (pos, option.name, len(option.outgoing)))
	choice = int(input("Which do you want to take? "))
	return selections[choice]
	
def handle_player(start, maze, max_length):
	"""Walks the maze, giving the player the choice of where to go."""
	w = maze.walk_nodes(start)
	# while the AI hasn't beat you and you've got places to go
	print(max_length)
	for adjacent_rooms in w:
		if max_length > 0: max_length -= 1
		else: break
		selection = player_select(adjacent_rooms)
		if selection.name is "END":
			print("You win!")
			return
		w.send(selection)
	# otherwise, lose
	print("You lose!")

if __name__ == "__main__":
	# build the maze
	p1_start, p2_start, maze = build_maze()
	# run the simulation for the AI
	path_to_beat = ai_path(p1_start, maze)
	# get the player's moves
	handle_player(p2_start, maze, path_to_beat)
