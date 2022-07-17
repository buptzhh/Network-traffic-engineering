import numpy as np
class RDCLink:
    def __init__(self, site, cloud, latency, jitter, lost, base_capacity, capacity, fixed_cost, variable_cost, cap_upperbound):
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
        self.line_name = site + '_' + cloud
