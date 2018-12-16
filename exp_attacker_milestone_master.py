import subprocess

for attacker_name in ["Average"]:
    for graph_name in ["Movielens", "BeerAdvocate"]:
        for percent_fake_entities in [0.05]:
            for fake_reviews in [2, 3, 4, 5]:
                filename = '-'.join([attacker_name, graph_name, str(percent_fake_entities), str(fake_reviews)])
                cmd = ' '.join(["python", "exp_attacker_milestone.py", graph_name, str(percent_fake_entities), str(fake_reviews), attacker_name])
                subprocess.Popen(cmd + " > " + filename, shell=True)
