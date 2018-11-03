"""General purpose utilities.

To keep the repo sane, utilities more specific to a particular module
should go on a new <module name>_utils.py file
"""

import random
import snap

def get_graph_items(G):
    """Returns a TIntSet containing the nodeIds
    corresponding to the items in G.

    :param G: snap graph
    :return: TIntSet containing item nodes
    """
    items = snap.TIntSet()
    for node in G.Nodes():
        nId = node.GetId()
        if nId % 2 == 0:
            items.AddKey(nId)
    return items

def get_graph_entities(G):
    """Returns a TIntSet containing the nodeIds
    corresponding to the entities in G.

    :param G: snap graph
    :return: TIntSet containing entity nodes
    """
    entities = snap.TIntSet()
    for node in G.Nodes():
        nId = node.GetId()
        if nId % 2 == 1:
            entities.AddKey(nId)
    return entities

def graph_node_is_item(nodeId):
    return nodeId % 2 == 0

def graph_node_is_entity(nodeId):
    return nodeId % 2 == 1

def get_neighbors(G, node):
    """Returns a list containing the node IDs of the neighbors
    of "node"
    """
    if type(node) == int:
        node = G.GetNI(node)
    return [e for e in node.GetOutEdges()]

def get_random_neighbor(G, node):
    """Returns a random neighbor of node in G as a Snap Node.

    Node can be a snap node or an int ID.
    """
    if type(node) == int:
        node = G.GetNI(node)
    return G.GetNI(random.choice([e for e in node.GetOutEdges()]))
