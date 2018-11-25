
import unittest

from gbra.recommender.recommenders import PopularItemRecommender
from gbra.recommender.evaluator import RecEvaluator
from gbra.data.network_loader import MovielensLoader

T = unittest.TestCase('__init__')

print("Experiment: Popular Item Recommender Tester\n\n")

# Movie lens graph with popular item recommender.
movie_lens = MovielensLoader().load()
recommender = PopularItemRecommender(movie_lens)
ml_evaluator = RecEvaluator(recommender, verbose=True)
recs_for_15 = recommender.recommend(entity_id=15, number_of_items=3)
recs_for_21 = recommender.recommend(entity_id=21, number_of_items=5)

print("Movie Lens:")
print("Recommendations for 15: %s" % str(recs_for_15))
print("Recommendations for 21: %s" % str(recs_for_21))
print("Evaluation score for ML: %f" % ml_evaluator.evaluate_random_sample(quick=True))

T.assertEqual(movie_lens.num_entities, 6040)
T.assertEqual(movie_lens.num_items, 3952)
