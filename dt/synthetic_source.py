import random
from .data_point import *
from .stat_tracker import *

"""
Represents a synthetic data source with seeded group probabilities. 
"""

class SyntheticSource:
    def __init__(self, num_groups, cost, weights):
        """
        @params:
            num_groups: the number of groups that data points may belong to
            cost: cost of sampling from this data source
            weights: an m-length array of weights for each group
        """
        self.num_groups = num_groups
        self.cost = float(cost)
        self.probs = [ w / sum(weights) for w in weights ]
        # The stat tracker which is ticked whenever the sample method is called
        self.sample_stats = StatTracker(num_groups)
        self.unique_sample_stats = StatTracker(num_groups)
        self.synthetic = True

    def __str__(self):
        s = "{Cost: " + str(self.cost)
        s += ", Probs: " + str(self.probs) + ")"
        return s

    def probability(self, group, method="gt", prior_weight=20):
        """
        Get the accurate or estimated probability of sampling a grpup from this
        data source. 
        @params
            group: the integer identifier for the group
            method: a string to specify the method used to compute probability
                "gt": the ground truth probability
                "sample": the sample probability
                "bayes": the Bayesian smoothed sample probability
            prior_weight: the weight that the Dirichlet prior should take (a+b)
        """
        if method == "gt-nodupe":
            return self.probs[group]
        elif method == "sample-nodupe":
            return self.sample_stats.prob(group)
        elif method == "bayes-nodupe":
            return self.sample_stats.bayes_prob(group, prior_weight)
        else:
            return self.probs[group]
    
    def sample(self):
        """
        @returns a uniformly random data point and updates sample_stats
        """
        group = random.choices(
            population = range(self.num_groups),
            weights = self.probs,
            k=1
        )[0]
        self.sample_stats.add_point(group)
        return DataPoint(group, random.randrange(9223372036854775807))
    
    def reset_sample(self):
        self.sample_stats = StatTracker(self.num_groups)

# Test cases
if __name__ == '__main__':
    source = SyntheticSource(2, 1.0, [0.8, 0.2])
    for i in range(101):
        if i % 10 == 0:
            print('i = ' + str(i))
            print("sampled point", source.sample())
            print("gt prob", source.probability(0))
            print("sample prob", source.probability(0, method="sample"))
            print("bayes prob", source.probability(0, method="bayes"))
            print()
