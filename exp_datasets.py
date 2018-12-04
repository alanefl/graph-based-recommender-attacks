
import unittest

from gbra.data.network_loader import *
from gbra.net_analysis.characteristics import print_all_stats

T = unittest.TestCase('__init__')

datasets = [
    ('ErdosRenyi', ErdosRenyiLoader(
        num_entities=6040, num_items=3952, num_edges=1000209, verbose=False)),
    ('Movielens', MovielensLoader()),
    ('Movielens100k', Movielens100kLoader()),
    ('BeerAdvocate', BeeradvocateLoader()),
]

for name, loader in datasets:
    print_all_stats(name, loader.load())
