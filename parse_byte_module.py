#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import sys
import datetime

sizes = {}
rates = {}
size_type = {}
size_module = {}
size_file = {}
rate_type = {}
rate_module = {}
rate_file = {}

def switch_type(str):
    if str == 'INFO':
        return str
    elif str == 'WARN':
        return str
    elif str == 'TRACE':
        return str
    elif str == 'DEBUG':
        return str
    elif str == 'ERROR':
        return str
    else:
        return ""

def get_type(line):
    str_list = line.split(' ')
    if len(str_list) < 3:
        return ""
    type_str = str_list[2]
    type_ = switch_type(type_str)
    return type_
    
def get_module(line):
    module_str = line.split(' ')[4]
    if not module_str.startswith('['):
        return ""
    if not module_str.endswith(']'):
        return ""
    module_str = module_str[1:len(module_str)-1]
    return module_str

def get_file(line):
    file_str = re.search(r'[a-z_]+\.[a-z]+:[1-9][0-9]*', line, 0)
    if file_str == None:
        return ""
    file_str = file_str.group()
    return file_str

def get_time(line):
    time_str = line.split(' ')[0] + ' ' + line.split(' ')[1]
    time_str = time_str[1:len(time_str) - 1]
    try:
        time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        time = None
    return time

def read_file(file_, start_time = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), end_time = datetime.datetime.now()):
    print("select from [%s] to [%s]" % (start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S")))
    # 初始化
    sizes["blank_size"] = 0
    sizes["no_type"]   = 0
    sizes["log_size"]   = 0
    sizes["sum_size"]  = 0
    time_flag = False
    if start_time == datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"):
        time_flag = True
    # 打开文件
    fr=open(file_,'r')
    # 读取文件所有行
    content=fr.readlines()

    # 依次迭代所有行
    for line in content:
        # 去除空格
        size = len(line)
        line = line.strip()
        # 如果满足时间条件
        if time_flag:
            sizes["sum_size"] += size
            # 如果是空行，则跳过
            if len(line)==0:
                sizes["blank_size"] += size
                continue
        log_type = get_type(line)
        if time_flag:
            # 如果没有类型，则跳过
            if log_type == "":
                sizes["no_type"] += size
                continue
        log_time = get_time(line)
        if log_time == None:
            continue
        # 小于时间区域，不记录
        if log_time < start_time:
            continue
        # 大于时间区域，直接返回
        elif log_time > end_time:
            sizes["sum_size"] -= size
            return True
        if not time_flag:
            sizes["sum_size"] += size
        time_flag = True
        sizes["log_size"] += size
        if log_type not in size_type.keys():
            size_type[log_type] = size
        else:
            size_type[log_type] += size

        module_name = get_module(line)
        if module_name not in size_file.keys():
            size_file[module_name] = {}
        if module_name not in size_module.keys():
            size_module[module_name] = size
        else:
            size_module[module_name] += size

        file_name = get_file(line)
        if file_name == "":
            continue
        if file_name not in size_file[module_name].keys():
            size_file[module_name][file_name] = size
        else:
            size_file[module_name][file_name] += size

    fr.close()

def cal_rate():
    global size_module_s
    global size_file_s
    size_file_s = {}
    size_module_s = sorted(size_module, cmp=lambda x,y:cmp(size_module[x],size_module[y]), reverse=True)
    sum_ = float(sizes["sum_size"])
    if sum_ == 0:
        return False
    for item in sizes:
        rates[item] = (float(sizes[item]) / sum_) * 100
    for module in size_module_s:
        rate_module[module] = (float(size_module[module]) / sum_) * 100
        rate_file[module] = {}
        size_file_s[module] = sorted(size_file[module], cmp=lambda x,y:cmp(size_file[module][x],size_file[module][y]), reverse=True)
        for file_ in size_file[module]:
            rate_file[module][file_] = (float(size_file[module][file_]) / sum_) * 100


def print_result():
    print("[parse result]")
    if sizes["sum_size"] == 0:
        print("no log meets the condition")
        return False
    print("size     rate     module/file")
    item = "sum_size"
    print('%-10d  %6.2f%%  %s' % (sizes[item], rates[item], item))
    for item in sizes:
        if item == "sum_size":
            continue
        print('%-10d  %6.2f%%  %s' % (sizes[item], rates[item], item))
    print("")
    n1 = 0
    for module in size_module_s:
        n1 += 1
        if n1 > 10:
            break
        if rate_module[module] < 0.1:
            break
        if module == "":
            print('%-10d  %6.2f%%  (no mudule)' % (size_module[module], rate_module[module]))
        else:
            print('%-10d  %6.2f%%  [%s]' % (size_module[module], rate_module[module], module))
        n2 = 0
        for file_ in size_file_s[module]:
            n2 += 1
            if n2 > 10:
                break
            if rate_file[module][file_] < 0.1:
                break
            print('  %-10d%6.2f%%  %s'% (size_file[module][file_], rate_file[module][file_], file_))
        print("")

if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 4:
        print("invalid arguments! please input like this:\n"
              "python parse.py log_file_path [xxxx-xx-xx-xx:xx:xx] [xxxx-xx-xx-xx:xx:xx]")
        exit(-1)
    print("start parse\n")
    if len(sys.argv) == 2:
        read_file(sys.argv[1])
    else:
        start_time = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d-%H:%M:%S")
        end_time = datetime.datetime.strptime(sys.argv[3], "%Y-%m-%d-%H:%M:%S")
        read_file(sys.argv[1], start_time, end_time)
    cal_rate()
    print_result()
    print("\nend parse")
