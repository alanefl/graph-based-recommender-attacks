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
from gbra.util.utils import *
from gbra.util.asserts import *
from gbra import Rnd

class BaseRecommender(object):

    def __init__(self, G):
        """Semi-abstract recommender class with an interface for an attacker.

        :param G: A SNAP bipartite graph of entities and items (i.e. users, products)
        """
        self._G = G
        self._attacker_nodes = set()

    def _attacker_add_entity(self, entity_id):
        """Adds a new entity to the graph G.

        Raises an error if a node with the given entity_id already
        exists in the graph G.

        :param entity_id: the id of the new entity to create.
        :returns: the newly-created node.
        """
        assert_node_is_entity(entity_id)

        if self._G.IsNode(entity_id):
            raise ValueError(
                "Attacker can't add existing entity with id: %d." % entity_id
            )
        self._G.AddNode(entity_id)
        self._attacker_nodes.add(entity_id)

    def _attacker_add_edge(self, entity_id, item_id):
        """Adds an edge from an attacker-controlled entity to any
        other item.  Does not check whether the edge already exists.

        Raises an error if the entity is not owned by the attacker.

        :param entity_id: the id of the entity (one end of the edge to add)
        :param item_id: the id of the item (the other end of the edge to add)
        :return: returns the newly-created edge.
        """
        assert_node_is_entity(entity_id)
        assert_node_is_item(entity_id)

        assert_node_exists(entity_id, self._G)
        assert_node_exists(item_id, self._G)

        if entity_id not in self._attacker_nodes:
            raise ValueError(
                "Attacker added edge from forbidden entity: %d" % entity_id
            )

        self._G.AddEdge(entity_id, item_id)

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
        if not self._G.IsNode(entity_id):
            raise ValueError("Node with id %d is not in the graph." % entity_id)

        graph_items = get_graph_items(self._G)
        entity_node = self._G.GetNI(entity_id)
        entity_neighbors = [
            neighborItem for neighborItem in entity_node.GetOutEdges()
        ]

        number_of_items = min(
            number_of_items, graph_items.Len() - len(entity_neighbors)
        )

        recommendations = []
        while number_of_items > 0:
            item = graph_items.GetKey(graph_items.GetRndKeyId(Rnd))
            if item in entity_neighbors or item in recommendations:
                continue
            recommendations.append(item)
            number_of_items -= 1
        return recommendations

class BasicRandomWalkRecommender(BaseRecommender):
    """Recommender basic random walk recommendations.  Based on
    Algorithm 1 in Eskombatchai et al, 2017, with minor modifications.
    """

    def __init__(self, G, num_steps_in_walk=10, alpha=0.5, verbose=False):
        """
        :param - G: snap graph to use in this recommender.
        :param - num_steps_in_walk: N in Eskombatchai et al. The number of steps
        in the random walk.  Each "step" is counted when an item is hit.
        :param - alpha: alpha in Eskombatchai et al, in [0, 1]
        """
        if alpha > 1 or alpha < 0:
            return ValueError("Alpha needs to be between 0 and 1.")
        if num_steps_in_walk < 1:
            raise ValueError("Steps must be positive integers.")

        self._num_steps_in_walk = num_steps_in_walk
        self._alpha = alpha
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
        mu = int(round(self._alpha * self._num_steps_in_walk))
        sigma = int(round(self._num_steps_in_walk / float(4)))
        sample = int(round(np.random.normal(mu, sigma, 1)[0]))
        return min(max(sample, 1), self._num_steps_in_walk)

    def _do_basic_random_walk(self, start_entity):
        V = {} # Maps items to the number of times we've seen them in random walks.
        tot_steps = 0

        if self._verbose:
            print("Starting random walks from entity: %d" % start_entity)

        while tot_steps < self._num_steps_in_walk:
            curr_entity = self._G.GetNI(start_entity)
            curr_steps = self._sample_walk_length()
            walk = [str(start_entity)]

            # Let's not go beyond tot_steps.
            curr_steps = min(curr_steps, self._num_steps_in_walk - tot_steps)

            # curr_entity contains SNAP node of the last traversed entity.
            # curr_item contains the SNAP node of the last traversed item.
            for step in range(curr_steps):
                if step != 0:
                    curr_entity = get_random_neighbor(self._G, curr_item)
                    walk.append(str(curr_entity.GetId()))

                curr_item = get_random_neighbor(self._G, curr_entity)
                walk.append(str(curr_item.GetId()))
                curr_item_id = curr_item.GetId()

                if curr_item_id not in V:
                    V[curr_item_id] = 0
                V[curr_item_id] += 1

            if self._verbose:
                print(' -> '.join(walk))

            tot_steps += curr_steps
        return V

    def recommend(self, entity_id, number_of_items):
        # TODO: it may be a good idea to use better data structures here
        # We want to very quickly get the top_n most visited items
        # in V.  It'd be great if V was already sorted in descending order
        # by the time we get it here.

        # Do random walk.  V maps item ids to number of times the item was
        # seen in a random walk.
        V = self._do_basic_random_walk(entity_id)
        if self._verbose:
            print("Random walk counts:")
            print(V)
            print("")
        entity_neighbor_ids = [e for e in self._G.GetNI(entity_id).GetOutEdges()]

        # Represent V as a list of pairs (k, v) reverse sorted by v.
        V_ = sorted(V.items(), key=lambda x: x[1], reverse=True)

        # Build recommendations.  Only add an item if the entity did
        # not already have an edge to that item.
        recommendations = []
        for i in range(len(V_)):
            item_id, _ = V_[i]
            if item_id not in entity_neighbor_ids:
                recommendations.append(item_id)
            if len(recommendations) >= number_of_items:
                break
        return recommendations

class PixieRecommender(BaseRecommender):
    # TODO
    pass
