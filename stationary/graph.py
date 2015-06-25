"""
Labeled and weighted graph class for Markov simulations. Not a full-featured
class, rather an appropriate organizational data structure for handling various
Markov process calculations.
"""

import random

class Graph(object):
    """Directed graph object intended for the graph associated to a Markov process.
    Gives easy access to the neighbors of a particular state needed for various
    calculations.

    Vertices can be any hashable / immutable python object.
    """

    def __init__(self):
        self._vertices = set()
        self._edges = []

    def add_vertex(self, label):
        self._vertices.add(label)

    def add_edge(self, source, target, weight=1.):
        for vertex in [source, target]:
            if vertex not in self._vertices:
                self._vertices.add(vertex)
        self._edges.append((source, target, weight))

    def add_edges(self, edges):
        try:
            for source, target, weight in edges:
                self.add_edge(source, target, weight)
        except ValueError:
            for source, target in edges:
                self.add_edge(source, target, 1.0)

    def vertices(self):
        """Returns the set of vertices of the graph."""
        return self._vertices

    def out_dict(self, source):
        """Returns a dictionary of the outgoing edges of source with weights."""
        return dict([(t, v) for s, t, v in self._edges if s == source])

    def out_vertices(self, source):
        """Returns a list of the outgoing vertices."""
        return [t for s, t, v in self._edges if s == source]

    def in_dict(self, target):
        """Returns a dictionary of the incoming edges of source with weights."""
        return dict([(s, v) for s, t, v in self._edges if t == target])

    def normalize_weights(self):
        """Normalizes the weights coming out of each vertex to be probability
        distributions."""
        new_edges = []
        for source in self.vertices():
            out_edges = [(s, t, v) for s, t, v in self._edges if s == source]
            total = sum(v for (s, t, v) in out_edges) 
            for s, t, v in out_edges:
                new_edges.append((s,t,v/total))
        self._edges = new_edges


class RandomGraph(object):
    """Random Graph class in which there is a probability p of an edge between any two vertices. Edge existence is drawn on each request (i.e. not determined once at initiation)."""
    def __init__(self, num_vertices, p):
        self._vertices = list(range(num_vertices))
        self.p = p

    def vertices(self):
        return self._vertices

    def out_vertices(self, source):
        outs = []
        for v in self._vertices:
            q = random.random()
            if q <= self.p:
                outs.append(v)
        return outs

    def in_vertices(self, source):
        ins = []
        for v in self._vertices:
            q = random.random()
            if q <= self.p:
                ins.append(v)
        return ins
