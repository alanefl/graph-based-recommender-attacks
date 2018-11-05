"""Parses movielens data and saves it as an EIGraph"""

import nose.tools as nt
from unittest import TestCase
import snap

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from gbra.util.ei_graph import EIGraph

T = TestCase('__init__')

def main():
    fn = "ml-1m/ratings.dat"
    edges = []
    num_entities = 6040
    num_items = 3952
    num_edges = 1000209

    with open(fn) as fin:
        for line in fin:
            sline = line.strip().split('::')
            user_id = int(sline[0])
            movie_id = int(sline[1])
            T.assertTrue(user_id >= 1 and user_id <= num_entities, user_id)
            T.assertTrue(movie_id >= 1 and movie_id <= num_items, movie_id)
            edges.append((user_id, movie_id))

    T.assertEqual(len(edges), num_edges)

    graph = EIGraph()
    user_to_entity = {}
    movie_to_item = {}

    for e in xrange(1, num_entities+1):
        eid = graph.add_entity()
        user_to_entity[e] = eid

    for i in xrange(1, num_items+1):
        iid = graph.add_item()
        movie_to_item[i] = iid

    for user_id, movie_id in edges:
        entity_id = user_to_entity[user_id]
        item_id = movie_to_item[movie_id]
        graph.add_edge(entity_id, item_id)

    T.assertEqual(graph.num_entities, num_entities)
    T.assertEqual(graph.num_items, num_items)
    T.assertEqual(graph.base().GetNodes(), num_entities+num_items)
    T.assertEqual(graph.base().GetEdges(), num_edges)

    graph.save('movielens.graph')

if __name__ == '__main__':
    main()
