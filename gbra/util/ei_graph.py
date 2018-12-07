"""Defines a general-purpose Entity-Item graph object."""

import marshal
import numpy as np
import random
import snap
import numpy as np

from gbra.util.math_utils import weighted_choice

class EIGraph(object):
    """An Entity-Item Graph.

    This class provides a simpler interface and some utilities
    for handling Entity-Item graphs.

    The underlying representation is a SNAP undirected graph (TUNGraph).
    One can obtain the Snappy graph object by calling `ei_graph.base()`.

    In an EIGraph, an entity is an odd-number node (starting at 1)
    and an item is an even-numbered node (starting at 2), in the
    underlying TUNGraph.
    """

    def __init__(self, num_entities=0,
            num_items=0, rating_range=(0, 5), possible_ratings=[0, 1, 2, 3, 4, 5]):
        self._G = snap.TUNGraph.New()
        self.num_entities = 0
        self.num_items = 0
        self.name = None
        self.items = []
        self.entities = []
        self.rating_range = rating_range
        self.possible_ratings = possible_ratings

        for _ in xrange(num_entities):
            self.add_entity()

        for _ in xrange(num_items):
            self.add_item()

        self._weights = {}  # (entity, item) -> weight

    def base(self):
        """Returns the underlying snap TUNGraph."""
        return self._G

    def get_name(self):
        """Returns name of the graph."""
        return self.name

    def add_entity(self):
        """Adds an entity and returns that entity's ID."""
        new_id = self.num_entities * 2 + 1
        self._G.AddNode(new_id)
        self.num_entities += 1
        self.entities.append(new_id)
        return new_id

    def add_item(self):
        """Adds an item and returns that entity's ID."""
        new_id = (self.num_items + 1) * 2
        self._G.AddNode(new_id)
        self.num_items += 1
        self.items.append(new_id)
        return new_id

    def _order_ei(self, nid1, nid2):
        """Return a tuple (entity, item) from `nid1`, `nid2`."""
        if self.nid_is_entity(nid2):
            return nid2, nid1
        return nid1, nid2

    def add_edge(self, nid1, nid2, weight=1):
        """Adds an edge between nodes with IDs `nid1` and `nid2`.

        :param - weight: (default 1), specifies a weight for the edge
        """
        assert self.nid_is_entity(nid1) != self.nid_is_entity(nid2)
        self._weights[self._order_ei(nid1, nid2)] = weight
        res = self._G.AddEdge(nid1, nid2)
        assert res == -1, res

    def del_edge(self, nid1, nid2):
        """Removes an edge between nodes with IDs `nid1` and `nid2`."""
        assert self.nid_is_entity(nid1) != self.nid_is_entity(nid2)
        del self._weights[self._order_ei(nid1, nid2)]
        self._G.DelEdge(nid1, nid2)

    def is_edge(self, nid1, nid2):
        """Returns whether there is an edge between nodes with IDs `nid1`
        and `nid2`.
        """
        return self._G.IsEdge(nid1, nid2)

    def num_edges(self):
        return self._G.GetEdges()

    def get_edge_weight(self, nid1, nid2):
        """Return the weight of the edge connected `nid1` and `nid2`."""
        assert self.is_edge(nid1, nid2)
        return self._weights[self._order_ei(nid1, nid2)]

    def get_items(self):
        """Returns a set containing the nodeIds
        corresponding to the items in this graph.

        :return: set containing item nodes
        """
        return set(self.items)

    def get_entities(self):
        """Returns a set containing the nodeIds
        corresponding to the entities in this graph.

        :return: set containing entity nodes
        """
        return set(self.entities)

    def get_neighbors(self, node):
        """Returns a list containing the node IDs of the neighbors
        of "node".
        """
        if isinstance(node, int):
            node = self._G.GetNI(node)
        return list(node.GetOutEdges())

    def get_random_edge(self):
        """Returns a random (entity, item, weight) pair whose edge
        exists in the graph.
        """
        if self._G.GetEdges() == 0:
            raise ValueError("Graph has no edges")

        [item] = self.get_random_items(1)
        while self._G.GetNI(item).GetOutDeg() == 0:
            [item] = self.get_random_items(1)

        entity = self.get_random_neighbor(item).GetId()
        return (entity, item, self.get_edge_weight(entity, item))

    def get_random_items(self, N, replace = True, excluding = None):
        """Returns a np.array of items in the graph"""
        if self.num_items == 0:
            raise ValueError("Graph has no items")
        return np.random.choice([i for i in self.get_items() if i != excluding], N, replace)

    def get_random_neighbor(self, node, use_weights=False):
        """Returns a random neighbor of node in this graph as a Snap Node.

        :param Node: can be a snap node or an int ID.
        :param use_weights: If true, weighs the random choice based on the
            weight of the edge between the current node and its neighbors.
            WARNING: This makes the code many times slower.
        """
        neighbors = self.get_neighbors(node)
        if not neighbors:
            raise ValueError("Node has no neighbors")

        if not use_weights:
            return self._G.GetNI(random.choice(neighbors))

        weights = []
        if not isinstance(node, int):
            node = node.GetId()

        weight_sum = 0.0
        for neighbor in neighbors:
            curr_edge_weight = self.get_edge_weight(node, neighbor)
            weight_sum += curr_edge_weight
            weights.append(curr_edge_weight)

        draw = weighted_choice(neighbors, weights, weight_sum)
        return self._G.GetNI(draw)

    def get_average_edge_weight(self, node):
        neighbors = self.get_neighbors(node)
        if len(neighbors) == 0:
            raise ValueError("Zero degree node has no average edge weight")

        weights = [self.get_edge_weight(n, node) for n in neighbors]
        return sum(weights) * 1.0 / len(weights)

    def has_entity(self, entity_id):
        """Returns whether the graph contains the given `entity_id`."""
        assert self.nid_is_entity(entity_id)
        return self._G.IsNode(entity_id)

    def has_item(self, item_id):
        """Returns whether the graph contains the given `item_id`."""
        assert self.nid_is_item(item_id)
        return self._G.IsNode(item_id)

    def has_node(self, node_id):
        """Returns whether the graph contains the given `node_id`."""
        return self._G.IsNode(node_id)

    @staticmethod
    def _get_meta_filename(filename):
        return filename + '.ei_meta'

    def save(self, filename):
        """Save this graph in binary format to the given `filename`.

        In order to store metadata associated with this the EIGraph
        object, we save an extra file, with the name `filename + '.ei_meta'`.
        """
        FOut = snap.TFOut(filename)
        self.base().Save(FOut)
        FOut.Flush()
        meta_fn = self._get_meta_filename(filename)

        with open(meta_fn, 'wb') as fout:
            marshal.dump(self._weights, fout)

    @staticmethod
    def load(filename):
        """Loads an EIGraph from the given `filename` and the possible
        ratings."""
        FIn = snap.TFIn(filename)
        G = snap.TUNGraph.Load(FIn)

        graph = EIGraph()
        graph.name = filename
        graph._G = G
        for node in G.Nodes():
            if EIGraph.nid_is_entity(node.GetId()):
                graph.num_entities += 1
                graph.entities.append(node.GetId())
            else:
                assert EIGraph.nid_is_item(node.GetId())
                graph.num_items += 1
                graph.items.append(node.GetId())

        with open(EIGraph._get_meta_filename(filename), 'rb') as fin:
            graph._weights = marshal.load(fin)
            ratings_set = set()
            for k, v in graph._weights.items():
                ratings_set.add(v)
            possible_ratings = sorted(list(ratings_set))

        # Setup the graph with the range of possible ratings.
        graph.rating_range = (0, 5)
        graph.possible_ratings = possible_ratings

        return graph

    @staticmethod
    def nid_is_entity(node_id):
        """Returns whether a given nid is an entity."""
        return node_id % 2 == 1 and node_id >= 1

    @staticmethod
    def nid_is_item(node_id):
        """Returns whether a given nid is an item."""
        return node_id % 2 == 0 and node_id >= 2
