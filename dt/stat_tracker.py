"""
A counter which keeps track of the number of data points that belong to each
group, either as ground truth or from sampling. 
"""

class StatTracker:
    def __init__(self, num_groups, initial_count=0):
        """
        @params
            num_groups: number of groups that data points may belong to
            initial_count: 
                if int: each group is initialized with the integer count
                if list: this list replaces the default count tracker
        """
        self.num_groups = num_groups
        # Switch based on count initialization
        if type(initial_count) == int:
            self.counts = [initial_count] * num_groups
            self.total_count = initial_count * num_groups
        elif type(initial_count) == list:
            self.counts = initial_count
            self.total_count = sum(initial_count)
    
    def __getitem__(self, group):
        return self.counts[group]
    
    def __str__(self):
        return str(self.counts)
    
    def __repr__(self):
        return str(self)
    
    def __len__(self):
        return self.total_count
    
    def add_point(self, group):
        """
        Increments the counter for the specified group. 
        """
        self.counts[group] += 1
        self.total_count += 1
    
    def decrement_point(self, group):
        self.counts[group] -= 1
        self.total_count -= 1
    
    def prob(self, group, dupes=0):
        """
        @returns the probability of a group's sampling chance
        """
        if self.total_count == 0:
            return -1
        else:
            net_count = self.counts[group] - dupes
            return net_count / self.total_count

    def bayes_prob(self, group, prior_weight, dupes=0):
        """
        @returns the smoothed probability of a group's sampling chance with a
                 uniform Dirichlet prior with specified weight
        """
        if self.total_count == 0:
            return -1
        else:
            a = prior_weight / (self.num_groups + 1)
            b = self.num_groups * prior_weight / (self.num_groups + 1)
            net_count = self.counts[group] - dupes
            return (net_count + a) / (self.total_count + b)

    def is_satisfied_by(self, other):
        """
        @returns whether self, interpreted as a query, is satisfied as a other,
                 interpreted as a count tracker
        """
        for group in range(self.num_groups):
            if self.counts[group] > other[group]:
                return False
        return True

# Test cases
if __name__ == '__main__':
    a = StatTracker(5)
    print(a)
    a.add_point(0)
    a.add_point(1)
    a.add_point(1)
    print(a)
    print(a[0])
    print(a[1])
    print(len(a))
    print(a.prob(0))
    print(a.bayes_prob(0, 10))
    b = StatTracker(5)
    print(b)
    print(b.is_satisfied_by(a))
    b.add_point(4)
    print(b)
    print(b.is_satisfied_by(a))
