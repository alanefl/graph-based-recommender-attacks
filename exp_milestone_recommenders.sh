#! /bin/bash

# Evaluates the three recommenders we've written on three datasets,
# According to what we did in the project milestone.

# Bring out the experiments.
cp milestone_experiments/exp_recommender_milestone.py .
cp milestone_experiments/exp_recommender_milestone_master.py .
python -u exp_recommender_milestone_master.py

# Clean up
mkdir -p milestone_rec_eval_results
mv *.milestone_recommender_eval milestone_rec_eval_results/
rm exp_recommender_milestone.py
rm exp_recommender_milestone_master.py

# Parse the results.
python milestone_experiments/exp_milestone_results_parser.py
