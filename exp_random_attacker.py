import unittest

from gbra.data.network_loader import TinyTestLoader
from gbra.attackers.attacker import RandomAttacker
from gbra.recommender.recommenders import BasicRandomWalkRecommender

T = unittest.TestCase('__init__')

tiny_network = TinyTestLoader().load()
recommender = BasicRandomWalkRecommender(
    tiny_network, num_steps_in_walk=50, alpha=0.25
)

# Target item to popularize
[target_item] = tiny_network.get_random_items(1)

# Initializer attacker
random_attacker = RandomAttacker(recommender, target_item, 4, 3, 2)

# Attack
random_attacker.attack()