
import unittest

from gbra.data.network_loader import MovielensLoader

T = unittest.TestCase('__init__')

graph = MovielensLoader().load()
T.assertEqual(graph.num_entities, 6040)
T.assertEqual(graph.num_items, 3952)

# verify some example ratings
T.assertEqual(graph.get_edge_weight(1, 1193*2), 5)
T.assertEqual(graph.get_edge_weight(1, 661*2), 3)
T.assertEqual(graph.get_edge_weight(3, 1213*2), 2)
