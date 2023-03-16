from dt import *
import numpy as np

"""
"THE WALL" Experiment: Minorivy vs majority, uniform/random/skewed cost model, 
varying n, m. 
"""

total_query = 10000
policies = ['random', 'coupcoll-nodupe', 'ratiocoll-nodupe', 'epsilon-exact-nodupe', 'ucb']
policy_displayname = {
    'random': 'Random',
    'coupcoll-nodupe': 'CoupColl',
    'ratiocoll-nodupe': 'RatioColl',
    'epsilon-exact-nodupe': 'EpsilonGreedy',
    'ucb': 'UCB',
}
rep = 50
n_m_combos = [
    [2, 10],
    [4, 10],
    [6, 10],
    [8, 10],
    [10, 10],
    [10, 20],
    [10, 30],
    [10, 40],
    [10, 50]
]
group_counts = [2, 4, 6, 8, 10]
source_counts = [10, 200, 200, 400, 600, 800]

def zipf_expected_value(s, n):
    H_N = scipy.special.zeta(s, N)
    H_N_plus_one = scipy.special.zeta(s, N + 1)
    return H_N / (H_N_plus_one - 1)

# Assign costs according to specified cost model while keeping the average
# to equal to 1. For the Pareto distribution, mean = 1 when a = 2. 
# We also ensure that cost is never exactly 0.0
def assign_costs(n, cost_model):
    match cost_model:
        case "uniform":
            return [1.0] * n
        case "random":
            return [ 2 * (1 - random.random()) for i in range(n) ]
        case "skewed":
            return [np.random.default_rng().pareto(2, None) for i in range(n)]

# Split total value t into n
def random_split(t, n):
    subsets = [(1 - random.random()) for i in range(n)]
    subsets = [ x * t / sum(subsets) for x in subsets ]
    return subsets  

def nonzeros(list):
    cnt = 0
    for elem in list:
        if elem != 0:
            cnt += 1
    return cnt

# n = number of data sources
# m = number of groups
# majority = whether all groups have at least 1/m optimal probability, or
# if there is one source which has less than 1/m optimal proability
def create_prob_tables(n, m, majority):
    probs = [[0] * m for i in range(n)]
    if not majority: # One group is the minority
        # Ensure group 0 is the minority group
        for i in range(n):
            probs[i][0] = (1.0 - random.random()) * (1.0 / m) # (0, 1/m]
        start = 1
    else:
        start = 0
    i = 0 # Cycle through available data sources
    for j in range(start, m): # Ensure groups 1/0 ~ m-1 have prob. at least 1/m
        if nonzeros(probs[i]) == m - 1:
            probs[i][j] = 1.0 - sum(probs[i])
        else:
            probs[i][j] = 1.0 / m
        if i == n - 1: # Loop over data sources index to 0 if needed
            i = 0
        else:
            i += 1
    # Randomly split the remaining probabilities
    for i in range(n):
        remaining_cnt = len(probs[i]) - nonzeros(probs[i])
        remaining_prob = 1.0 - sum(probs[i])
        split = random_split(remaining_prob, remaining_cnt)
        k = 0
        for j in range(m):
            if probs[i][j] == 0:
                probs[i][j] = split[k]
                k += 1
    return probs

def create_synthetic_source(n, m, majority, cost_model):
    probs = create_prob_tables(n, m, majority)
    costs = assign_costs(n, cost_model)
    data_sources = []
    for i in range(n):
        data_sources.append(SyntheticSource(m, costs[i], probs[i]))
    return data_sources

def create_dt(n, m, majority, cost_model):
    all_ds = create_synthetic_source(n, m, majority, cost_model)
    query_counts = [int(total_query / m) for j in range(m)]
    query = StatTracker(m, initial_count=query_counts)
    return DT(m, all_ds, query)

if __name__ == '__main__':
    print("n,m,majority_distribution,cost_model,policy,avg_cost,avg_iters")
    for n_m in n_m_combos:
        n = n_m[0]
        m = n_m[1]
        for majority in [True, False]:
            for cost_model in ['uniform', 'random', 'skewed']:
                for policy in policies:
                    cost_sum = 0.0
                    iters_sum = 0
                    for r in range(rep):
                        dt = create_dt(n, m, majority, cost_model)
                        cost, iters = dt.run(policy)
                        cost_sum += cost
                        iters_sum += iters
                    avg_cost = cost_sum / rep
                    avg_iters = iters_sum / rep
                    print(str(n) + ',' + str(m) + ',' + str(majority) + ',' + cost_model + ',' + policy_displayname[policy] + ',' + str(avg_cost) + ',' + str(avg_iters))