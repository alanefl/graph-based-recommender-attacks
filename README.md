# Studying Graph Based Recommendation Systems under Adversarial Pressure
## CS224W @ Stanford, Fall 2018
---

## Overview

IMPORTANT: because SNAP.py uses Python 2.7, we use Python 2.7 in this
project as well.

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

- `*_exp.py`: experiment files.  To maintain some order on the
repo, make a new python file for each separate experiment you plan to run,
then run it as `python <experiment name>_exp.py` from `gbra/`. Add
all graphing code to its corresponding experiment file.
- Utility logic for each submodule lives in `gbra/util/<submodule>_utils.py`.
- Global utilities live at `gbra/utils/utils.py`.

## Quick Start

 1. Create a Python 2 virtual environment and activate it.
 2. Install SNAP from within that virtual environment
 3. `python sample_exp.py`
 4. Profit
