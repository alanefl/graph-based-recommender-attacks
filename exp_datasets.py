
import unittest

from gbra.data.network_loader import *

T = unittest.TestCase('__init__')

def print_basic_stats(name, graph):
    print name
    print 'Entities: {}'.format(graph.num_entities)
    print 'Items:    {}'.format(graph.num_items)
    print 'Edges:    {}'.format(graph.base().GetEdges())

graph = MovielensLoader().load()
print_basic_stats('Movielens', graph)

graph = BeeradvocateLoader().load()
print_basic_stats('BeerAdvocate', graph)
