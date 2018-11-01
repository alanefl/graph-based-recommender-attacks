
from gbra.recommender.recommenders import RandomRecommender
from gbra.data.network_loader import NetworkLoader


loader = NetworkLoader()
tiny_network = loader.load_network("tiny_test")
recommender = RandomRecommender(tiny_network)
recs_for_3 = recommender.recommend(entity_id=3, number_of_items=3)
recs_for_5 = recommender.recommend(entity_id=5, number_of_items=2)

print("Recommendations for 3: %s" % str(recs_for_3))
print("Recommendations for 5: %s" % str(recs_for_5))
