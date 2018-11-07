import random
import numpy as np
from scipy import stats
import snap
from abc import abstractmethod

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

    @abstractmethod
    def attack(self, verbose = False):
        raise NotImplemented()

class RandomAttacker(BaseAttacker):
    """Implementation of RandomBot from [S. Lam, J. Riedl. Shilling Recommender Systems for Fun and Profit]
    Fits a normal distribution N to a sample of existing ratings, samples a rating R from N,
    and applies R to a randomly chosen item that is not the target item. Each fake entity rates the
    target item with the highest rating possible."""

    def __init__(self, _recommender, _target_item, _num_fake_entities, _num_fake_ratings, _num_rating_samples):
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
            mu, std, (self.num_fake_entities, self.num_fake_ratings - 1)
        )
        fake_entities = [self.add_fake_entity() for i in range(self.num_fake_entities)]
        for i in range(self.num_fake_entities):
            entity_id = fake_entities[i]
            item_ids = graph.get_random_items(self.num_fake_ratings - 1, replace = False, excluding = self.target_item)
            for j in range(self.num_fake_ratings - 1):
                rating = rating_matrix[i][j]
                item_id = item_ids[j]
                self.recommender._attacker_add_edge(entity_id, item_id, rating)
            self.recommender._attacker_add_edge(entity_id, self.target_item, 100) # TODO: set max rating

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
            self.recommender._attacker_add_edge(entity_id, self.target_item, 100) # TODO: set max rating
