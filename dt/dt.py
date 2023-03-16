import random
import math
from .stat_tracker import *
from .utils import *

"""
Represents a single instance of the DT problem. 
In other words, implements (D, G, C, Q) as a class. 
Implements the random, CoupColl, RatioColl, and EpsilonGreedy algorithms via 
the run() function that runs specified algorithm and returns the results. 
"""

class DT:
    def __init__(self, num_groups, data_sources, query):
        """
        @params
            num_groups: number of groups in data sources
            data_sources: an iterable of RealSource or SyntheticSource instances
            query: a StatTracker with the desired count
        """
        self.num_groups = num_groups
        self.data_sources = data_sources
        self.query = query
    
    def __str__(self):
        s = "Query: " + str(self.query) + "\n"
        return s + "Dataset: " + str(self.data_sources)
    
    def remaining_query(self, group):
        return max(0, self.query[group] - self.collected_stats[group])
    
    def unsatisfied_groups(self):
        """
        @returns a list of group indices whose query is not satisfied
        """
        return [ g for g in range(self.num_groups) 
                 if self.query[g] > self.collected_stats[g] ]
    
    def run(self, policy):
        # Reset any sampling counts already attached to data source
        for data_source in self.data_sources:
            data_source.reset_sample()
        # Reset/initialize variables used
        self.unified_set = set()
        self.collected_stats = StatTracker(self.num_groups)
        self.total_cost = 0.0
        # Run the chosen algorithm
        iteration = 0 # Used for epsilon greedy
        while not self.query.is_satisfied_by(self.collected_stats):
            selected_source = self.select(policy, iteration)
            new_point = selected_source.sample()
            if new_point not in self.unified_set:
                self.unified_set.add(new_point)
                self.collected_stats.add_point(new_point.group)
                selected_source.unique_sample_stats.add_point(new_point.group)
            self.total_cost += selected_source.cost
            iteration += 1
            #print(self.remaining_queries_csv(iteration))
        return self.total_cost, iteration
    
    def select(self, policy, iteration):
        if policy == "random":
            return random.choice(self.data_sources)
        elif policy == "coupcoll-nodupe":
            return self.select_coupcoll(dupe=False)
        elif policy == "coupcoll-dupe":
            return self.select_coupcoll(dupe=True)
        elif policy == "ratiocoll-nodupe":
            return self.select_ratiocoll(dupe=False)
        elif policy == "ratiocoll-dupe":
            return self.select_ratiocoll(dupe=True)
        elif policy == "epsilon-exact-nodupe":
            return self.select_epsilongreedy(iteration, bayes=False, dupe=False)
        elif policy == "epsilon-exact-dupe":
            return self.select_epsilongreedy(iteration, bayes=False, dupe=True)
        elif policy == "epsilon-bayes-nodupe":
            return self.select_epsilongreedy(iteration, bayes=True, dupe=False)
        elif policy == "epsilon-bayes-dupe":
            return self.select_epsilongreedy(iteration, bayes=False, dupe=True)
        elif policy ==  "ucb":
            return self.select_ucb(iteration)
    
    def group_score(self, group, prob_method="gt-nodupe", prior_weight=20.0):
        """
        Computes group score defined as:
            min_{forall D_i \in D}(C_i / P(G_j | D_i))
        for the specified group using the specified probability compute method. 
        """
        def cost_of_group_in_source(data_source):
            """
            @returns C_i / P(G_j | D_i)
            """
            prob = data_source.probability(group, method=prob_method, 
                                           prior_weight=prior_weight)
            if prob == 0.0:
                return float('inf')
            else:
                return data_source.cost / prob
        scores_by_source = [ cost_of_group_in_source(data_source)
                             for data_source in self.data_sources ]
        return min(scores_by_source)
    
    def group_maximizing_source(self, group, prob_method="gt-nodupe", prior_weight=20.0):
        """
        @returns the data source which maximizes the expected cost of sampling
                 the specified group
        """
        expected_costs = { ds : ds.probability(group, method=prob_method,
                           prior_weight=prior_weight) / ds.cost
                           for ds in self.data_sources }
        return argmax(expected_costs)

    def select_coupcoll(self, dupe=False):
        unsatisfied_groups = self.unsatisfied_groups()
        if dupe:
            prob_method = "gt-dupe"
        else:
            prob_method = "gt_nodupe"
        group_scores = { g : self.group_score(g, prob_method=prob_method) 
                        for g in unsatisfied_groups }
        chosen_group = argmax(group_scores)
        chosen_ds = self.group_maximizing_source(chosen_group, prob_method=prob_method)
        return chosen_ds
    
    def select_ratiocoll(self, dupe=False):
        unsatisfied_groups = self.unsatisfied_groups()
        if dupe:
            prob_method = "gt-dupe"
        else:
            prob_method = "gt-nodupe"
        group_scores = { g : self.remaining_query(g) * self.group_score(g, 
                        prob_method=prob_method) for g in unsatisfied_groups }
        #for g in unsatisfied_groups:
        #    print(str(g), str(self.remaining_query(g)), str(self.group_score(g)), str(self.remaining_query(g) * self.group_score(g)))
        chosen_group = argmax(group_scores)
        chosen_ds = self.group_maximizing_source(chosen_group, prob_method=prob_method)
        #print(chosen_group, chosen_ds)
        #print(str(chosen_group), chosen_ds)
        return chosen_ds

    def select_dualcoll(self):
        group_scores = {g : self.remaining_query(g) * self.group_score(g) for g in range(self.num_groups)}
        ds_scores = { ds : sum([ ds.probability(g) * group_scores[g] for g in range(self.num_groups) ]) for ds in self.data_sources }
        chosen_ds = argmax(ds_scores)
        return chosen_ds
    
    def select_epsilongreedy(self, iteration, bayes=False, dupe=False): # Change prob method
        r = random.random()
        if bayes:
            if dupe:
                prob_method = "bayes-dupe"
            else:
                prob_method = "bayes-nodupe"
        else:
            if dupe:
                prob_method = "sample-dupe"
            else:
                prob_method = "sample-nodupe"
        if (iteration < len(self.data_sources)):
            return self.data_sources[iteration]
        elif (r <= math.pow(math.log(iteration) / iteration, 1/3)): # Explore
            return random.choice(self.data_sources)
        else: # Exploit
            unsatisfied_groups = self.unsatisfied_groups()
            group_scores = { g : self.remaining_query(g) * self.group_score(g, 
                             prob_method=prob_method) for g in unsatisfied_groups }
            chosen_group = argmax(group_scores)
            return self.group_maximizing_source(chosen_group, prob_method=prob_method)
    
    def select_ucb(self, iteration):
        # Memoize total counts for each group
        if iteration == 0:
            total_group_counts = [0] * self.num_groups
            total_count = 0
            for g in range(self.num_groups):
                for ds in self.data_sources:
                    if ds.synthetic: # Synthetic DS doesn't have a "count"
                        count = ds.probability(g)
                    else:
                        count = ds.count(g)
                    total_group_counts[g] += count
                    total_count += count
            self.ucb_rewards = [ total_count / total_group_counts[j] for j in range(self.num_groups) ]
        # Initialization rounds
        if iteration < len(self.data_sources):
            return self.data_sources[iteration]
        else:
            # Estimated reward from each data source
            unsatisfied_groups = self.unsatisfied_groups()
            avg_rewards = [ 1.0 / (len(ds.sample_stats) * ds.cost) for ds in self.data_sources ]
            for i in range(len(self.data_sources)):
                mult = 1.0
                for group in unsatisfied_groups:
                    ds = self.data_sources[i]
                    mult += (ds.sample_stats[group]) / self.ucb_rewards[group]
                avg_rewards[i] *= mult
            # UCB logic
            rewards_range = max(avg_rewards) - min(avg_rewards)
            upper_bounds = { ds : avg_rewards[ds] + rewards_range * math.sqrt(2 
                * math.log(iteration) / len(self.data_sources[ds].sample_stats)) for ds in range(len(self.data_sources)) }
            #print(avg_rewards, upper_bounds)
            chosen_ds = argmax(upper_bounds)
            return self.data_sources[chosen_ds]

    def remaining_queries_csv(self, iteration):
        s = str(iteration) + ","
        g = 0
        while g < self.num_groups:
            s += str(self.remaining_query(g))
            if g != self.num_groups - 1:
                s += ","
            g += 1
        return s