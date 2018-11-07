"""Runs evaluation experiments for the random recommender,
for the milestone."""

from gbra.recommender.recommenders import RandomRecommender
from gbra.recommender.evaluator import RecEvaluator
from gbra.data.network_loader import *

def print_basic_stats(name, graph):
    print name
    print 'Entities: {}'.format(graph.num_entities)
    print 'Items:    {}'.format(graph.num_items)
    print 'Edges:    {}'.format(graph.base().GetEdges())

movie_lens = MovielensLoader().load()
print_basic_stats('MovieLens', movie_lens)

beer_advocate = BeeradvocateLoader().load()
print_basic_stats('BeerAdvocate', beer_advocate)

# Let's make an ER graph with the same statistics as the movie_lens data.
erdos_renyi = ErdosRenyiLoader(num_entities=6040, num_items=3952, num_edges=1000209).load()
print_basic_stats('ErdosRenyi', erdos_renyi)

graphs = [(movie_lens, "ml"), (beer_advocate, "ba"), (erdos_renyi, "er")]

def evaluate_recommender(graph, name, num_recs):
    recommender = RandomRecommender(graph)
    evaluator = RecEvaluator(recommender, num_recs=num_recs, verbose=False)
    score = evaluator.evaluate_random_sample(entity_sample_size=1)
    print("graph:%s,num_recs:%s,score:%s" % (name, str(num_recs), str(score)))

# top 10 recommendations
for graph, name in graphs:
    evaluate_recommender(graph, name, 10)

# top 100 recommendations
for graph, name in graphs:
    evaluate_recommender(graph, name, 100)

# top 1000 recommendations
for graph, name in graphs:
    evaluate_recommender(graph, name, 1000)
