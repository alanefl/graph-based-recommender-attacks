
import unittest

from gbra.data.network_loader import *
from gbra.net_analysis.characteristics import print_all_stats

T = unittest.TestCase('__init__')

datasets = [
    ('ErdosRenyi', ErdosRenyiLoader(
        num_entities=1000, num_items=1000, num_edges=10000, verbose=False)),
    ('Movielens', MovielensLoader()),
    ('BeerAdvocate', BeeradvocateLoader()),
]

for name, loader in datasets:
    print_all_stats(name, loader.load())
