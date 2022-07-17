import numpy as np
from link import Link
from app import App
from rdc_link import RDCLink
from site_ import Site
from config import Config
from base_method import BaseMethod
import copy


class LoadBalanceMethod(BaseMethod):
    def choose_roads(self, site, app_config, download_traffic, upload_traffic, time_slot):
        re_link = {}  # {linkname : [download_traffic, upload_traffic]}
        available_links = self.get_available_link(site=site, app_config=app_config)
        d = download_traffic + upload_traffic
        re_link = self.balance_flow(site=site, available_link=available_links, time_slot=time_slot,
                                    d=d)
        return re_link

    def balance_flow(self, site, available_link, d, time_slot):  # {linkname : rate}
        re_links_rate = {}
        sum_rest_cap = 0
        total_available_base_capacity = 0
        for linkname, link in copy.deepcopy(available_link).items():
            # link_rest_max_cap = link.capacity - link.link_utilization[time_slot]
            # if link_rest_max_cap >= 0:
            #     sum_rest_cap += link_rest_max_cap  # 根据剩余容量分配链路
            # pass
            if link.capacity - link.link_utilization[time_slot] == 0 and \
                    link.free_times <= 0 and link.is_out_of_capacity == False:  # 没有免费时间，且最大带宽已无法满足
                available_link.pop(linkname)
            else:
                total_available_base_capacity += link.base_capacity  # 计算总的链路容量

        for linkname, link in available_link.items():  # 直接分配链路流量比例
            re_links_rate[linkname] = d * (link.base_capacity / total_available_base_capacity)

        for linkname, link in available_link.items():
            if re_links_rate[linkname] > link.capacity - link.link_utilization[time_slot]:
                if link.is_out_of_capacity:  # 如果已经以超出最大带宽方式运行则不管
                    if re_links_rate[linkname] + link.link_utilization[time_slot] > link.capacity_upperbound:
                        re_links_rate[linkname] = link.capacity_upperbound - link.link_utilization[time_slot]
                        site.infeasible[time_slot] += 1
                    continue
                if link.free_times > 0:  # 如果还有免费时间，则使用免费时间
                    link.is_out_of_capacity = True
                    link.free_times -= 1
                    if re_links_rate[linkname] + link.link_utilization[time_slot] > link.capacity_upperbound:
                        re_links_rate[linkname] = link.capacity_upperbound - link.link_utilization[time_slot]
                        site.infeasible[time_slot] += 1
                if link.free_times <= 0:  # 如果已经没有免费时间，则问题infeasible
                    re_links_rate[linkname] = link.capacity - link.link_utilization[time_slot]
                    site.infeasible[time_slot] += 1
        return re_links_rate
        pass
