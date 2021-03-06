"""
Contains the implementation for several recommender systems.

Each recommender object has the interface you'd expect it to have:
      - Instantiating with a graph
      - Getting recommendations
      - Etc

Each recommender system object also exposes an interface to the attacker.
All methods starting with "_attacker_" are meant to be called by the
attacker entity.
"""

import random
import numpy as np

from abc import abstractmethod
from gbra.util.ei_graph import EIGraph
from gbra.util.asserts import *
from gbra import Rnd

class BaseRecommender(object):

    def __init__(self, G):
        """Semi-abstract recommender class with an interface for an attacker.

        :param G: A SNAP bipartite graph of entities and items (i.e. users, products)
        """
        self._G = G
        self._attacker_nodes = set()

    def _attacker_add_entity(self):
        """Adds a new entity to the graph G.

        :returns: the newly-created node.
        """
        entity_id = self._G.add_entity()
        self._attacker_nodes.add(entity_id)
        return entity_id

    def _attacker_add_edge(self, entity_id, item_id, weight):
        """Adds an edge from an attacker-controlled entity to any
        other item.  Does not check whether the edge already exists.

        Raises an error if the entity is not owned by the attacker.

        :param entity_id: the id of the entity (one end of the edge to add)
        :param item_id: the id of the item (the other end of the edge to add)
        :return: returns the newly-created edge.
        """
        assert_node_is_entity(entity_id)
        assert_node_is_item(item_id)

        assert_node_exists(entity_id, self._G)
        assert_node_exists(item_id, self._G)

        if entity_id not in self._attacker_nodes:
            raise ValueError(
                "Attacker added edge from forbidden entity: %d" % entity_id
            )

        self._G.add_edge(entity_id, item_id, weight = weight)

    def calculate_hit_ratio(self, target_item, number_of_items, verbose = False):
        if verbose:
            print "Calculating hit ratio:"
        real_entities = self._G.get_entities() - self._attacker_nodes
        hits = 0
        count = 0
        for entity_id in real_entities:
            if verbose:
                print "Processing %d/%d" % (count, len(real_entities))
            try:
                recommendations = self.recommend(entity_id, number_of_items)
            except:
                recommendations = []
            if target_item in recommendations:
                hits += 1
            count += 1
        ratio = hits * 1.0 / count
        if verbose:
            print "Calculated hit ratio: %f" % ratio
        return ratio

    @abstractmethod
    def recommend(self, entity_id, number_of_items):
        """Returns an ordered list of items recommended
        for the given entity.  Returns the following number of recommendations:

            min(number_of_items, items in the graph - num neighbors of entity_id)
        """
        raise NotImplemented()

class RandomRecommender(BaseRecommender):
    """Recommender that returns random recommendations
    """
    def recommend(self, entity_id, number_of_items):
        if not self._G.has_entity(entity_id):
            raise ValueError("Node with id %d is not in the graph." % entity_id)

        graph_items = tuple(self._G.get_items())
        entity_node = self._G.base().GetNI(entity_id)
        entity_neighbors = [
            neighborItem for neighborItem in entity_node.GetOutEdges()
        ]

        number_of_items = min(
            number_of_items, len(graph_items) - len(entity_neighbors)
        )

        recommendations = []
        while number_of_items > 0:
            item = random.choice(graph_items)
            if item in entity_neighbors or item in recommendations:
                continue
            recommendations.append(item)
            number_of_items -= 1
        return recommendations

