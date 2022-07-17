import os
import configparser
from link import Link
from app import App
from rdc_link import RDCLink
from site_ import Site

class Config:
    @staticmethod
    def getConfig(section, key=None):
        config = configparser.ConfigParser()  # 初始化一个configparser类对象
        dir = os.path.dirname(__file__)  # 获取当前文件的文件夹位置
        file_path = os.path.join(dir, 'config.ini')  # 完整的config.ini文件路径
        config.read(file_path, encoding='utf-8')  # 读取config.ini文件内容
        if key != None:
            return config.get(section, key)  # 获取某个section下面的某个key的值
        else:
            return config.items(section)  # 或者某个section下面的所有值

    @staticmethod
    def read_a_flow_all_data(filename):  # 返回某一个流的数据
        flow_dict = [[], []]
        with open(os.path.join(Config.getConfig('url', 'flow_url'), filename), encoding="UTF-8", mode="r") as infile:
            infile.readline()
            for line in infile:
                info = line.split(',')
                time_slot = float(info[0])
                download_traffic = float(info[1])
                upload_traffic = float(info[2])
                flow_dict[0].append(download_traffic)
                flow_dict[1].append(upload_traffic)
        return flow_dict

    @staticmethod
    def read_links(filename):  # {linkname : Link}
        link_dict = {}
        with open(os.path.join(Config.getConfig('url', 'network_url'), filename), encoding="UTF-8", mode="r") as infile:
            infile.readline()
            for line in infile:
                info = line.split(',')
                site = info[0]
                if site == 'RDC':
                    continue
                cloud = info[1]
                latency = int(info[2])
                jitter = int(info[3])
                lost = float(info[4])
                base_capacity = int(info[5])
                capacity = int(info[6])
                fixed_cost = int(info[7])
                variable_cost = int(info[8])
                capacity_upperbound = int(info[9][:-1])
                linkname = site + '_' + cloud
                link = Link(site, cloud, latency, jitter, lost, base_capacity, capacity, fixed_cost, variable_cost,
                            capacity_upperbound)
                link_dict[linkname] = link
        return link_dict

    @staticmethod
    def read_rdc_links(filename):  # {linkname : Link}
        link_dict = {}
        with open(os.path.join(Config.getConfig('url', 'network_url'), filename), encoding="UTF-8", mode="r") as infile:
            infile.readline()
            for line in infile:
                info = line.split(',')
                site = info[0]
                if site != 'RDC':
                    continue
                cloud = info[1]
                latency = int(info[2])
                jitter = int(info[3])
                lost = float(info[4])
                base_capacity = int(info[5])
                capacity = int(info[6])
                fixed_cost = int(info[7])
                variable_cost = int(info[8])
                capacity_upperbound = info[9]
                linkname = site + '_' + cloud
                link = Link(site, cloud, latency, jitter, lost, base_capacity, capacity, fixed_cost, variable_cost,
                            capacity_upperbound)
                link_dict[linkname] = link
        return link_dict

    @staticmethod
    def get_flow_as_infile():  # 返回各个流的读文件
        flow_infile_dict = {}
        files = [name for name in os.listdir(Config.getConfig('url', 'flow_url'))
                 if os.path.isfile(os.path.join(Config.getConfig('url', 'flow_url'), name))]
        for file in files:
            infile = open(os.path.join(Config.getConfig('url', 'flow_url'), file), encoding="UTF-8", mode="r")
            infile.readline()
            flow_infile_dict[file.split('.')[0]] = infile
        return flow_infile_dict

    @staticmethod
    def read_app_types():  # 返回{app_type : app}
        app_dict = {}
        with open(Config.getConfig('url', 'app_sla_url'), encoding="UTF-8", mode="r") as infile:
            infile.readline()
            for line in infile:
                info = line[:-1].split(',')
                type = info[0]
                latency = int(info[1])
                jitter = int(info[2])
                lost = float(info[3])
                app = App(type, latency, jitter, lost)
                app_dict[type] = app
        return app_dict

    @staticmethod
    def read_sites(filename):  # 返回 {sitename : site}
        links = Config.read_links(filename)
        sites_dict = {}
        for linkname, link in links.items():
            if link.site == "RDC":
                continue
            if link.site not in sites_dict:
                sites_dict[link.site] = Site()
            sites_dict[link.site].add_link(linkname, link)
        return sites_dict