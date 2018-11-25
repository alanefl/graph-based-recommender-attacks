import os
import subprocess

# Number of times to run each experiment for each setting
# e.g., for each setting of recommender, graph,
#  and top_k_recommendations, select N randomly sampled entities
#  to compute the recommender hit ratio on that entity.
N = 136

recommenders = ["pixie", "popular", "random"]

# The name of the ErdosRenyi graph is of the form
# ErdosRenyi_[num entities]_[num items]_[num edges].
graphs = ["MovieLens", "BeerAdvocate", "ErdosRenyi_6040_3952_1000209"]
top_k_recommendations = [10, 100, 1000]

pids = []
files = []
for recommender_name in recommenders:
    for graph_name in graphs:
        for k_recs in top_k_recommendations:

            filename = '-'.join(
                [recommender_name, graph_name, \
                    str(k_recs), str(N)]
            ) + '.milestone_recommender_eval'

            cmd = ["python", "-u", "exp_recommender_milestone.py", \
                    graph_name, recommender_name,str(k_recs), str(N)]

            outputfile = open(filename, "w")
            files.append(outputfile)

            print("Launched experiment with command: %s" % str(cmd))
            pids.append(
                subprocess.Popen(
                    cmd, shell=True, stdout=outputfile
                )
            )
            #os.system(cmd + " >> " + filename)

print("Waiting for experiments to finish...")
for pid, file in zip(pids, files):
    pid.wait()
    file.close()

print("Done.")
