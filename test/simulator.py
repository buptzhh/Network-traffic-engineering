import numpy
from config import Config
from flow import Flow
from load_balance import LoadBalanceMethod
from greedy import GreedyMethod
from cascara import Cascara
import numpy as np
import time
import matplotlib.pyplot as plt

TIME = 'a_month'


class Simulator:
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

    def process_a_slot(self):
        for linkname, link in self.link_dict.items():
            link.is_out_of_capacity = False
        # 当前flow分配流量顺序为site:0-9,app:0,1,2，即从要求高的开始分配
        for flowname, flow in self.flow_dict.items():
            line = flow.infile.readline()
            info = line.split(',')
            if line == '':
                break
            time_slot = int(info[0])
            download_traffic = float(info[1])
            upload_traffic = float(info[2])
            # choosed_links = self.method.choose_roads(flow.site, flow.app_config, download_traffic, upload_traffic,
            #                                          time_slot)  # 上下行混合
            # for linkname, utilization in choosed_links.items():
            #     self.link_dict[linkname].link_utilization[time_slot] += utilization[0] + utilization[1]
            choosed_links = self.method.choose_roads(flow.site, flow.app_config, download_traffic*2, 0,
                                                     time_slot)  # 只计算下行
            for linkname, utilization in choosed_links.items():
                self.link_dict[linkname].link_utilization[time_slot] += utilization
            # choosed_links = self.method.choose_roads(flow.site, flow.app_config, 0, upload_traffic,
            #                                          time_slot)  # 只计算上行
            # for linkname, utilization in choosed_links.items():
            #     self.link_dict[linkname].link_utilization[time_slot] += utilization[1]
            pass
        pass

    def rate_calculating(self):
        sum_cost = 0
        for link in self.link_dict:
            for i in range(int(Config.getConfig('timeInfo', TIME))):
                if link.link_utilization[i] <= link.base_capacity:
                    pass
        pass

    def calculate_link_p95(self, method):  # 计算各链路的P95利用
        links_p95 = {}
        for linkname, link in self.link_dict.items():
            sorted_utilization = sorted(link.link_utilization, reverse=True)
            links_p95[linkname] = sorted_utilization[432]
            x = range(8640)
            plt.plot(x, [link.base_capacity for i in range(8640)], marker=' ', mec='b', mfc='w',
                     label=u'y=base_capacity')
            plt.plot(x, [link.capacity for i in range(8640)], marker=' ', mec='b', mfc='w',
                     label=u'y=capacity')
            plt.plot(x, sorted_utilization, marker=' ', mec='b', mfc='w',
                     label=u'y=link utilization')
            plt.axvline(432, color='r', linestyle='--', label='p95 point')
            plt.legend()  # 让图例生效
            plt.xticks(np.arange(0, 8640, step=288))
            plt.margins(0.1)
            plt.subplots_adjust(bottom=0.15)
            plt.xlabel(u"time(5min time slot)")  # X轴标签
            plt.ylabel("traffic")  # Y轴标签

            plt.title("graph/" + method + "_method_ " + linkname + " ordered traffic (in)")  # 标题
            plt.savefig("graph/" + method + "_method" + linkname + ' ordered traffic (in).png')
            plt.show()
        return links_p95

    def calculate_cloud_p95(self):  # 计算各链路类型的总P95分位点
        links_p95 = {}
        cloud_p95 = {}
        cloud_utilization = {}
        for linkname, link in self.link_dict.items():
            sorted_utilization = sorted(link.link_utilization, reverse=True)
            links_p95[linkname] = sorted_utilization[432]
        for key, value in links_p95.items():
            if key[2:] not in cloud_p95:
                cloud_p95[key[2:]] = 0
            cloud_p95[key[2:]] += value
        sites_infeasiable = 0
        for sitename, site in self.site_dict.items():
            sites_infeasiable += sum(site.infeasible)
        print(sites_infeasiable)
        return cloud_p95

    def calculate_link_traffic(self, method):  # 计算各物理节点的链路的P95利用
        links_p95 = {}
        for sitename, site in self.site_dict.items():
            i = 1
            for linkname, link in site.links.items():
                sorted_utilization = sorted(link.link_utilization, reverse=True)
                links_p95[linkname] = sorted_utilization[432]
                x = range(8640)

                plt.subplot(1, len(site.links), i)
                i += 1
                plt.axhline(link.capacity,  linestyle='--', label='capacity')
                plt.axhline(link.base_capacity,  linestyle='--', label='base_capacity')
                plt.plot(x, link.link_utilization, marker=' ', mec='b', mfc='w',
                         label=u'y=link utilization')
                plt.axhline(links_p95[linkname], color='r', linestyle='--', label='p95 point')
                plt.legend()  # 让图例生效
                plt.margins(0.1)
                plt.subplots_adjust(bottom=0.15)
                plt.xlabel(u"time(5min time slot)")  # X轴标签
                plt.ylabel(linkname+" traffic")  # Y轴标签

                plt.xticks(np.arange(0, 8640, step=288), rotation=45)
                plt.title("graph/" + method + "_method_ " + linkname + " traffic (in)")  # 标题
            plt.savefig("graph/" + method + "_method" + sitename + ' traffic (in).png')
            plt.show()

if __name__ == "__main__":
    # method = LoadBalanceMethod()
    # method_name= 'balance'
    # method = GreedyMethod()
    # method_name = 'greedy'
    method = Cascara()
    method_name = 'cascara'
    simulator = Simulator(method)

    starttime = time.time()
    for i in range(int(Config.getConfig('timeInfo', TIME))):
        simulator.process_a_slot()
    endtime = time.time()
    print(endtime - starttime)

    simulator.calculate_link_traffic(method_name)
    print(simulator.calculate_cloud_p95())
    pass
