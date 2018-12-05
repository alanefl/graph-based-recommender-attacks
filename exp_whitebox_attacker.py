import unittest

from gbra.data.network_loader import MovielensLoader
from gbra.attackers.attacker import WhiteBoxAttacker
from gbra.recommender.recommenders import PixieRandomWalkRecommender

T = unittest.TestCase('__init__')

print "WhiteBoxAttack on TinyTest sanity check"

network = MovielensLoader().load()
recommender = PixieRandomWalkRecommender(
    n_p=30, n_v=4, G=network, num_steps_in_walk=200, alpha=0.25
)

# Target item to popularize
[target_item] = network.get_random_items(1)

# Initializer attacker
attacker = WhiteBoxAttacker(recommender, target_item, 4, 3)

# print "Hit ratio before attack %f" % recommender.calculate_hit_ratio(target_item, 3, verbose = True)

# Attack
attacker.attack()

# print "Hit ratio after attack %f" % recommender.calculate_hit_ratio(target_item, 3, verbose = True)
