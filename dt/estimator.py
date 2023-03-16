import math

"""
Contains functions which compute the Union Bound and the asymptotic estimate when parameters are specified.
"""

def union_bound(dt):
    ret = 0.0
    for group in range(dt.num_groups):
        estimate = dt.query[group]
        estimate *= dt.group_score(group, "gt") 
        ret += estimate
    return ret

def asymptotic_estimate(dt):
    q = len(dt.query)
    optimal_probs = []
    for group in range(dt.num_groups):
        prob_by_source = [ ds.probability(group) for ds in dt.data_sources ]
        optimal_probs.append(max(prob_by_source))
    c = sum(optimal_probs) / math.sqrt(2 * math.pi * math.prod(optimal_probs))
    return q + math.sqrt(q) * c
