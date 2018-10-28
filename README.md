# Studying Graph Based Recommendation Systems under Adversarial Pressure
## CS224W @ Stanford, Fall 2018
---

## Overview

This repo houses code that experiments with how graph-based recommender systems
react under Adversarial pressure. We use a variant of the Pixie
algorithm to recommend items to users on
bipartite networks. Throughout our code we use the SNAP library
for common graph operations.

## Directory Structure

 - `gbra`: contains all our core code.  Any miscellaneous scripts
and documentation files live in the outer level of the repo.

    - `gbra/recommenders`: contains the recommender system black box.
    Recommender systems in this module can be instantiated on a graph, trained,
    evaluated, and asked for predictions.
    - `gbra/attackers`: contains different classes of attackers.
    - `gbra/data`: contains routines for fetching different datasets and
    instantiating them as graphs.
    - `gbra/feature_extraction`: contains classes and routines for extracting
    features from graphs.
    - `gbra/experiments`: experiment scripts.  To maintain some order on the
    repo, make a new python file for each separate experiment you plan to run,
    then run it as `python experiments/<experiment name>.py` from `gbra/`

- Utility logic for each submodule lives in `gbra/*/utils.py`.
- Utility logic shared across two or more submodules lives in `gbra/utils.py`.

## Quick Start

TODO
