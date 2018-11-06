"""Utlities for probability/math operations"""

import random

def weighted_choice(seq, weights, weight_sum):
    """https://scaron.info/blog/python-weighted-choice.html
    Returns a random element in seq weighted by "weights".
    """
    assert len(weights) == len(seq)

    x = random.random() * weight_sum
    for i, elmt in enumerate(seq):
        if x <= weights[i]:
            return elmt
        x -= weights[i]
    # Not reached.
