import unittest
import sys

from gbra.data.network_loader import MovielensLoader, BeeradvocateLoader, ErdosRenyiLoader
from gbra.attackers.attacker import NeighborAttacker, RandomAttacker, AverageAttacker
from gbra.recommender.recommenders import PixieRandomWalkRecommender
from gbra.net_analysis.characteristics import print_all_stats

T = unittest.TestCase('__init__')

graph_name, percent_fake_entities, fake_reviews, attacker_name = sys.argv[1:]
percent_fake_entities = float(percent_fake_entities)
fake_reviews = int(fake_reviews)
NUM_RECOMMENDATIONS = 5

loaders = {
    "Movielens":    MovielensLoader(),
    "BeerAdvocate": BeeradvocateLoader(),
    "ErdosRenyi":   ErdosRenyiLoader(num_entities=33387, num_items=66051, num_edges=1571251, verbose=False) 
                                     # matches BeerAdvocate 
}
network = loaders[graph_name].load()
recommender = PixieRandomWalkRecommender(
    n_p=30, n_v=4, G=network, num_steps_in_walk=200, alpha=0.25
)

[target_item] = network.get_random_items(1)

fake_entities = int(percent_fake_entities * network.num_items)

attackers = {
    "Random" : RandomAttacker(recommender, target_item, fake_entities, fake_reviews, 20),
    "Average": AverageAttacker(recommender, target_item, fake_entities, fake_reviews),
    "Neighbor": NeighborAttacker(recommender, target_item, fake_entities, fake_reviews)
}
attacker = attackers[attacker_name]

print "{}Attack on {} graph with {} fake users and {} fake reviews: ".format(attacker_name, graph_name, fake_entities, fake_reviews)

filename = '-'.join([attacker_name, graph_name, str(percent_fake_entities), str(fake_reviews)])

print_all_stats(filename, network)
print "Hit ratio before attack %f" % recommender.calculate_hit_ratio(target_item, NUM_RECOMMENDATIONS, verbose=False)
attacker.attack()
print "Hit ratio after attack %f" % recommender.calculate_hit_ratio(target_item, NUM_RECOMMENDATIONS, verbose=False)
print_all_stats(filename, network)


