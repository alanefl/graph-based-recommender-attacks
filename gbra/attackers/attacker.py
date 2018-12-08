import random
import numpy as np
from scipy import stats
import snap
from abc import abstractmethod
from collections import Counter

from gbra.recommender.recommenders import PixieRandomWalkRecommender

class BaseAttacker(object):
    """Base configurations for an Attacker"""
    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings):
        self.recommender = _recommender
        self.target_item = _target_item
        self.num_fake_entities = _num_fake_entities
        self.num_fake_ratings = _num_fake_ratings

    def add_fake_entity(self):
        """Adds a fake entity to the graph and returns the ID"""
        return self.recommender._attacker_add_entity()

    def get_degree_dictionary(self):
        """Cache the dictionary of item_id -> degree as a .npy file"""
        graph = self.recommender._G
        name = graph.name
        try:
            return np.load(name + '-item-degrees.npy').item()
        except:
            graph = self.recommender._G
            degrees = {}
            for item_id in graph.get_items():
                degrees[item_id] = len(graph.get_neighbors(item_id))
            np.save(name + '-item-degrees.npy', degrees)
            return degrees

    @abstractmethod
    def attack(self, verbose = False):
        raise NotImplemented()

class RandomAttacker(BaseAttacker):
    """Implementation of RandomBot from [S. Lam, J. Riedl. Shilling Recommender Systems for Fun and Profit]
    Fits a normal distribution N to a sample of existing ratings, samples a rating R from N,
    and applies R to a randomly chosen item that is not the target item. Each fake entity rates the
    target item with the highest rating possible."""

    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings, _num_rating_samples = 20):
        self.num_rating_samples = _num_rating_samples
        super(RandomAttacker, self).__init__(_recommender, _target_item, _num_fake_entities, _num_fake_ratings)

    def _fit_rating_distribution(self):
        """Returns the (mean, std) of a normal distribution fitted from num_rating_samples"""
        graph = self.recommender._G
        sample_weights = [
            graph.get_random_edge()[2] for i in range(self.num_rating_samples)
        ]
        mu, std = stats.norm.fit(sample_weights)
        return (mu, std)

    def attack(self, verbose = False):
        mu, std = self._fit_rating_distribution()
        graph = self.recommender._G
        rating_matrix = np.random.normal(
            mu, max(std, 0.1), (self.num_fake_entities, self.num_fake_ratings - 1)
        )
        fake_entities = [self.add_fake_entity() for i in range(self.num_fake_entities)]
        for i in range(self.num_fake_entities):
            entity_id = fake_entities[i]
            item_ids = graph.get_random_items(self.num_fake_ratings - 1, replace = False, excluding = self.target_item)
            for j in range(self.num_fake_ratings - 1):
                rating = rating_matrix[i][j]
                item_id = item_ids[j]
                self.recommender._attacker_add_edge(entity_id, item_id, rating)
            self.recommender._attacker_add_edge(entity_id, self.target_item, graph.rating_range[1])

class AverageAttacker(BaseAttacker):
    """Implementation of AverageBot from [S. Lam, J. Riedl. Shilling Recommender Systems for Fun and Profit]
    Uniformly chooses a random item and creates a fake rating sampled from a normal distribution with mean
    equal to the average rating and standard deviation of 1.1. Each fake entity rates the
    target item with the highest rating possible."""

    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings):
        super(AverageAttacker, self).__init__(_recommender, _target_item, _num_fake_entities, _num_fake_ratings)

    def attack(self, verbose = False):
        graph = self.recommender._G
        fake_entities = [self.add_fake_entity() for i in range(self.num_fake_entities)]
        average_cache = {} # caches the average rating of randomly selected items
        for entity_id in fake_entities:
            item_ids = graph.get_random_items(self.num_fake_ratings - 1, replace = False, excluding = self.target_item)
            for item_id in item_ids:
                if item_id not in average_cache:
                    average_cache[item_id] = graph.get_average_edge_weight(item_id)
                sample_rating = np.random.normal(average_cache[item_id], 1.1)
                self.recommender._attacker_add_edge(entity_id, item_id, sample_rating)
            self.recommender._attacker_add_edge(entity_id, self.target_item, graph.rating_range[1])

class NeighborAttacker(BaseAttacker):
    """Generates fake reviews on items that are two hops away from the
    target item and gives highest-rating reviews to the target item."""
    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings):
        super(NeighborAttacker, self).__init__(_recommender, _target_item, _num_fake_entities, _num_fake_ratings)

    def attack(self, verbose = False):
        graph = self.recommender._G
        fake_entities = [self.add_fake_entity() for i in range(self.num_fake_entities)]
        target_reviewers = graph.get_neighbors(self.target_item)
        also_reviewed = set()
        for reviewer in target_reviewers:
            also_reviewed |= set(graph.get_neighbors(reviewer))

        also_reviewed -= set([self.target_item])

        average_cache = {}
        for entity_id in fake_entities:
            item_ids = np.random.choice(list(also_reviewed), min(self.num_fake_ratings - 1, len(also_reviewed)), replace = False)
            for item_id in item_ids:
                if item_id not in average_cache:
                    average_cache[item_id] = graph.get_average_edge_weight(item_id)
                sample_rating = np.random.normal(average_cache[item_id], 1.1)
                self.recommender._attacker_add_edge(entity_id, item_id, sample_rating)
            self.recommender._attacker_add_edge(entity_id, self.target_item, graph.rating_range[1])


