"""Runs evaluation experiments recommenders, as used in the project milestone."""

import time
import sys

from gbra.recommender.recommenders import RandomRecommender, PopularItemRecommender, \
    PixieRandomWalkRecommender
from gbra.recommender.evaluator import RecEvaluator
from gbra.data.network_loader import *

def get_graph(name):
    name = name.lower()
    if name == "movielens":
        return MovielensLoader().load()
    elif name == "beeradvocate":
        return BeeradvocateLoader().load()
    elif name.startswith("erdosrenyi"):
        _, entities, items, edges = name.split("_")
        entities, items, edges = int(entities), int(items), int(edges)
        return ErdosRenyiLoader(
            num_entities=entities, num_items=items, num_edges=edges
        ).load()
    else:
        raise ValueError("Unknown graph %s" % name)

# Experiment-wide variables. These are fixed across all experiments.

# For Pixie.
STEPS_IN_RANDOM_WALK = 30
N_P = 20
N_V = 4
ALPHA = 0.20

# For popular Items
NUM_POPULAR_ITEMS = 1000

def get_recommender(name, graph):
    name = name.lower()
    if name == "random":
        return RandomRecommender(graph)
    elif name == "popular":
        return PopularItemRecommender(graph, num_popular_items=NUM_POPULAR_ITEMS)
    elif name == "pixie":
        return PixieRandomWalkRecommender(
            n_p=N_P, n_v=N_V, G=graph, num_steps_in_walk=STEPS_IN_RANDOM_WALK, alpha=ALPHA
        )
    else:
        raise ValueError("Unknown recomender %s" % name)

def evaluate_recommender(graph, name, recommender, recommender_name, \
                        num_recs, entity_sample_size):

    evaluator = RecEvaluator(recommender, num_recs=num_recs, verbose=False)

    # Run this quickly so that we don't lose experiment output.
    for iter in range(entity_sample_size):
        score = evaluator.evaluate_random_sample(entity_sample_size=entity_sample_size)
        print("graph:%s,num_recs:%s,score:%s,rec:%s,iter:%d" % (
            name, str(num_recs), str(score), recommender_name, iter
        ))

# Start experiment
_, graph_name, recommender_name, k_recs, N = sys.argv

k_recs = int(k_recs)
N = int(N)
G = get_graph(graph_name)
R = get_recommender(recommender_name, G)

evaluate_recommender(G, graph_name, R, recommender_name, k_recs, N)
