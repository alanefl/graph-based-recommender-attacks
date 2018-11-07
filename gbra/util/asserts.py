"""
Contains custom asserts
"""

from ei_graph import EIGraph

def assert_node_is_item(nodeId):
    if not EIGraph.nid_is_item(nodeId):
        raise ValueError(
            "Invalid item id: %d. Item ids are even." % nodeId
        )

def assert_node_is_entity(nodeId):
    if not EIGraph.nid_is_entity(nodeId):
        raise ValueError(
            "Invalid entity id: %d. Entity ids are odd." % nodeId
        )

def assert_node_exists(nodeId, EIG):
    if not EIG.has_node(nodeId):
        raise ValueError("Node id %d does not exist in the graph." % nodeId)
