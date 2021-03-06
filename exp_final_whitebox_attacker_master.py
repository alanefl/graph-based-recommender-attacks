import os

for attacker_name in ["RandomAttacker", "AverageAttacker", "NeighborAttacker", "HighDegreeAttacker", "HillClimbingAttacker"]:
    for percent_fake_entities in [0.01, 0.05, 0.10]:
        for fake_reviews in [1, 2, 3, 5, 10]:
            filename = '-'.join([attacker_name, str(percent_fake_entities), str(fake_reviews)])
            cmd = ' '.join(["python", "exp_final_whitebox_attacker.py", str(percent_fake_entities), str(fake_reviews), attacker_name])
            os.system(cmd + " > " + filename + " &")
