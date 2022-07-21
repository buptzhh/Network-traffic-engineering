import numpy as np
from link import Link
from app import App
from rdc_link import RDCLink
from site_ import Site
from config import Config
from base_method import BaseMethod


class Cascara(BaseMethod):
    def __init__(self):
        self.Cf = 0
        self.beta = 5

    def choose_roads(self, site, app_config, download_traffic, upload_traffic, time_slot):
        re_link = {}  # {linkname : [download_traffic, upload_traffic]}
        available_links = self.get_available_link(site=site, app_config=app_config)
        d = download_traffic + upload_traffic
        re_link = self.cascara_allocation(site=site, available_link=available_links, time_slot=time_slot,
                                          d=d)
        return re_link

    def cascara_allocation(self, site, available_link, d, time_slot):  # {linkname : rate}
        re_links_rate = {}
        sum_rest_cap = 0
        for linkname, link in available_link.items():
            link_rest_cap = link.p95_point - link.link_utilization[time_slot]
            if link_rest_cap >= 0:
                sum_rest_cap += link_rest_cap  # 根据剩余容量分配链路
            pass
        if sum_rest_cap < d:  # 需要使用freeslot或增加p95分位点
            for linkname, link in available_link.items():
                link_rest_cap = link.p95_point - link.link_utilization[time_slot]
                re_links_rate[linkname] = 0
                if link_rest_cap >= 0:
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
                link_rest_cap = link.p95_point - link.link_utilization[time_slot]
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
        min_capacity = float('inf')
        re_link = None
        for linkname, cost in available_augment_link.items():
            if 0 <= cost[0] < min_cost:
                min_cost = cost[0]
                min_capacity = cost[1]
                re_link = linkname
            if cost[0] == min_cost:
                if cost[1] < min_capacity:
                    min_capacity = cost[1]
                    re_link = linkname
        return re_link

    def link_augment(self, site, available_link, d, re_links_rate, time_slot):
        # 在这里记录超过最大带宽利用率的时间，和免费时间，超过最大带宽利用率的时间不能超过5%，即freetime <= outtime
        # 只有当链路的利用率+链路准备分配的流量大于p95分位点才做处理
        # 如果已经在使用免费时间，则直接分配，但不能超过物理上限
        # 如果还有免费时间，则使用免费时间
        # 如果没有免费时间了，且剩余可用最大带宽小于需求，则将可分配的流量都分配，且问题infeasible
        available_augment_link = {}  # {linkname : cost},得到可扩容的链路
        for linkname, link in available_link.items():
            if (link.p95_point < link.capacity) or link.free_times > 0 or link.is_out_of_capacity:
                 available_augment_link[linkname] = [link.free_times, link.capacity]
        while d > 0:
            augment_link = self.choose_augment_link(available_augment_link)  # 根据弹性链路的价格递增顺序选择弹性链路
            if augment_link is not None:
                link = available_link[augment_link]
                if available_link[augment_link].is_out_of_capacity:  # 链路已经以超出最大带宽运行,则尽量将流量分给该链路
                    if d + link.link_utilization[time_slot] + re_links_rate[augment_link] > link.capacity_upperbound:  # 不能以超出物理上限运行
                        available_link_rate = link.capacity_upperbound - link.link_utilization[time_slot] - \
                                              re_links_rate[augment_link]
                        d -= available_link_rate
                        re_links_rate[augment_link] += available_link_rate
                        available_augment_link[augment_link] = [-1, -1]
                    else:
                        re_links_rate[augment_link] += d
                        d = 0
                        break

                elif link.free_times > 0:
                    if d + link.link_utilization[time_slot] + re_links_rate[augment_link] > link.capacity_upperbound:  # 不能以超出物理上限运行
                        available_link_rate = link.capacity_upperbound - link.link_utilization[time_slot] - \
                                              re_links_rate[augment_link]
                        d -= available_link_rate
                        re_links_rate[augment_link] += available_link_rate
                        available_augment_link[augment_link] = [-1, -1]
                        link.is_out_of_capacity = True
                        link.is_out_of_capacity_times -= 1
                    else:
                        re_links_rate[augment_link] += d  # 这里没判定超过最大带宽次数，因为默认outtime < freetime
                        if re_links_rate[augment_link] + link.link_utilization[time_slot] > link.capacity:
                            link.is_out_of_capacity = True
                            link.is_out_of_capacity_times -= 1
                        d = 0
                        break
                else:  # 如果没有免费时间，则选择下一条链路， 这是因为优先选择使用freeslot
                    available_augment_link[augment_link] = [-1, -1]
            else:
                sum_rest_cap = 0
                for linkname, link in available_link.items():
                    if link.p95_point + self.beta <= link.capacity:
                        available_augment_link[linkname] = [link.variable_cost, link.capacity]
                    sum_rest_cap += link.capacity - re_links_rate[linkname] - link.link_utilization[time_slot]
                if sum_rest_cap < d:  # 全部链路的p95点都到了最大弹性带宽
                    site.infeasible[time_slot] += 1
                    for linkname, link in available_link.items():
                        re_links_rate[linkname] += link.capacity - re_links_rate[linkname] - link.link_utilization[time_slot]
                    break
                augment_link2 = self.choose_augment_link(available_augment_link)
                if augment_link2 ==None:  # 全部链路的p95点都到了最大弹性带宽
                    site.infeasible[time_slot] += 1
                    break
                available_link[augment_link2].p95_point += self.beta
                d -= self.beta
                re_links_rate[augment_link2] += self.beta
                if available_link[augment_link2].is_out_of_capacity_times > 0:
                    available_link[augment_link2].free_times = int(int(Config.getConfig('timeInfo', 'a_month')) * 0.05)
                    for u in range(len(available_link[augment_link2].link_utilization)):
                        if available_link[augment_link2].link_utilization[u] > available_link[augment_link2].p95_point:
                            available_link[augment_link2].free_times -= 1
            pass
        for linkname, link in available_link.items():
            if link.link_utilization[time_slot] + re_links_rate[linkname] > link.p95_point:
                link.free_times -= 1


class PRIORITYQUEUE:
    def __init__(self, site_dict):
        self.site_priority_queue = 0
