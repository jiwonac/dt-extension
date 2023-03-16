from dt import *

"""
EXPERIMENT 2: Synthetic source, equi-cost binary-group, binary-source, initial query ratio follows ideal ratio. 
Change P*1 and P*2 from [0.1, 0.3, 0.5, 0.7, 0.9] ^ 2 while removing infeasible combinations. 
Q = 100, 1000, 10000, 100000, 1000000
"""

probs = [0.1, 0.3, 0.5, 0.7, 0.9]
query_counts = [32, 64, 128, 256, 512, 1024, 2048, 5096]
policies = ['random', 'coupcoll', 'ratiocoll', 'union-bound', 'asymptotic', 'epsilon-exact']
rep = 30

def create_synthetic_sources(p1, p2):
    ds1 = SyntheticSource(2, 1.0, [p1, 1 - p1])
    ds2 = SyntheticSource(2, 1.0, [1 - p2, p2])
    return [ds1, ds2]

def create_dt(p1, p2, total_query):
    all_ds = create_synthetic_sources(p1, p2)
    q1 = int(round((total_query * p1 / (p1 + p2)), 0))
    q2 = total_query - q1
    query = StatTracker(2, initial_count = [q1, q2])
    #print(query)
    dt = DT(2, create_synthetic_sources(p1, p2), query)
    return dt

if __name__ == '__main__':
    print("p1,p2,total_query,policy,avg_cost")
    for p1 in probs:
        for p2 in probs:
            if p1 + p2 < 1.0:
                continue # Impossible
            else:
                for total_query in query_counts:
                    for policy in policies:
                        if policy == 'union-bound':
                            dt = create_dt(p1, p2, total_query)
                            cost = union_bound(dt)
                            print(str(int(p1 * 100)) + ',' + str(str(int(p2 * 100))) + ',' + str(total_query) + ',' + policy + ',' + str(cost))
                        elif policy == 'asymptotic':
                            dt = create_dt(p1, p2, total_query)
                            cost = asymptotic_estimate(dt)
                            print(str(int(p1 * 100)) + ',' + str(str(int(p2 * 100))) + ',' + str(total_query) + ',' + policy + ',' + str(cost))
                        else:
                            cost_sum = 0.0
                            for r in range(rep):
                                dt = create_dt(p1, p2, total_query)
                                us, cs, tc = dt.run(policy)
                                cost_sum += tc
                                #print(tc)
                            avg_cost = cost_sum / rep
                            print(str(int(p1 * 100)) + ',' + str(str(int(p2 * 100))) + ',' + str(total_query) + ',' + policy + ',' + str(avg_cost))
