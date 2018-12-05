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
from gbra.util.print_utils import *
from gbra import Rnd

class RecEvaluator(object):

    def __init__(self, recommender, num_recs=10, min_score_threshold=0, verbose=False):
        """Recommender system evaluator.

        :param recommender: A recommender object.
        :param num_recs: The number of recommendations to give for each
            evaluation step.
        :param min_score_threshold: The minimum rating to consider in
            evaluation logic.  i.e. if min_score_threshold is 4, the evaluator
            will only evaluate whether the recommender can re-generate edges
            to an item that have weight 4 or more.
        """
        self._recommender = recommender
        self._num_recs = num_recs
        self._verbose = verbose
        self._min_score_threshold = min_score_threshold

        # Entities with degree 30 or less.
        self._quick_entities = []

        # All entities
        self._entities = recommender._G.get_entities()

        # Set up the entities to work with if we require "quick" evaluation
        # in our samples.
        for entity in self._entities:
            neighbors = self._recommender._G.get_neighbors(entity)
            if len(neighbors) > 30:
                continue
            self._quick_entities.append(entity)

    def evaluate_at_entity(self, entity_id, neighbors_to_eval=None):
        """Returns how well the recommender does at predicting items for
        a single entity.

        :param entity_id: the id of the entity to evaluate at
        :param neighbors_to_eval: for performance, can pass in the neighbor items
            of this entity.
        :returns: a number between 0 and 1 indicating performance, or None
            if the recommender could not be evaluated at the given entity.
        """
        G = self._recommender._G
        if neighbors_to_eval is None:
            neighbors_to_eval = G.get_neighbors(entity_id)

        if len(neighbors_to_eval) < 1:
            # If this neighbor only has a single edge to another item,
            # (or none), we cannot evaluate it using this scheme
            return None
        hits = 0.0
        for neighbor in neighbors_to_eval:
            G.del_edge(entity_id, neighbor)
            recommendations = self._recommender.recommend(
                entity_id, self._num_recs
            )
            output = "At entity %d, target was %d, and recommendations were %s" % \
                (entity_id, neighbor, str(recommendations))

            if neighbor in recommendations:
                hits += 1
                if self._verbose:
                    print_green(output)
            else:
                if self._verbose:
                    print(output)

            G.add_edge(entity_id, neighbor)

        return hits / len(neighbors_to_eval)

    def evaluate_all(self):
        """Returns the sum of evaluation scores for every single entity
        in the graph, normalized by the number of entities in the graph.
        """
        return self._evaluate(self._recommender._G.get_entities())

    def evaluate_random_sample(self, entity_sample_size=10, quick=False):
        """Returns the sum of recommender evaluation scores for a certain set
        of randomly sampled entities in the graph, normalized by the number of
        entities. If quick=True, only looks at entities with 30 or less
        items.
        """
        entities_to_work_with = self._entities if not quick else self._quick_entities
        entities_to_work_with = list(entities_to_work_with)
        if len(entities_to_work_with) < entity_sample_size:
            print(len(entities_to_work_with), entity_sample_size)
            raise ValueError(
                "Not enough entities in graph satisfying quickness property."
            )

        entity_sample = set()
        while entity_sample_size > 0:
            entity = np.random.choice(entities_to_work_with)
            assert(entity % 2 == 1)

            neighbors = self._recommender._G.get_neighbors(entity)

            # Let's not look at very high degree or very low degree nodes in any case.
            if len(neighbors) > 200 or len(neighbors) < 5:
                continue

            if entity not in entity_sample:
                entity_sample_size -= 1
                entity_sample.add(entity)

        return self._evaluate(entity_sample)

    def _evaluate(self, entity_set):
        """Returns sum of recommender evaluation scores for the given set
        of entities, normalized by the number of entities.
        """
        cumulative_eval_score = 0.0
        graph_entities = self._recommender._G.get_entities()
        for entity_id in entity_set:
            assert(entity_id % 2 == 1)
            neighbors = self._recommender._G.get_neighbors(entity_id)

            # Only keep this neighbors to which you have an edge with weight
            # greater than the min score threshold.  This is so that we don't
            # measure hit ratio for edges that should not be recommended in
            # the first place.
            neighbors = [
                n for n in neighbors \
                    if self._recommender._G.get_edge_weight(
                        n, entity_id
                    ) >= self._min_score_threshold
            ]

            if len(neighbors) <= 1:
                # We can't evaluate an entity with one or no valid edges.
                continue
            curr_cumulative_eval_score = self.evaluate_at_entity(
                entity_id, neighbors
            )

            cumulative_eval_score += curr_cumulative_eval_score

        return cumulative_eval_score / len(entity_set)
