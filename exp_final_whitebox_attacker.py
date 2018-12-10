import traceback
import sys
import numpy as np

from gbra.data.network_loader import Movielens100kLoader
from gbra.attackers.attacker import *
from gbra.recommender.recommenders import PixieRandomWalkRecommender

ITERATIONS = 5

PIXIE_PARAMS = {
    'n_p': 30,
    'n_v': 4,
    'max_steps_in_walk': 1000,
    'alpha': 0.01,
    'beta': 20
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
    'HillClimbingAttacker': HillClimbingAttacker,
    'RandomAttacker': RandomAttacker,
    'AverageAttacker': AverageAttacker,
    'NeighborAttacker': NeighborAttacker,
    'BlackBoxRWRAttacker': BlackBoxRWRAttacker,
    'BlackBoxDeepRWRAttacker': BlackBoxDeepRWRAttacker
}

BLACK_BOX_RWR_NUM_SCOUT_ITEMS = 100

def get_attacker(network, recommender, target_item):
    attacker_klass = attackers[ATTACKER_NAME]
    num_fake_entities = int(PERCENT_FAKE_ENTITIES * network.num_entities)

    kwargs = dict(
        _recommender=recommender,
        _target_item=target_item,
        _num_fake_entities=num_fake_entities,
        _num_fake_ratings=NUM_FAKE_REVIEWS
    )
    if ATTACKER_NAME == 'BlackBoxRWRAttacker':
        kwargs.update(dict(
            _num_items_to_scout=BLACK_BOX_RWR_NUM_SCOUT_ITEMS,
            _num_recs=RECOMMENDATIONS
        ))
    elif ATTACKER_NAME == 'BlackBoxDeepRWRAttacker':
        kwargs.update(dict(
            _num_items_to_scout=BLACK_BOX_RWR_NUM_SCOUT_ITEMS,
        ))

    return attacker_klass(**kwargs)

def evaluate_attacker(target_item):
    network = Movielens100kLoader().load()

    recommender = PixieRandomWalkRecommender(G=network, **PIXIE_PARAMS)
    attacker = get_attacker(network, recommender, target_item)

    # before = recommender.calculate_hit_ratio(target_item, RECOMMENDATIONS, verbose=False)
    before = 0  # this is basically always true
    try:
        attacker.attack()
    except:
        traceback.print_exc()
    after = recommender.calculate_hit_ratio(target_item, RECOMMENDATIONS, verbose=False)
    return (before, after)

results = []
network = Movielens100kLoader().load()
# target_items = network.get_random_items(ITERATIONS)
# print target_items
target_items = [2352, 380, 1722, 2514, 2384]

for i in range(ITERATIONS):
    print i
    (before, after) = evaluate_attacker(target_items[i])
    results.append((before, after))
print results

arr = np.array([a[1] for a in results])
print "mean: {}, median {}, std dev {}".format(np.mean(arr), np.median(arr), np.std(arr))
