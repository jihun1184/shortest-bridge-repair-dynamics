"""Tiny local subset used only by frozen finite_window_classification.py.

This avoids adding a runtime dependency for the two operations needed to
construct disconnected Q2/Q3 occupancy masks.
"""

from __future__ import annotations

import itertools


class Graph:
    def __init__(self, adjacency=None):
        self.adjacency = {
            node: set(neighbors) for node, neighbors in (adjacency or {}).items()
        }

    def nodes(self):
        return self.adjacency.keys()

    def subgraph(self, nodes):
        nodes = set(nodes)
        return Graph(
            {
                node: self.adjacency.get(node, set()) & nodes
                for node in nodes
            }
        )


def hypercube_graph(dimension):
    nodes = tuple(itertools.product((0, 1), repeat=dimension))
    adjacency = {node: set() for node in nodes}
    for node in nodes:
        for axis in range(dimension):
            neighbor = list(node)
            neighbor[axis] ^= 1
            adjacency[node].add(tuple(neighbor))
    return Graph(adjacency)


def is_connected(graph):
    nodes = set(graph.adjacency)
    if not nodes:
        raise ValueError("connectivity is undefined for the null graph")
    reached = set()
    stack = [next(iter(nodes))]
    while stack:
        node = stack.pop()
        if node in reached:
            continue
        reached.add(node)
        stack.extend(graph.adjacency[node] - reached)
    return reached == nodes
