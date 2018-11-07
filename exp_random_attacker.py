import unittest

from gbra.data.network_loader import TinyTestLoader
from gbra.attackers.attacker import RandomAttacker
from gbra.recommender.recommenders import BasicRandomWalkRecommender

T = unittest.TestCase('__init__')

tiny_network = TinyTestLoader().load()
recommender = BasicRandomWalkRecommender(
    tiny_network, num_steps_in_walk=50, alpha=0.25
)
initial_entities = tiny_network.num_entities
initial_edges = tiny_network.num_edges()

# Target item to popularize
[target_item] = tiny_network.get_random_items(1)

# Initializer attacker
random_attacker = RandomAttacker(recommender, target_item, 4, 3, 2)

# Attack
random_attacker.attack()

T.assertEqual(tiny_network.num_entities, initial_entities + 4)
T.assertEqual(tiny_network.num_edges(), initial_edges + 12)