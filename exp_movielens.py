
from gbra.data.network_loader import MovielensLoader

graph = MovielensLoader().load()
print graph.num_entities
print graph.num_items
