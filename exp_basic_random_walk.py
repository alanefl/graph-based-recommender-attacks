
from gbra.recommender.recommenders import BasicRandomWalkRecommender
from gbra.recommender.evaluator import RecEvaluator
from gbra.data.network_loader import NetworkLoader

print("Experiment: Basic Random Walk Tester\n\n")

# Tiny Test with basic random walk.
loader = NetworkLoader()
tiny_network = loader.load_network("tiny_test")
recommender = BasicRandomWalkRecommender(
    tiny_network, num_steps_in_walk=50, alpha=0.25
)
tiny_evaluator = RecEvaluator(recommender, verbose=True)
recs_for_3 = recommender.recommend(entity_id=3, number_of_items=3)
recs_for_5 = recommender.recommend(entity_id=5, number_of_items=2)

print("Tiny test")
print("Random recommendations for 3: %s" % str(recs_for_3))
print("Random recommendations for 5: %s" % str(recs_for_5))
print("Evaluation score for tiny test: %f" % tiny_evaluator.evaluate_all())
print("---")

# Erdos-renyi bipartite graph with basic random walk.
loader = NetworkLoader()
er_network = loader.get_erdos_renyi_bipartite_graph(
    num_entities=100, num_items=1000, num_edges=600
)
recommender = BasicRandomWalkRecommender(
    er_network, num_steps_in_walk=400, alpha=0.05
)
er_evaluator = RecEvaluator(recommender)
recs_for_15 = recommender.recommend(entity_id=15, number_of_items=3)
recs_for_21 = recommender.recommend(entity_id=21, number_of_items=5)

print("Erdos Renyi:")
print("Random recommendations for 15: %s" % str(recs_for_15))
print("Random recommendations for 21: %s" % str(recs_for_21))
print("Evaluation score for ER: %f" % er_evaluator.evaluate_all())

assert(er_network.GetNodes() == 100 + 1000)
assert(er_network.GetEdges() == 600)