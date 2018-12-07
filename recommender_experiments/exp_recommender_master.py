import os
import subprocess

# Number of times to run each experiment for each setting
# e.g., for each setting of recommender, graph,
# and top_k_recommendations, select N randomly sampled entities
# to compute the recommender hit ratio on that entity.
N = 150

recommenders = ["pixie", "random", "popular"]

# The name of the ErdosRenyi graph is of the form
# ErdosRenyi_[num entities]_[num items]_[num edges]_[graph to draw edge weights from].
graphs = [

    # MovieLens. Evaluate threshold above 4.
    (4.0, "MovieLens"),

    # BeerAdvocate. Evaluate threshold above 4.
    (4.0, "BeerAdvocate"),

    # ER-MovieLens. Evaluate threshold above 4.
    (4.0, "ErdosRenyi_6040_3952_1000209_movielens"),

    # ER-BeerAdvocate. Evaluate threshold above 4.
    (4.0, "ErdosRenyi_33387_66051_1571251_beeradvocate")
]

top_k_recommendations = [10, 100, 1000]

pids = []
files = []
for recommender_name in recommenders:
    for min_threshold, graph_name in graphs:
        for k_recs in top_k_recommendations:

            filename = '-'.join(
                [recommender_name, graph_name, \
                    str(k_recs), str(N)]
            ) + '.recommender_eval'

            cmd = ["python", "-u", "exp_recommender.py", \
                    graph_name, recommender_name,str(k_recs), str(N), str(min_threshold)]

            outputfile = open(filename, "w")
            files.append(outputfile)

            print("Launched experiment with command: %s" % str(' '.join(cmd)))
            pids.append(
                subprocess.Popen(
                    ' '.join(cmd), shell=False, stdout=outputfile
                )
            )

print("Waiting for experiments to finish...")
for pid, file in zip(pids, files):
    pid.wait()
    file.close()

print("Done.")
