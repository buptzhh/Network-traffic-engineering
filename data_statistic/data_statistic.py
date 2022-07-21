import csv
import os
import numpy as np
import matplotlib.pyplot as plt
def read_up_and_down_flow(dir_path):
    file_paths = [name for name in os.listdir(dir_path)
                  if os.path.isfile(os.path.join(dir_path, name))]
    flow_dict = {}
    for file in file_paths:
        # if (file.split('.')[0] != 'flow_site_0_app_2'):
        #     continue
        flow_dict[file.split('.')[0]] = [[],[]]
        with open(os.path.join(dir_path, file),encoding="UTF-8",mode="r") as infile:
            infile.readline()
            for line in infile:
                info = line.split(',')
                time_slot = float(info[0])
                download_traffic = float(info[1])
                upload_traffic = float(info[2])
                flow_dict[file.split('.')[0]][0].append(download_traffic)
                flow_dict[file.split('.')[0]][1].append(upload_traffic)
    return flow_dict

def total_statistic(flow_dict):
    total_upload = []
    total_download = []
    for i in range(8640):
        total_download.append(0)
        total_upload.append(0)
    x = range(8640)
    for k, v in flow_dict.items():
        total_download = list_add(total_download, v[0])
        total_upload = list_add(total_upload, v[1])
    plt.plot(x, total_upload, marker=' ', mec='r', mfc='w', label=u'y=total_upload')
    plt.plot(x, total_download, marker=' ', mec='b', mfc='w', label=u'y=total_download')
    # plt.plot(x, [total_download[i]/total_upload[i] for i in range(8640)], marker=' ', mec='b', mfc='w', label=u'y=total_download/total_upload')
    # print([total_download[i]/total_upload[i] for i in range(8640)])
    count = 0
    for i in range(8640):
        if total_download[i] > total_upload[i]:
            count += 1
    print(count)
    plt.legend()  # 让图例生效
    plt.xticks(np.arange(0, 8640, step=288))
    plt.margins(0)
    plt.subplots_adjust(bottom=0.15)
    plt.xlabel(u"time(5min time slot)")  # X轴标签
    plt.ylabel("traffic")  # Y轴标签
    plt.title("total in and out traffic ")  # 标题
    plt.savefig('total in and out traffic.png')
    plt.show()

def each_app_statistic(flow_dict):
    apps = {}
    for k in flow_dict.keys():
        apps[k.split('_')[-2]+k.split('_')[-1]] = [[], []]
        pass
    for i in range(8640):
        for k, v in apps.items():
            v[0].append(0)
            v[1].append(0)
    for k, v in flow_dict.items():
        apps[k.split('_')[-2]+k.split('_')[-1]][0] = list_add(apps[k.split('_')[-2]+k.split('_')[-1]][0], v[0])
        apps[k.split('_')[-2] + k.split('_')[-1]][1] = list_add(apps[k.split('_')[-2] + k.split('_')[-1]][1], v[1])
    x = range(8640)
    for k,v in apps.items():
        plt.plot(x, v[0], marker=' ', mfc='w', label=u'y='+k+'in')
        plt.plot(x, v[1], marker=' ', mfc='w', label=u'y=' + k+'out')
        plt.legend()  # 让图例生效
        plt.xticks(np.arange(0, 8640, step=288))
        plt.margins(0)
        plt.subplots_adjust(bottom=0.15)
        plt.xlabel(u"time(5min time slot)")  # X轴标签
        plt.ylabel("traffic")  # Y轴标签
        plt.title(k+"site0 in and out traffic")  # 标题
        plt.savefig(k+' site0 in and out traffic.png')
        plt.show()

def each_site_statistic(flow_dict):
    apps = {}
    for k in flow_dict.keys():
        apps[k.split('_')[1]+k.split('_')[2]] = [[], []]
        pass
    for i in range(8640):
        for k, v in apps.items():
            v[0].append(0)
            v[1].append(0)
    for k, v in flow_dict.items():
        apps[k.split('_')[1]+k.split('_')[2]][0] = list_add(apps[k.split('_')[1]+k.split('_')[2]][0], v[0])
        apps[k.split('_')[1]+k.split('_')[2]][1] = list_add(apps[k.split('_')[1]+k.split('_')[2]][1], v[1])
    x = range(8640)
    for k,v in apps.items():
        plt.plot(x, v[0], marker=' ', mfc='w', label=u'y='+k+'in')
        plt.plot(x, v[1], marker=' ', mfc='w', label=u'y=' + k+'out')
        plt.legend()  # 让图例生效
        plt.xticks(np.arange(0, 8640, step=288))
        plt.margins(0)
        plt.subplots_adjust(bottom=0.15)
        plt.xlabel(u"time(5min time slot)")  # X轴标签
        plt.ylabel("traffic")  # Y轴标签
        plt.title(k+"in and out traffic")  # 标题
        plt.savefig(k+'in and out traffic.png')
        plt.show()

def list_add(l1,l2):
    if len(l1) == len(l2):
        return [l1[i]+l2[i] for i in range(len(l1))]

if __name__ == "__main__":
    dir_path = '../flow'
    total_statistic(read_up_and_down_flow(dir_path))
