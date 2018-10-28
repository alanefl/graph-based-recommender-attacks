"""
Contains custom asserts
"""

from utils import graph_node_is_item, graph_node_is_entity

def assert_node_is_item(nodeId):
    if not graph_node_is_item(nodeId):
        raise ValueError(
            "Invalid item id: %d. Item ids are even." % nodeId
        )

def assert_node_is_entity(nodeId):
    if not graph_node_is_entity(nodeId):
        raise ValueError(
            "Invalid entity id: %d. Entity ids are odd." % nodeId
        )

def assert_node_exists(nodeId, G):
    if not G.IsNode(nodeId):
        raise ValueError("Node id %d does not exist in the graph." % nodeId)
