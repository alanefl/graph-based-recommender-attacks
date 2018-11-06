"""Parses beeradvocate data and saves it as an EIGraph.

Notes:
- for users that remove a single beer more than once, we
    take their average rating.
"""

from collections import defaultdict
import nose.tools as nt
from unittest import TestCase
import snap

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from gbra.util.ei_graph import EIGraph

T = TestCase('__init__')

def main():
    fn = "Beeradvocate.txt"
    ratings = defaultdict(list)  # user, beer -> list of ratings
    num_entities = 33387
    num_items = 66051
    num_edges = 1571251

    with open(fn) as fin:
        beer_id = None
        user_name = None
        rating = None

        user_to_uid = {}
        beer_ids = set()

        for line in fin:
            sline = line.strip().split(': ')
            if len(sline) < 2:
                continue

            key = sline[0]
            value = sline[1]

            if key == 'beer/beerId':
                beer_id = value
            elif key == 'review/profileName':
                user_name = value
            elif key == 'review/overall':
                rating = float(value)
                T.assertTrue(rating >= 0 and rating <= 5, rating)

            if beer_id and user_name and rating:
                if user_name not in user_to_uid:
                    uid = len(user_to_uid)
                    user_to_uid[user_name] = uid
                else:
                    uid = user_to_uid[user_name]
                beer_ids.add(beer_id)
                ratings[(uid, beer_id)].append(rating)

                beer_id = None
                user_name = None
                rating = None

    T.assertEqual(len(ratings), num_edges)

    graph = EIGraph()
    user_to_entity = {}
    movie_to_item = {}

    for uid in user_to_uid.itervalues():
        eid = graph.add_entity()
        user_to_entity[uid] = eid

    for i in beer_ids:
        iid = graph.add_item()
        movie_to_item[i] = iid

    for (user_id, beer_id), ratings in ratings.iteritems():
        entity_id = user_to_entity[user_id]
        item_id = movie_to_item[beer_id]
        avg_rating = sum(ratings) / len(ratings)
        graph.add_edge(entity_id, item_id, weight=avg_rating)

    T.assertEqual(graph.num_entities, num_entities)
    T.assertEqual(graph.num_items, num_items)
    T.assertEqual(graph.base().GetNodes(), num_entities+num_items)
    T.assertEqual(graph.base().GetEdges(), num_edges)

    graph.save('beeradvocate.dat')

if __name__ == '__main__':
    main()
