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

    def __init__(self, recommender, num_recs=10, verbose=False):
        """Recommender system evaluator.

        :param recommender: A recommender object.
        :param num_recs: The number of recommendations to give for each
            evaluation step.
        """
        self._recommender = recommender
        self._num_recs = num_recs
        self._verbose = verbose

        # Entities with degree 30 or less.
        self._quick_entities = []

        # All entities
        self._entities = []

        # Set up the entities to work with if we require "quick" evaluation
        # in our samples.
        for entity in self._recommender._G.get_entities():
            self._entities.append(entity)
            neighbors = self._recommender._G.get_neighbors(entity)
            if len(neighbors) > 30:
                continue
            self._quick_entities.append(entity)

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

        return hits / len(neighbors)

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

            # Let's not look at very high degree nodes in any case.
            if len(neighbors) > 200:
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
            if len(neighbors) <= 1:
                # We can't evaluate an entity with one or no edges.
                continue
            curr_cumulative_eval_score = self.evaluate_at_entity(
                entity_id, neighbors
            )

            cumulative_eval_score += curr_cumulative_eval_score

        return cumulative_eval_score / len(entity_set)
