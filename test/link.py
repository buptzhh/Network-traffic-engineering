import numpy as np


class Link:
    def __init__(self, site, cloud, latency, jitter, lost, base_capacity, capacity, fixed_cost, variable_cost,
                 cap_upperbound):
        self.site = site
        self.cloud = cloud
        self.latency = latency
        self.jitter = jitter
        self.lost = lost
        self.base_capacity = base_capacity
        self.capacity = capacity
        self.fixed_cost = fixed_cost
        self.variable_cost = variable_cost
        self.capacity_upperbound = cap_upperbound
        self.link_name = site + '_' + cloud
        self.link_utilization = None
        self.link_augment = None
        self.free_times = 0
        self.base_marginal_cost = base_capacity / fixed_cost
        self.is_out_of_capacity = False
        self.is_out_of_capacity_times = 0
        self.p95_point = base_capacity
