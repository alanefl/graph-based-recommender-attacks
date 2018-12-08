
# import matplotlib.pyplot as plt
# import networkx as nx

from gbra.util.ei_graph import EIGraph
from gbra.recommender.recommenders import PixieRandomWalkRecommender

"""
Our recommender, based on Pixie, performs a random walk from the entity e
and returns the K items that are reached most frequently by random walks
of varying lengths.

The hit-ratio of an attacker for a target item I is the fraction of nodes
in the Graph that are recommended I.

Our attacker is:
    Given: (
        Graph G,
        Recommender R,
        target item I,
        num_fake_users N,
        num_fake_reviews M
    )
    Outputs:
        list of N*M edges to add to G, with the goal of increasing the hit-ratio
        of I

The below example shows a graph that has the following edges
1 -> 2
3 -> 2
5 -> 2, 4
7 -> 4, 6
9 (fake) -> 8 (target)

Note that:
    item 2 has degree 3
    item 4 has degree 2
    item 6 has degree 1

We tune the parameters of our Pixie recommender for the purposes of this
small graph, and only recommend *1* item to a user.

First, we expect that:
    nodes 1 and 3 are recommended 4
    node 5 is recommended 6
    node 7 is recommended 2

Next, consider the attacking scenario.

We examine the hit ratio for target item 8, for each possible edge that fake
user (9) can add to the other items (2,4,6).

There are a handful of basic ideas for how to pick which item the fake user
should add a review for:
1. highest degree: by adding an edge to 2, we maximize the direct exposure of
    the fake item to other users.
2. lowest degree: adding an edge to 6 may be good because it directly targets
    a single user with a high likelihood of swaying them (vs. high degree
    which has a higher "diffusion").
3. items that reach the most other users: we introduce an idea called
    random walk reachability (RWR) on items, which is high for items that
    can reach a large number of distinct entities.

In the end, we care about decreasing the average distance of a random walk
from every other node in the graph to the target item. For this reason,
we believe 3. RWR is a promising direction.
"""

# create a small graph to illustrate RWR
G = EIGraph(5, 4)

# the fake user gives the target item a review
fake_user = 9
target_item = 8

edges = [
    (1, 2),
    (3, 2),
    (5, 2),
    (5, 4),
    (7, 4),
    (7, 6),
    (fake_user, target_item)
]

for e in edges:
    G.add_edge(*e)

# this visualization is very bad, it doesn't optimize for low edge crossing
# nx_graph = nx.Graph(edges)
# pos = nx.bipartite_layout(nx_graph, [1,3,5,7,9])
# nx.draw(nx_graph, with_labels=True, font_weight='bold', pos=pos)
# plt.savefig('small_rwr_vis.png')

quit()


def make_rec(graph, walk_len):
    # e.g. this is basically a random walk of constant length
    STEPS_IN_RANDOM_WALK = walk_len
    N_P = 30
    N_V = 4
    ALPHA = 1
    BETA = 0.001

    return PixieRandomWalkRecommender(
        n_p=N_P, n_v=N_V, G=graph, max_steps_in_walk=STEPS_IN_RANDOM_WALK, alpha=ALPHA,
        beta=BETA)

for wl in [5,20,100,200,500,1000]:
    print '\n == walk length ', wl
    base_rec = make_rec(G, wl)

    NUM_RECS = 2

    for eid in [1,3,5,7]:
        recs = base_rec.recommend(entity_id=eid, number_of_items=NUM_RECS)
        print 'recs for eid {}: {}'.format(eid, recs)

    hr_before = base_rec.calculate_hit_ratio(target_item, NUM_RECS)
    print 'hit-ratio before:', hr_before
    print ' (expect 0, since the target item is disconnected from all other entities)'

    def do_attack(review_item_id):
        G.add_edge(fake_user, review_item_id)
        new_rec = make_rec(G, wl)
        hr_after = new_rec.calculate_hit_ratio(target_item, NUM_RECS)
        print 'hit-ratio (fake user reviews item {}): {}'.format(review_item_id, hr_after)
        G.del_edge(fake_user, review_item_id)

    for i in [2,4,6]:
        do_attack(i)
