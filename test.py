import numpy as np
import scipy.special
import mpmath

s = [np.random.default_rng().pareto(2, None) for i in range(1000000)]

print(np.mean(s))