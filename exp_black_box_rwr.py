import unittest
T = unittest.TestCase('__init__')

from gbra.recommender.recommenders import PixieRandomWalkRecommender
from gbra.attackers.attacker import BlackBoxRWRAttacker
from gbra.data.network_loader import Movielens100kLoader

graph = Movielens100kLoader().load()

initial_entities = graph.num_entities
initial_items = graph.num_items
initial_edges = graph.num_edges()

STEPS_IN_RANDOM_WALK = 1000
N_P = 20
N_V = 4
ALPHA = 0.01
BETA = 20
recommender = PixieRandomWalkRecommender(
    n_p=N_P, n_v=N_V, G=graph, max_steps_in_walk=STEPS_IN_RANDOM_WALK, alpha=ALPHA,
    beta=BETA
)

[target_item] = graph.get_random_items(1)
bb_rwr_attacker = BlackBoxRWRAttacker(
    _num_items_to_scout=100, _num_recs=10, _recommender=recommender,
    _target_item=target_item, _num_fake_entities=10, _num_fake_ratings=1
)

NUM_RECS = 10

# print "Hit ratio before attack", recommender.calculate_hit_ratio(target_item, NUM_RECS, verbose = True)
bb_rwr_attacker.attack()
T.assertEqual(graph.num_entities, initial_entities + 11)
T.assertEqual(graph.num_items, initial_items)
T.assertEqual(graph.num_edges(), initial_edges + 20)
print "Hit ratio after attack", recommender.calculate_hit_ratio(target_item, NUM_RECS, verbose = True)