# Import lib
from gurobipy import *
import numpy as np
from link import Link
from app import App
from rdc_link import RDCLink
from site_ import Site
from flow import Flow
from config import Config
from base_method import BaseMethod

TIME = 'a_month'


class StaticMethod(BaseMethod):

    def __init__(self, method):
        self.site_dict = {}  # {sitename : Site}
        self.app_types = {}  # {appname : App}
        self.flow_dict = {}  # {flowname : Flow}
        self.link_dict = {}
        self.method = method
        self.init()

    def init(self):
        self.site_dict = Config.read_sites('network-3-23.csv')
        for sitename, site in self.site_dict.items():
            for linkname, link in site.links.items():
                print(linkname)
                link.link_utilization = np.zeros(int(int(Config.getConfig('timeInfo', TIME))))
                link.free_times = int(int(Config.getConfig('timeInfo', TIME)) * 0.05)
                link.is_out_of_capacity_times = link.free_times
                self.link_dict[linkname] = link
            site.infeasible = np.zeros(int(int(Config.getConfig('timeInfo', TIME))))
            site.cal_total_capacity()
        self.app_types = Config.read_app_types()
        flow_infile_dict = Config.get_flow_as_infile()
        for k, v in flow_infile_dict.items():
            self.flow_dict[k] = Flow(self.site_dict[k.split('_')[2]], self.app_types[k.split('_')[-1]], v)
        print(self.site_dict)
        print(self.app_types)
        print(self.flow_dict)

    def static_balance_traffic_allocation(self):
        # Create model
        model = Model()
        # Add decision variables to a model
        x = {}
        for flowname, flow in self.flow_dict.items():
            for linkname, link in self.get_available_link(site=flow.site, app_config=flow.app_config).keys():
                for time in range(int(Config.getConfig('timeInfo', TIME))):
                    name = flowname + '_' + linkname + '_' + str(time)
                    x[name] = model.addVar(lb=0, ub=1, vtype=GRB.BINARY, name=name, obj=0, column=None)
        for flowname, flow in self.flow_dict.items():  # 对每个流，添加各个
            x[flowname] = model.addVars(self.get_available_link(site=flow.site, app_config=flow.app_config).keys(),
                                        [i for i in range(int(Config.getConfig('timeInfo', TIME)))], vtype=GRB.BINARY,
                                        name='x_' + flowname)
            model.addConstrs(quicksum(x[flowname]) >= 1, name='c')
        for linkname, link in self.link_dict.items():
            model.addConstrs(quicksum(model.getVarByName('x_' + linkname)) <= link.link_utilization)  #
            ze = sorted()
            model.addConstrs(ze <= link.capacity)

        # Set objective function
        f1 = 0
        for linkname, link in self.link_dict.items():
            ze = None
            f1 += link.variable_cost * max(ze - link.base_capacity, 0)
        model.setObjective(f1, GRB.MINIMIZE)

        # Optimize
        model.optimize()
        # Print data
        if model.status == GRB.Status.OPTIMAL:
            pass

    def print_infeasible(self, model):
        """
        if model infeasible, print the infeasible constraints
        :param model:  Model,  Gurobi Model object
        :return: infeasible_list:  [str],  list of infeasible constraint names
        """

        model.computeIIS()

        infeasible_list = []
        for constr in model.getConstrs():
            if constr.IISConstr:
                print(constr.constrName)
                infeasible_list.append(constr.constrName)

        return infeasible_list