class LowDegreeAttacker(BaseAttacker):
    # _num_fake_ratings is interpreted as per fake user
    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings):
        super(LowDegreeAttacker, self).__init__(_recommender, _target_item, _num_fake_entities, _num_fake_ratings)

    def attack(self, verbose = False):
        degrees = self.get_degree_dictionary()
        del degrees[self.target_item]

        degrees = { item_id : (degrees[item_id] * -1) for item_id in degrees if degrees[item_id] != 0}
        sorted_ids = [a[0] for a in Counter(degrees).most_common(len(degrees))]
        entities = [self.add_fake_entity() for i in range(self.num_fake_entities)]
        i = 0
        for j in range(self.num_fake_ratings):
            for entity in entities:
                self.recommender._attacker_add_edge(entity, sorted_ids[i % len(sorted_ids)], 5)
                i += 1
        for entity in entities:
            self.recommender._attacker_add_edge(entity, self.target_item, 5)

class HighDegreeAttacker(BaseAttacker):
    # _num_fake_ratings is interpreted as per fake user
    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings):
        super(HighDegreeAttacker, self).__init__(_recommender, _target_item, _num_fake_entities, _num_fake_ratings)

    def attack(self, verbose = False):
        degrees = self.get_degree_dictionary()
        del degrees[self.target_item]

        sorted_ids = [a[0] for a in Counter(degrees).most_common(len(degrees))]
        entities = [self.add_fake_entity() for i in range(self.num_fake_entities)]
        i = 0
        for j in range(self.num_fake_ratings):
            for entity in entities:
                self.recommender._attacker_add_edge(entity, sorted_ids[i % len(sorted_ids)], 5)
                i += 1
        for entity in entities:
            self.recommender._attacker_add_edge(entity, self.target_item, 5)

class HillClimbingAttacker(BaseAttacker):
    # Standard Hill Climbing Algorithm (white box)
    # Doesn't take into account weights, ignores _num_fake_ratings
    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings):
        super(HillClimbingAttacker, self).__init__(_recommender, _target_item, _num_fake_entities, _num_fake_ratings)
    def attack(self, verbose = False):
        network = self.recommender._G
        seen = set()
        chosen = []
        neighbors = {}
        for item_id in network.get_items():
            neighbors[item_id] = set(network.get_neighbors(item_id) + [item_id])
        del neighbors[self.target_item]
        while True: # exits when all nodes are seen
            intersects = Counter({item_id : len(neighbors[item_id] - seen) for item_id in neighbors})
            if len(intersects) == 0:
                break
            [(next_item, count)] = intersects.most_common(1)
            if (count == 0):
                break
            chosen.append(next_item)
            seen |= set(neighbors[next_item])

            del neighbors[next_item]

        entities = [self.add_fake_entity() for i in range(self.num_fake_entities)]
        i = 0
        for j in range(self.num_fake_ratings):
            for entity in entities:
                self.recommender._attacker_add_edge(entity, chosen[i % len(chosen)], 5)
                i += 1

        for entity in entities:
            self.recommender._attacker_add_edge(entity, self.target_item, 5)


class BlackBoxRWRAttacker(BaseAttacker):
    """
    Approximates RWR each item in the graph and then for each of the
    top `_num_items_to_scout`, creates a fake entity that adds a high review
    to that item and to the target item.

    NOTE: doesn't use _num_fake_ratings, always only makes one rating per
    fake user.
    """

    def __init__(self, _num_items_to_scout, _num_recs, *args, **kwargs):
        super(BlackBoxRWRAttacker, self).__init__(*args, **kwargs)
        self.num_items_to_scout = _num_items_to_scout
        self.num_recs = _num_recs

    def attack(self, verbose = False):
        item_to_approx_rwr = self.run_scout()

        max_rating = max(self.recommender._G.rating_range)
        sorted_items = sorted(
            item_to_approx_rwr.iteritems(),
            key=lambda (iid, approx_rwr): approx_rwr, reverse=True
        )

        for i in range(self.num_fake_entities):
            fake_entity_id = self.add_fake_entity()
            item_to_attack = sorted_items[i % len(sorted_items)][0]
            self.recommender._attacker_add_edge(
                fake_entity_id, item_to_attack, max_rating
            )
            self.recommender._attacker_add_edge(
                fake_entity_id, self.target_item, max_rating
            )

    def run_scout(self):
        scout_id = self.add_fake_entity()

        item_to_approx_rwr = dict(
            (item, self.approxRWR(scout_id, item))
            for item, _ in self.get_top_items()
        )
        return item_to_approx_rwr

    def get_top_items(self):
        """Return the top `num_items_to_scout` according to weighted degree

        Weighted degree for an item is the sum of weights of its edges.

        We originally considered shifting the weights to be centered at 0,
        with the intuition that an item with many negative reviews should
        have a lower score than one with few, but positive, reviews.

        However -- we decided to stick with just vanilla weighted degree,
        because it's not clear that such a weighting scheme leads to items
        with higher RWR.
        """
        return sorted(
            self.recommender._G.get_weighted_item_to_degree().iteritems(),
            key=lambda (iid, weighted_deg): weighted_deg,
            reverse=True
        )[:self.num_items_to_scout]

    def approxRWR(self, entity_id, item_id):
        max_rating = max(self.recommender._G.rating_range)
        self.recommender._attacker_add_edge(entity_id, item_id, max_rating)
        recs = self.recommender.recommend(entity_id, self.num_recs)
        self.recommender._G.del_edge(entity_id, item_id)

        return sum(
            self.recommender._G.get_weighted_degree(iid)
            for iid in recs
        )
