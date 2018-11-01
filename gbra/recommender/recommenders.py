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
    # TODO
    pass

class PixieRecommender(BaseRecommender):
    # TODO
    pass
