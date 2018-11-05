"""
Contains the implementation of our recommender system Evaluator.

An Evaluator ingests a recommender and exposes functions for evaluating it.

The basic evaluator evaluates a recommender at an entity as follows:

    number of hits = 0
    For each edge coming out of the current entity:
        Remove edge from the graph
        Run the recommender on the current entity
        If the removed edge was in the recommendations:
            number of hits += 1
        Reinsert edge into the graph
    yield (number of hits) / degree of current entity

Evaluating over the entire graph means adding the evaluations for all
entities and normalizing by the number of entities in the graph and weighing
each score by the degree of an entity.
"""

import numpy as np
import snap

from gbra.util.ei_graph import EIGraph
from gbra.util.asserts import *

class RecEvaluator(object):

    def __init__(self, recommender, num_recs=10, verbose=False):
        """Recommender system evaluator.

        :param recommender: A recommender object.
        :param num_recs: The number of recommendations to give for each
            evaluation step.
        """
        self._recommender = recommender
        self._num_recs = num_recs
        self._verbose = verbose

    def evaluate_at_entity(self, entity_id, neighbors=None):
        """Returns how well the recommender does at predicting items for
        a single entity.

        :param entity_id: the id of the entity to evaluate at
        :param neighbors: for performance, can pass in the neighbor items
            of this entity.
        :returns: a number between 0 and 1 indicating performance, or None
            if the recommender could not be evaluated at the given entity.
        """
        G = self._recommender._G
        if neighbors is None:
            neighbors = G.get_neighbors(entity_id)

        if len(neighbors) < 1:
            # If this neighbor only has a single edge to another item,
            # (or none), we cannot evaluate it using this scheme
            return None
        hits = 0.0
        for neighbor in neighbors:
            G.del_edge(entity_id, neighbor)
            recommendations = self._recommender.recommend(
                entity_id, self._num_recs
            )
            if self._verbose:
                print(
                    "At entity %d, target was %d, and recommendations were %s" % \
                        (entity_id, neighbor, str(recommendations))
                    )
            if neighbor in recommendations:
                hits += 1
            G.add_edge(entity_id, neighbor)

        return hits / len(neighbors)

    def evaluate_all(self):
        """Returns the sum of evaluation scores for every single entity
        in the graph, normalized by the number of entities in the graph,
        and weighted by the degree of each entity.
        """
        cumulative_eval_score = 0.0
        cumulative_degree = 0
        graph_entities = self._recommender._G.get_entities()
        for entity_id in graph_entities:
            neighbors = self._recommender._G.get_neighbors(entity_id)
            if len(neighbors) <= 1:
                # We can't evaluate an entity with one or no edges.
                continue
            cumulative_degree += len(neighbors)
            cumulative_eval_score += self.evaluate_at_entity(
                entity_id, neighbors
            ) * len(neighbors)

        return cumulative_eval_score / cumulative_degree
