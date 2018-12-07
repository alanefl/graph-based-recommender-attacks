"""Parses recommender evaluation results files.
"""

import os

EXP_DIRECTORY = "rec_eval_results"

experiment_sums = {}
experiment_counts = {}

for filename in os.listdir(EXP_DIRECTORY):
    if filename.endswith(".recommender_eval"):
        full_path = os.path.join(EXP_DIRECTORY, filename)
        with open(full_path, "r") as results_file:
            for line in results_file:
                line = line.strip()
                graph_pair, num_recs_pair, score_pair, recommender_pair, iter_pair = line.split(",")
                graph_name = graph_pair.split(":")[1]
                num_recs = int(num_recs_pair.split(":")[1])
                score = float(score_pair.split(":")[1])
                recommender = recommender_pair.split(":")[1]
                iteration = int(iter_pair.split(":")[1])

                experiment_id = (graph_name, num_recs, recommender)

                if experiment_id not in experiment_sums:
                    experiment_sums[experiment_id] = 0
                if experiment_id not in experiment_counts:
                    experiment_counts[experiment_id] = 0

                experiment_sums[experiment_id] += score
                experiment_counts[experiment_id] += 1

for k, v in experiment_sums.items():
    print("Experiment: %s, average recommender hit ratio: %f" % (
        str(k), v / float(experiment_counts[k])
    ))
