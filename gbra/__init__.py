import snap
import numpy as np

# Seed the SNAP randomizer.
Rnd = snap.TRnd(1337)
Rnd.Randomize()

# Seed NumPy
np.random.seed(1337)
