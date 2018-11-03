
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
print sys.path
from gbra.util.ei_graph import EIGraph

class TestEIGraph(unittest.TestCase):

    def test_basic(self):
        n_ents = 10
        n_items = 20
        G = EIGraph(n_ents, n_items)
        self.assertEqual(G.get_items().Len(), n_items)
        self.assertEqual(G.get_entities().Len(), n_ents)

        for i in G.get_items():
            self.assertTrue(EIGraph.nid_is_item(i))

        for e in G.get_entities():
            self.assertTrue(EIGraph.nid_is_entity(e))

        G.add_edge(1, 2)

        self.assertEqual(1, G.base().GetEdges())

if __name__ == '__main__':
    unittest.main()
