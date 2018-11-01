"""
Classes and routines for loading SNAP networks
"""

import snap

class NetworkLoader(object):
    """Loads bipartite entity-item network for our research project.

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
