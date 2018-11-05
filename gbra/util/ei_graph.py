"""Defines a general-purpose Entity-Item graph object."""

import random
import snap

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

    def __init__(self, num_entities=0, num_items=0):
        self._G = snap.TUNGraph.New()
        self.num_entities = 0
        self.num_items = 0

        for _ in xrange(num_entities):
            self.add_entity()

        for _ in xrange(num_items):
            self.add_item()

    def base(self):
        """Returns the underlying snap TUNGraph."""
        return self._G

    def add_entity(self):
        """Adds an entity and returns that entity's ID."""
        new_id = self.num_entities * 2 + 1
        self._G.AddNode(new_id)
        self.num_entities += 1
        return new_id

    def add_item(self):
        """Adds an item and returns that entity's ID."""
        new_id = (self.num_items + 1) * 2
        self._G.AddNode(new_id)
        self.num_items += 1
        return new_id

    def add_edge(self, nid1, nid2):
        """Adds an edge between nodes with IDs `nid1` and `nid2`."""
        assert self.nid_is_entity(nid1) != self.nid_is_entity(nid2)
        res = self._G.AddEdge(nid1, nid2)
        assert res == -1, res

    def del_edge(self, nid1, nid2):
        """Removes an edge between nodes with IDs `nid1` and `nid2`."""
        assert self.nid_is_entity(nid1) != self.nid_is_entity(nid2)
        self._G.DelEdge(nid1, nid2)

    def is_edge(self, nid1, nid2):
        """Returns whether there is an edge between nodes with IDs `nid1`
        and `nid2`.
        """
        return self._G.IsEdge(nid1, nid2)

    def get_items(self):
        """Returns a TIntSet containing the nodeIds
        corresponding to the items in this graph.

        :return: TIntSet containing item nodes
        """
        items = snap.TIntSet()
        for node in self._G.Nodes():
            nId = node.GetId()
            if nId % 2 == 0:
                items.AddKey(nId)
        return items

    def get_entities(self):
        """Returns a TIntSet containing the nodeIds
        corresponding to the entities in this graph.

        :return: TIntSet containing entity nodes
        """
        entities = snap.TIntSet()
        for node in self._G.Nodes():
            nId = node.GetId()
            if nId % 2 == 1:
                entities.AddKey(nId)
        return entities

    def get_neighbors(self, node):
        """Returns a list containing the node IDs of the neighbors
        of "node".
        """
        if isinstance(node, int):
            node = self._G.GetNI(node)
        return list(node.GetOutEdges())

    def get_random_neighbor(self, node):
        """Returns a random neighbor of node in this graph as a Snap Node.

        :param Node: can be a snap node or an int ID.
        """
        if isinstance(node, int):
            node = self._G.GetNI(node)
        neighbors = list(node.GetOutEdges())
        if not neighbors:
            raise ValueError("Node has no neighbors")
        return self._G.GetNI(random.choice(neighbors))

    def has_entity(self, entity_id):
        """Returns whether the graph contains the given `entity_id`."""
        assert self.nid_is_entity(entity_id)
        return self._G.IsNode(entity_id)

    def has_item(self, item_id):
        """Returns whether the graph contains the given `item_id`."""
        assert self.nid_is_item(item_id)
        return self._G.IsNode(item_id)

    def save(self, filename):
        """Save this graph in binary format to the given `filename`."""
        FOut = snap.TFOut(filename)
        self.base().Save(FOut)
        FOut.Flush()

    @staticmethod
    def load(filename):
        """Loads an EIGraph from the given `filename`."""
        FIn = snap.TFIn(filename)
        G = snap.TUNGraph.Load(FIn)

        graph = EIGraph()
        graph._G = G
        for node in G.Nodes():
            if EIGraph.nid_is_entity(node.GetId()):
                graph.num_entities += 1
            else:
                assert EIGraph.nid_is_item(node.GetId())
                graph.num_items += 1

        return graph

    @staticmethod
    def nid_is_entity(node_id):
        """Returns whether a given nid is an entity."""
        return node_id % 2 == 1 and node_id >= 1

    @staticmethod
    def nid_is_item(node_id):
        """Returns whether a given nid is an item."""
        return node_id % 2 == 0 and node_id >= 2
