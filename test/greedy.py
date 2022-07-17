import numpy as np
from link import Link
from app import App
from rdc_link import RDCLink
from site_ import Site
from config import Config
from base_method import BaseMethod


class GreedyMethod(BaseMethod):
    def choose_roads(self, site, app_config, download_traffic, upload_traffic, time_slot):
        re_link = {}  # {linkname : [download_traffic, upload_traffic]}
        available_links = self.get_available_link(site=site, app_config=app_config)
        d = download_traffic + upload_traffic
        re_link = self.greedy_allocation(site=site, available_link=available_links, time_slot=time_slot,
                                         d=d)
        return re_link

    def greedy_allocation(self, site, available_link, d, time_slot):  # {linkname : rate}
        re_links_rate = {}
        sum_rest_cap = 0
        for linkname, link in available_link.items():
            link_rest_cap = link.base_capacity - link.link_utilization[time_slot]
            if link_rest_cap >= 0:
                sum_rest_cap += link_rest_cap  # 根据剩余容量分配链路
            pass
        if sum_rest_cap < d:  # 需要使用弹性带宽
            for linkname, link in available_link.items():
                link_rest_cap = link.base_capacity - link.link_utilization[time_slot]
                re_links_rate[linkname] = link_rest_cap
            d -= sum_rest_cap  # 先将容量分配到可用的链路

            self.link_augment(site, available_link, d, re_links_rate, time_slot)
        else:
            ordered_available_link = dict(
                sorted(available_link.items(), key=lambda x: (x[1].fixed_cost / x[1].base_capacity), reverse=False))
            # key=lambda x: (x[1].fixed_cost / x[1].base_capacity), reverse=False))
            for linkname, link in ordered_available_link.items():  # 直接分配
                # print('\n' + linkname + " "+ str(d))
                # print(link.fixed_cost/link.base_capacity)
                if d == 0:  # 存在download_traffic + upload_traffic==0的情况，所以d==0判定要放在前面
                    break
                link_rest_cap = link.base_capacity - link.link_utilization[time_slot]
                if link_rest_cap >= d:
                    re_links_rate[linkname] = d
                    d = 0
                    break
                else:
                    re_links_rate[linkname] = link_rest_cap
                    d -= link_rest_cap
        return re_links_rate
        pass

    # 1. 根据剩余容量比例进行流量负担均衡or根据基础容量？
    # 2. 如何选择弹性链路
    # 3. 弹性浮动成本如何计算

    def choose_augment_link(self, available_augment_link):
        min_cost = float('inf')
        re_link = None
        for linkname, cost in available_augment_link.items():
            if 0 < cost < min_cost:
                min_cost = cost
                re_link = linkname
        return re_link

    def link_augment(self, site, available_link, d, re_links_rate, time_slot):
        available_augment_link = {}  # {linkname : cost},得到可扩容的链路
        for linkname, link in available_link.items():
            if (link.variable_cost != 0 and link.link_utilization[time_slot] < link.capacity) \
                    or link.free_times > 0 or link.is_out_of_capacity:
                available_augment_link[linkname] = link.variable_cost
        while d > 0:
            augment_link = self.choose_augment_link(available_augment_link)  # 根据弹性链路的价格递增顺序选择弹性链路
            if augment_link is not None:
                link = available_link[augment_link]
                if available_link[augment_link].is_out_of_capacity:  # 链路已经以超出最大带宽运行
                    if d + link.link_utilization[time_slot] > link.capacity_upperbound:  # 不能以超出物理上限运行
                        re_links_rate[augment_link] += link.capacity_upperbound - link.link_utilization[time_slot]
                        d -= link.capacity_upperbound - link.link_utilization[time_slot]
                        available_augment_link[augment_link] = -1
                    else:
                        re_links_rate[augment_link] += d
                        d = 0
                        break

                available_augment_cap = link.capacity - link.link_utilization[time_slot]
                if available_augment_cap >= d:  # 如果最大带宽可满足，则使用最大带宽
                    re_links_rate[augment_link] += d
                    d = 0
                    break
                elif link.free_times > 0:
                    link.free_times -= 1
                    link.is_out_of_capacity = True
                    if d + link.link_utilization[time_slot] > link.capacity_upperbound:  # 不能以超出物理上限运行
                        re_links_rate[augment_link] += link.capacity_upperbound - link.link_utilization[time_slot]
                        d -= link.capacity_upperbound - link.link_utilization[time_slot]
                        available_augment_link[augment_link] = -1
                    else:
                        re_links_rate[augment_link] += d
                        d = 0
                        break
                else:  # 如果没有免费时间，且最大带宽也满足不了，则选择下一条链路
                    re_links_rate[augment_link] += available_augment_cap
                    d -= available_augment_cap
                    available_augment_link[augment_link] = -1
            else:
                site.infeasible[time_slot] += 1
            pass
