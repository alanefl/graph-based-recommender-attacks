import unittest

from gbra.data.network_loader import TinyTestLoader
from gbra.attackers.attacker import AverageAttacker
from gbra.recommender.recommenders import BasicRandomWalkRecommender

T = unittest.TestCase('__init__')

print "AverageAttack on TinyTest sanity check"

tiny_network = TinyTestLoader().load()
recommender = BasicRandomWalkRecommender(
    tiny_network, num_steps_in_walk=50, alpha=0.25
)
initial_entities = tiny_network.num_entities
initial_items = tiny_network.num_items
initial_edges = tiny_network.num_edges()

# Target item to popularize
[target_item] = tiny_network.get_random_items(1)

# Initializer attacker
average_attacker = AverageAttacker(recommender, target_item, 4, 3)

print "Hit ratio before attack %f" % recommender.calculate_hit_ratio(target_item, 3, verbose = True)

# Attack
average_attacker.attack()

T.assertEqual(tiny_network.num_entities, initial_entities + 4)
T.assertEqual(tiny_network.num_items, initial_items)
T.assertEqual(tiny_network.num_edges(), initial_edges + 12)

print "Hit ratio after attack %f" % recommender.calculate_hit_ratio(target_item, 3, verbose = True)
