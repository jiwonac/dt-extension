import random
from .stat_tracker import *
from .data_point import *

"""
Represents a real-world data source containing instances of DataPoint. 
"""

class RealSource:
    def __init__(self, num_groups, cost):
        """
        @params
            num_groups: the number of groups that data points may belong to
            cost: cost of sampling from this data source
        """
        self.num_groups = num_groups
        self.cost = float(cost)
        self.data_points = []
        # The stat tracker which knows the ground truth of all groups
        self.gt_stats = StatTracker(num_groups)
        # The stat tracker which is ticked whenever the sample method is called
        self.sample_stats = StatTracker(num_groups)
        # Unlike sample_stats, this one keeps track of the non-duplicate
        # data points which were sampled
        self.unique_sample_stats = StatTracker(num_groups)
        self.synthetic = False
    
    def __len__(self):
        return len(self.data_points)
    
    def __getitem__(self, position):
        return self.data_sources[position]
    
    def __str__(self):
        s = "{Cost: " + str(self.cost) + ", Length: " + str(len(self))
        s += ", Stats: " + str(self.gt_stats) + ")"
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
        dupes = self.unique_sample_stats[group]
        if method == "gt-nodupe":
            return self.gt_stats.prob(group)
        elif method == "gt-dupe":
            return self.gt_stats.prob(group, dupes=dupes)
        elif method == "sample-nodupe":
            return self.sample_stats.prob(group)
        elif method == "sample-dupe":
            return self.sample_stats.prob(group, dupes=dupes)
        elif method == "bayes-nodupe":
            return self.sample_stats.bayes_prob(group, prior_weight)
        elif method == "bayes-dupe":
            return self.sample_stats.bayes_prob(group, prior_weight, dupes=dupes)
        else:
            return self.gt_stats.prob(group)
    
    def count(self, group):
        return self.gt_stats[group]

    def add_point(self, data_point):
        """
        @params
            data_point: a DataPoint with a valid group within range
        """
        self.data_points.append(data_point)
        self.gt_stats.add_point(data_point.group)
    
    def add_points(self, data_points):
        """
        @params
            data_points: a list-like of DataPoint instances
        """
        for data_point in data_points:
            self.add_point(data_point)

    def sample(self):
        """
        @returns a uniformly random data point and updates sample_stats
        """
        data_point = random.choice(self.data_points)
        self.sample_stats.add_point(data_point.group)
        return data_point

    def reset_sample(self):
        self.sample_stats = StatTracker(self.num_groups)

# Test cases
if __name__ == '__main__':
    source = RealSource(2, 1.0)
    source.add_point(DataPoint(0, ""))
    source.add_point(DataPoint(0, ""))
    source.add_point(DataPoint(0, ""))
    source.add_point(DataPoint(0, ""))
    source.add_point(DataPoint(1, ""))
    for i in range(101):
        if i % 10 == 0:
            print('i = ' + str(i))
            print("sampled point", source.sample())
            print("gt prob", source.probability(0))
            print("sample prob", source.probability(0, method="sample"))
            print("bayes prob", source.probability(0, method="bayes"))
            print()