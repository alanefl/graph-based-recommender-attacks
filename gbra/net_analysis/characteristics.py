"""Tools for measuring network characteristics."""

from collections import Counter

import matplotlib.pyplot as plt
import snap

def plot_degree_distribution(ei_graph, name):
    """Create a plot of degree distribution and saves image to file.

    :param name: used to create the output filename, `outDeg.name.plt`,
        and in the title of the plot.

    https://snap.stanford.edu/snappy/doc/reference/PlotOutDegDistr.html
    """
    description = 'Degree Distribution for ' + name
    snap.PlotOutDegDistr(ei_graph.base(), name, description)

def get_diameter(ei_graph):
    """Returns the graph diameter.

    https://snap.stanford.edu/snappy/doc/reference/GetBfsFullDiam.html
    """
    num_sample = min(ei_graph.base().GetNodes(), 100)
    is_directed = False
    return snap.GetBfsFullDiam(ei_graph.base(), num_sample, is_directed)

def get_cluster_coeff(ei_graph):
    """Returns the average clustering coefficient.

    https://snap.stanford.edu/snappy/doc/reference/GetClustCf.html
    """
    return snap.GetClustCf(ei_graph.base())

def get_component_distribution(ei_graph):
    """Returns the sizes of strongly connected components.

    returns: dict of (size of component -> num of such components)

    https://snap.stanford.edu/snappy/doc/reference/GetSccs.html
    """
    components = snap.TCnComV()
    snap.GetSccs(ei_graph.base(), components)
    return Counter(c.Len() for c in components)


def get_fill(ei_graph):
    """Returns the fill of `ei_graph`.

    Fill = # edges / # total possible edges
    """
    e = ei_graph.base().GetEdges()
    n = ei_graph.base().GetNodes()
    return float(e) / (n*n)

def print_basic_stats(name, ei_graph):
    print name
    print 'Entities & {} \\\\'.format(ei_graph.num_entities)
    print 'Items    & {} \\\\'.format(ei_graph.num_items)
    print 'Edges    & {} \\\\'.format(ei_graph.base().GetEdges())
    print 'Fill     & {:.4f} \\\\'.format(get_fill(ei_graph))

def print_complex_stats(name, ei_graph):
    plot_degree_distribution(ei_graph, name)
    print 'Diameter       & {} \\\\'.format(get_diameter(ei_graph))
    print 'Cluster Coeff  & 0.0 (always for E-I networks) \\\\'
    print 'Components (size, count) & {} \\\\'.format(
        sorted(get_component_distribution(ei_graph).iteritems()))

def print_all_stats(name, ei_graph):
    print_basic_stats(name, ei_graph)
    print_complex_stats(name, ei_graph)
    print ''
