class Site:
    def __init__(self, links=None):
        self.links = {}
        self.total_base_capacity = 0
        self.total_max_capacity = 0
        self.infeasible = None

    def add_link(self, linkname, link):
        self.links[linkname] = link

    def cal_total_capacity(self):
        for link in self.links.values():
            self.total_base_capacity += link.base_capacity
        for link in self.links.values():
            self.total_max_capacity += link.capacity
