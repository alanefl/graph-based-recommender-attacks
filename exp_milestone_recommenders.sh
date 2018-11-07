#! /bin/bash

# Evaluates the three recommenders we've written on three datasets.
# Runs experiments forever, since the results are stochastic.

while :
do
    # Forever keep running these three experiments.
    python -u exp_milestone_eval_random_recommender.py  2>&1 | tee -a experiment_output.txt
    python -u exp_milestone_eval_popular_items_recommender.py  2>&1 | tee -a experiment_output.txt
    python -u exp_milestone_eval_pixie_recommender.py  2>&1 | tee -a experiment_output.txt
done
