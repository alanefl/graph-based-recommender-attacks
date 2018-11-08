import subprocess

for attacker_name in ["Random", "Average", "Neighbor"]:
    for graph_name in ["ErdosRenyi", "Movielens", "BeerAdvocate"]:
        for percent_fake_entities in [0.005, 0.01, 0.03, 0.05]:
            for fake_reviews in [1, 2, 3, 4, 5, 6, 8, 10]:
                filename = '-'.join([attacker_name, graph_name, str(percent_fake_entities), str(fake_reviews)])
                with open(filename, "w") as out:
                    subprocess.Popen(
                        ["python", "exp_attacker_milestone.py", graph_name, str(percent_fake_entities), str(fake_reviews)],
                        stdout=out, stderr=out
                    )