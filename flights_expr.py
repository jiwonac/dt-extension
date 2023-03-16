from dt import *
import pickle

"""
FLIGHTS EXPERIMENT: The flights dataset, equi-cost, uniform requirements. 
IVs: Algorithm used, duplicate protection ON/OFF
Q_i = 10,000 for each group
"""

query_counts = [10, 100, 1000, 10000]
policies = ['random', 'coupcoll-nodupe', 'ratiocoll-nodupe', 'epsilon-exact-nodupe', 'coupcoll-dupe', 'ratiocoll-dupe', 'epsilon-exact-dupe', 'ucb']
#policies = ['ucb-exact-dupe']
reps = 5
num_groups = 51

def load_sources():
    with open("data/flights_sources.pickle", "rb") as f:
        return pickle.load(f)

def create_dt(query_count):
    query_counts = [query_count] * num_groups
    query = StatTracker(num_groups, initial_count = query_counts)
    return DT(num_groups, load_sources(), query)

if __name__ == '__main__':
    print("query_per_group,policy,avg_cost,avg_iters")
    for query_count in query_counts:
        for policy in policies:
            cost_sum = 0.0
            iter_sum = 0
            for rep in range(reps):
                dt = create_dt(query_count)
                tc, iters = dt.run(policy)
                cost_sum += tc
                iter_sum += iters
            avg_cost = cost_sum / reps
            avg_iters = iter_sum / reps
            print(str(query_count) + ',' + policy + ',' + str(avg_cost) + ',' + str(avg_iters))