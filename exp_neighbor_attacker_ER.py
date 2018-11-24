import unittest

from gbra.data.network_loader import MovielensLoader
from gbra.attackers.attacker import NeighborAttacker
from gbra.recommender.recommenders import PixieRandomWalkRecommender

T = unittest.TestCase('__init__')

print "NeighborAttack on ErdosRenyi sanity check"

er_network = MovielensLoader().load()
recommender = PixieRandomWalkRecommender(
    n_p=30, n_v=4, G=er_network, num_steps_in_walk=200, alpha=0.25
)
initial_entities = er_network.num_entities
initial_items = er_network.num_items
initial_edges = er_network.num_edges()

# Target item to popularize
[target_item] = er_network.get_random_items(1)

# Initializer attacker
neighbor_attacker = NeighborAttacker(recommender, target_item, 25, 1)

print "Hit ratio before attack %f" % recommender.calculate_hit_ratio(target_item, 5, verbose = True)

# Attack
neighbor_attacker.attack()

T.assertEqual(er_network.num_entities, initial_entities + 25)
T.assertEqual(er_network.num_items, initial_items)
# T.assertEqual(er_network.num_edges(), initial_edges + 75)

print "Hit ratio after attack %f" % recommender.calculate_hit_ratio(target_item, 5, verbose = True)
