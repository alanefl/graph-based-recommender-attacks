"""
Classes and routines for loading SNAP networks
"""

import snap
import random

class NetworkLoader(object):
    """Loads bipartite entity-item network for our research project.

    Can also load an Erdos-Renyi bipartite graph.

    Enforces the condition that entities have ODD ids and items have
    EVEN ids.
    """

    def _load_tiny_test_network(self):
        """Returns a very simple undirected network with unweighted edges:

        Entity -> Items
        1 -> [2, 4, 6]
        3 -> [8]
        5 -> [4, 8]
        7 -> [6, 8, 10]
        9 -> [2, 10]
        11 -> [10]

        """
        G = snap.TUNGraph.New()
        for i in range(1, 12):
            G.AddNode(i)

        G.AddEdge(1, 2)
        G.AddEdge(1, 4)
        G.AddEdge(1, 6)
        G.AddEdge(3, 2)
        G.AddEdge(5, 4)
        G.AddEdge(5, 8)
        G.AddEdge(7, 6)
        G.AddEdge(7, 8)
        G.AddEdge(7, 10)
        G.AddEdge(9, 2)
        G.AddEdge(9, 10)
        G.AddEdge(11, 10)

        return G

    def load_network(self, name):
        name = name.lower()
        if name == "tiny_test":
            return self._load_tiny_test_network()
        else:
            raise ValueError("Network name %s unknown.")

    def get_erdos_renyi_bipartite_graph(self, num_entities, num_items, num_edges):
        """
        :param - num_entities: number of entities to include
        :param - num_items: number of items to include
        :param - num_edges: the number of edges desired.

        TODO: this will take a long time if num_edges is close
        to num_items/num_entities. If we need to make graphs like this in
        the future, please update my logic :)

        return type: snap.PUNGraph
        return: Erdos-Renyi graph bipartite graph with NUM_ENTITIES,
                NUM_ITEMS, and NUM_EDGES chosen uniformly at random between
                entities and items.
        """
        if num_edges > num_entities * num_items:
            raise ValueError("More edges requested than possible.")

        Graph = snap.TUNGraph.New()
        for i in range(num_entities):
            Graph.AddNode(2 * i + 1)

        for i in range(num_items):
            Graph.AddNode(2 * i)

        edges_left = num_edges
        while edges_left > 0:
            entity_node_id = 2 * random.randint(0, num_entities - 1) + 1
            item_node_id = 2 * random.randint(0, num_items - 1)
            if not Graph.IsEdge(entity_node_id, item_node_id):
                edges_left -= 1
                Graph.AddEdge(entity_node_id, item_node_id)

        return Graph
