import os

for attacker_name in ["LowDegreeAttacker", "HighDegreeAttacker", "HillClimbingAttacker"]:
    for percent_fake_entities in [0.01, 0.03, 0.05, 0.10, 0.25, 0.50]:
        for fake_reviews in [1, 2, 3, 4, 5, 7, 10]:
            filename = '-'.join([attacker_name, str(percent_fake_entities), str(fake_reviews)])
            cmd = ' '.join(["python", "exp_final_whitebox_attacker.py", str(percent_fake_entities), str(fake_reviews), attacker_name])
            os.system(cmd + " > " + filename)
