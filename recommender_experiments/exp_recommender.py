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
        _, entities, items, edges, graph_to_emulate_name = name.split("_")
        assert(graph_to_emulate_name != "erdosrenyi")
        entities, items, edges = int(entities), int(items), int(edges)
        graph_to_emulate = get_graph(graph_to_emulate_name)
        return ErdosRenyiLoader(
            num_entities=entities,
            num_items=items,
            num_edges=edges,
            graph_to_emulate=graph_to_emulate
        ).load()
    else:
        raise ValueError("Unknown graph %s" % name)

# Experiment-wide variables. These are fixed across all experiments.

# For Pixie.
STEPS_IN_RANDOM_WALK = 1000
N_P = 20
N_V = 4

# In expectation, each random walk is of length 10,
# but you can get up to 30 in some cases.
# Reasonable, because the diameter of the graphs are about 8.
ALPHA = 0.01
BETA = 20

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
            n_p=N_P, n_v=N_V, G=graph, max_steps_in_walk=STEPS_IN_RANDOM_WALK, alpha=ALPHA,
            beta=BETA
        )
    else:
        raise ValueError("Unknown recomender %s" % name)

def evaluate_recommender(graph, name, recommender, recommender_name, \
                        num_recs, entity_sample_size, min_score_threshold):

    evaluator = RecEvaluator(
        recommender,
        min_score_threshold=min_score_threshold,
        num_recs=num_recs,
        verbose=False
    )

    # Run this quickly so that we don't lose experiment output.

    scores_to_go = entity_sample_size
    while scores_to_go > 0:

        # For each iteration, only sample 1 entity and evaluate it.
        score = evaluator.evaluate_random_sample(entity_sample_size=1)

        # If the score is None, we should not count it when we parse result
        # experiments.
        if not score:
            continue

        scores_to_go -= 1
        print("graph:%s,num_recs:%s,score:%s,rec:%s,iter:%d" % (
            name, str(num_recs), str(score), recommender_name, entity_sample_size - scores_to_go
        ))

# Start experiment
_, graph_name, recommender_name, k_recs, N, min_score_threshold = sys.argv

k_recs = int(k_recs)
N = int(N)
G = get_graph(graph_name)
R = get_recommender(recommender_name, G)
min_threshold = float(min_score_threshold)

evaluate_recommender(G, graph_name, R, recommender_name, k_recs, N, min_threshold)
