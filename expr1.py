from dt import *

"""
EXPERIMENT 1: Synthetic source, equi-cost binary-group, binary source
IVs: P*1, P*2, minority-query-ratio
P*1 & P*2 varied by 0.1, 0.3, 0.5, 0.7, 0.9
Minority query ratio varied by 1% interval
Q = 1000, fixed
"""

total_query = 100
query_prob_increment = 1
probs = [0.1, 0.3, 0.5, 0.7, 0.9]
policies = ['random', 'coupcoll-nodupe', 'ratiocoll-nodupe', 'epsilon-exact-nodupe']
rep = 30

def create_synthetic_sources(p1, p2):
    ds1 = SyntheticSource(2, 1.0, [p1, 1 - p1])
    ds2 = SyntheticSource(2, 1.0, [1 - p2, p2])
    return [ds1, ds2]

def create_dt(p1, p2, g1_ratio):
    # Create data sources
    all_ds = create_synthetic_sources(p1, p2)
    # Compute query counts
    g1_query_count = int(round(total_query * g1_ratio))
    g2_query_count = total_query - g1_query_count
    query_counts = [g1_query_count, g2_query_count]
    # Create query
    query = StatTracker(2, initial_count = query_counts)
    # Create DT
    return DT(2, all_ds, query)

if __name__ == '__main__':
    """
    Output to stdout can easily be piped to csv. 
    """
    print("p1,p2,g1_ratio,policy,avg_cost")
    for p1 in probs:
        for p2 in probs:
            if p1 + p2 < 1.0:
                # Skip impossible combinations
                continue
            else:
                g1_prob = 0
                while g1_prob <= 100:
                    for policy in policies:
                        cost_sum = 0.0
                        for r in range(rep):
                            dt = create_dt(p1, p2, g1_prob * 0.01)
                            tc = dt.run(policy)
                            cost_sum += tc
                        avg_cost = cost_sum / rep
                        print(str(round(p1, 2)) + ',' + str(round(p2, 2)) + ',' + str(g1_prob) + ',' + policy + ',' + str(avg_cost))
                    g1_prob += query_prob_increment
