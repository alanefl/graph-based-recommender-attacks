#! /bin/bash

# Evaluates the three recommenders we've written on several datasets.

# Bring out the experiments.
cp recommender_experiments/exp_recommender.py .
cp recommender_experiments/exp_recommender_master.py .
python -u exp_recommender_master.py

# Clean up
mkdir -p rec_eval_results
mv *.recommender_eval rec_eval_results/
rm exp_recommender.py
rm exp_recommender_master.py

# Parse the results.
python recommender_experiments/exp_results_parser.py