class PopularItemRecommender(BaseRecommender):
    """Recommender that returns random recommendations from the top K most popular items,
    where an item's popularity is defined as the sum of the weights of all its out edges.

    If top k most popular items are not enough to give recommendations to an entity,
    the algorithm devolves to random sampling.
    """

    def __init__(self, G, num_popular_items=500):
        """
        :param G: EIGraph to recommend for.
        :param num_popular_items: the number of popular items to recommend items from.
        """
        super(PopularItemRecommender, self).__init__(G)
        self._install_popular_items(num_popular_items)

    def _install_popular_items(self, num_items):
        """Constructs an ordered list of the top "num_items" and stores
        it as a class variable.  The "top" items are filtered according to the
        sum of the weights of their out edges.
        """

        # TODO: if the total number of items is huge, we need to be smarter about this,
        # i.e., use a min heap for keeping the top k most popular elements.
        popular_items = []

        items = self._G.get_items()
        for item in items:
            neighbors = self._G.get_neighbors(item)
            total_popularity = 0
            for neighbor in neighbors:
                total_popularity += self._G.get_edge_weight(item, neighbor)
            popular_items.append((item, total_popularity))

        self._popular_items = np.array([
            i[0] for i in sorted(
                popular_items, key=lambda x: x[1], reverse=True
            )[:num_items]
        ])

    def recommend(self, entity_id, number_of_items):
        if not self._G.has_entity(entity_id):
            raise ValueError("Node with id %d is not in the graph." % entity_id)

        graph_items = tuple(self._G.get_items())
        entity_node = self._G.base().GetNI(entity_id)
        entity_neighbors = [
            neighborItem for neighborItem in entity_node.GetOutEdges()
        ]

        number_of_items = min(
            number_of_items, len(graph_items) - len(entity_neighbors)
        )

        recommendations = []

        # Let's permute popular items and scan for recommendations.
        self._popular_items = np.random.permutation(self._popular_items)
        for pop_item in self._popular_items:
            if number_of_items == 0:
                break
            if pop_item in entity_neighbors or pop_item in recommendations:
                continue
            recommendations.append(pop_item)
            number_of_items -= 1

        # If we still need to recommend some things, let's just do it by randomly
        # sampling all items.
        while number_of_items > 0:
            item = random.choice(graph_items)
            if item in entity_neighbors or item in recommendations:
                continue
            recommendations.append(item)
            number_of_items -= 1

        return recommendations

class BasicRandomWalkRecommender(BaseRecommender):
    """Recommender basic random walk recommendations.  Based on
    Algorithm 1 in Eskombatchai et al, 2017, with minor modifications.

    The random walks here are "weighted" which means at each step,
    we take a random sample of neighboring nodes to proceed to based on
    the weights of those nodes.
    """

    def __init__(self, G, max_steps_in_walk=10,
            alpha=0.5, beta=10, verbose=False):
        """
        :param n_p: n_p in Alg 2 in Eskombatchai et al
        :param n_v: n_v in Alg 2 in in Eskombatchai et al. The number of
            items that, if visited at least n_p times each, is sufficient to
            terminate the algorithm.
        :param - G: snap graph to use in this recommender.
        :param - max_steps_in_walk: N in Eskombatchai et al. The number of steps
            across all random walks from an entity.  Each "step" is counted when an item is hit.
        :param - alpha: parameter for tuning random walk samples in [0, 1]
        :param - beta: parameter that directly indicates the variance of
            the random walk samples.

        """
        if alpha > 1 or alpha < 0:
            return ValueError("Alpha needs to be between 0 and 1.")
        if max_steps_in_walk < 1:
            raise ValueError("Steps must be positive integers.")

        self._max_steps_in_walk = max_steps_in_walk
        self._alpha = alpha
        self._beta = beta
        self._verbose = verbose
        super(BasicRandomWalkRecommender, self).__init__(G)

    def _sample_walk_length(self):
        """Returns the walk length to carry out, based on alpha
        This function is not clarified in Eskombatchai et al, 2017. It is likely
        the walk length sampling logic is a trade secret.

        The approach here is as follows:

            random walk length is drawn from a normal distribution
            with mean int(round(alpha * N)), and
            standard deviation int(round(N/4)).  If the sample is beyond
            1 or N, we bring it back into the interval.

        Intuitively, smaller alphas bias towards shorter walks, whereas
        larger alphas bias towards longer walks.
        """
        mu = int(round(self._alpha * self._max_steps_in_walk))
        sigma = self._beta
        sample = int(round(np.random.normal(mu, sigma, 1)[0]))

        # Clip back to desired range.
        return min(max(sample, 1), self._max_steps_in_walk)

    def _do_basic_random_walk(self, start_entity):
        V = {} # Maps items to the number of times we've seen them in random walks.
        tot_steps = 0

        if self._verbose:
            print("Starting random walks from entity: %d" % start_entity)

        while tot_steps < self._max_steps_in_walk:
            curr_entity = self._G.base().GetNI(start_entity)
            curr_steps = self._sample_walk_length()
            walk = [str(start_entity)]

            # Let's not go beyond tot_steps.
            curr_steps = min(curr_steps, self._max_steps_in_walk - tot_steps)

            # curr_entity contains SNAP node of the last traversed entity.
            # curr_item contains the SNAP node of the last traversed item.
            for step in range(curr_steps):
                if step != 0:
                    curr_entity = self._G.get_random_neighbor(curr_item, use_weights=True)
                    walk.append(str(curr_entity.GetId()))

                curr_item = self._G.get_random_neighbor(curr_entity, use_weights=True)
                walk.append(str(curr_item.GetId()))
                curr_item_id = curr_item.GetId()

                if curr_item_id not in V:
                    V[curr_item_id] = 0
                V[curr_item_id] += 1

            if self._verbose:
                print(' -> '.join(walk))

            tot_steps += curr_steps
        return V

    def _recommend(self, entity_id, number_of_items, random_walk_func):
        # TODO: it may be a good idea to use better data structures here
        # We want to very quickly get the top_n most visited items
        # in V.  It'd be great if V was already sorted in descending order
        # by the time we get it here.

        # Do random walk.  V maps item ids to number of times the item was
        # seen in a random walk.
        V = random_walk_func(entity_id)
        if self._verbose:
            print("Random walk counts:")
            print(V)
            print("")
        entity_neighbor_ids = list(self._G.base().GetNI(entity_id).GetOutEdges())

        # Represent V as a list of pairs (k, v) reverse sorted by v.
        V_ = sorted(V.items(), key=lambda x: x[1], reverse=True)

        # Build recommendations.  Only add an item if the entity did
        # not already have an edge to that item.
        recommendations = []
        for item_id, _ in V_:
            if item_id not in entity_neighbor_ids:
                recommendations.append(item_id)
            if len(recommendations) >= number_of_items:
                break
        return recommendations

    def recommend(self, entity_id, number_of_items):
        return self._recommend(
            entity_id, number_of_items, random_walk_func=self._do_basic_random_walk
        )


