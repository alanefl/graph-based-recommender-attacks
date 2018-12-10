import os

num_fake_reviews = '1'
for attacker_name in ["BlackBoxRWRAttacker"]:
    for percent_fake_entities in [0.01, 0.05, 0.10]:
        filename = '-'.join([attacker_name, str(percent_fake_entities)])
        cmd = ' '.join([
            "python", "exp_final_whitebox_attacker.py",
            str(percent_fake_entities), num_fake_reviews, attacker_name
        ])
        os.system(cmd + " > " + filename + " &")
