import sys

from gbra.data.network_loader import Movielens100kLoader
from gbra.attackers.attacker import *
from gbra.recommender.recommenders import PixieRandomWalkRecommender

ITERATIONS = 10

PIXIE_PARAMS = {
    'n_p': 30,
    'n_v': 4,
    'num_steps_in_walk': 1000,
    'alpha': 0.01
}
RECOMMENDATIONS = 10

""""
python exp_final_whitebox_attacker.py 0.10 10 HighDegreeAttacker
"""

PERCENT_FAKE_ENTITIES, NUM_FAKE_REVIEWS, ATTACKER_NAME = sys.argv[1:]
PERCENT_FAKE_ENTITIES = float(PERCENT_FAKE_ENTITIES)
NUM_FAKE_REVIEWS = int(NUM_FAKE_REVIEWS)

attackers = {
    'HighDegreeAttacker': HighDegreeAttacker,
    'LowDegreeAttacker': LowDegreeAttacker,
    'HillClimbingAttacker': HillClimbingAttacker
}

def get_attacker(network, recommender, target_item):
    attacker_klass = attackers[ATTACKER_NAME]
    num_fake_entities = int(PERCENT_FAKE_ENTITIES * network.num_entities)
    return attacker_klass(recommender, target_item, num_fake_entities, NUM_FAKE_REVIEWS)

def evaluate_attacker():
    network = Movielens100kLoader().load()

    # Target item to popularize
    [target_item] = network.get_random_items(1)

    recommender = PixieRandomWalkRecommender(G=network, **PIXIE_PARAMS)
    attacker = get_attacker(network, recommender, target_item)

    before = recommender.calculate_hit_ratio(target_item, RECOMMENDATIONS)
    attacker.attack()
    after = recommender.calculate_hit_ratio(target_item, RECOMMENDATIONS)
    return (before, after)

results = []
for i in range(ITERATIONS):
    results.append(evaluate_attacker())
print results
