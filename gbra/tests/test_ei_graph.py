
import tempfile
import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from gbra.util.ei_graph import EIGraph

class TestEIGraph(unittest.TestCase):

    def test_basic(self):
        n_ents = 10
        n_items = 20
        graph = EIGraph(n_ents, n_items)
        self.assertEqual(len(graph.get_items()), n_items)
        self.assertEqual(len(graph.get_entities()), n_ents)

        for i in graph.get_items():
            self.assertTrue(EIGraph.nid_is_item(i))

        for e in graph.get_entities():
            self.assertTrue(EIGraph.nid_is_entity(e))

        graph.add_edge(1, 2)
        self.assertEqual(1, graph.base().GetEdges())

        graph.add_edge(1, 4, weight=2)
        self.assertEqual(2, graph.get_edge_weight(1, 4))
        self.assertEqual(2, graph.get_edge_weight(4, 1))

    def test_save_load(self):
        graph = EIGraph(2, 2)
        graph.add_edge(1, 2)
        graph.add_edge(1, 4)
        graph.add_edge(3, 2, 2)

        with tempfile.NamedTemporaryFile(delete=True) as temp_f:
            graph.save(temp_f.name)
            graph = EIGraph.load(temp_f.name)

        self.assertEqual(graph.num_entities, 2)
        self.assertEqual(graph.num_items, 2)
        self.assertTrue(graph.is_edge(1, 2))
        self.assertTrue(graph.is_edge(1, 4))
        self.assertTrue(graph.is_edge(3, 2))
        self.assertTrue(graph.base().GetNodes(), 4)
        self.assertEqual(2, graph.get_edge_weight(3, 2))

if __name__ == '__main__':
    unittest.main()