class PixieRandomWalkRecommender(BasicRandomWalkRecommender):
    """Pixie random walk recommendations.  Based on
    Algorithm 2 in Eskombatchai et al, 2017, with minor modifications.

    Differences:
        1) We don't have access to the SampleWalkLength logic presented in the paper
        2) We don't have proprietary knowledge to determine "personalized neighbors"
           of an entity. We simply used a weighted random walk based on the
           neighboring edges.

    The random walks here are "weighted" which means at each step,
    we take a random sample of neighboring nodes to proceed to based on
    the weights of those nodes.
    """

    def __init__(self, n_p, n_v, *args, **kwargs):
        """
        :param n_p: n_p in Alg 2 in Eskombatchai et al
        :param n_v: n_v in Alg 2 in in Eskombatchai et al. The number of
            items that, if visited at least n_p times each, is sufficient to
            terminate the algorithm.
        """
        self._n_p = n_p
        self._n_v = n_v
        super(PixieRandomWalkRecommender, self).__init__(*args, **kwargs)

    def _do_pixie_random_walk(self, start_entity):
        V = {} # Maps items to the number of times we've seen them in random walks.
        tot_steps = 0

        if self._verbose:
            print("Starting random walks from entity: %d" % start_entity)

        num_high_visited = 0
        while tot_steps < self._max_steps_in_walk \
            and num_high_visited <= self._n_p:
            curr_entity = self._G.base().GetNI(start_entity)
            curr_steps = self._sample_walk_length()
            walk = [str(start_entity)]

            # Let's not go beyond tot_steps.
            curr_steps = min(curr_steps, self._max_steps_in_walk - tot_steps)

            # curr_entity contains SNAP node of the last traversed entity.
            # curr_item contains the SNAP node of the last traversed item.
            for step in range(curr_steps):
                if step != 0:
                    curr_entity = self._G.get_random_neighbor(curr_item, use_weights=True)
                    walk.append(str(curr_entity.GetId()))

                curr_item = self._G.get_random_neighbor(curr_entity, use_weights=True)
                walk.append(str(curr_item.GetId()))
                curr_item_id = curr_item.GetId()

                if curr_item_id not in V:
                    V[curr_item_id] = 0
                V[curr_item_id] += 1

                if V[curr_item_id] == self._n_v:
                    num_high_visited += 1

            if self._verbose:
                print(' -> '.join(walk))

            tot_steps += curr_steps
        return V

    def recommend(self, entity_id, number_of_items):
        return super(PixieRandomWalkRecommender, self)._recommend(
            entity_id, number_of_items, random_walk_func=self._do_pixie_random_walk
        )
