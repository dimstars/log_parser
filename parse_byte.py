#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import sys
import datetime

sizes = {}
rates = {}
size_type = {}
size_line = {}
rate_type = {}
rate_file = {}

types = {'INFO', 'WARN', 'TRACE', 'DEBUG', 'ERROR'}

def get_type(line):
    str_list = line.split(' ')
    if len(str_list) < 3:
        return ""
    type_str = str_list[2]
    if type_str in types:
        type_ = type_str
    else:
        type_ = ""
    return type_

def get_line(line):
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
    sizes["no_type"]    = 0
    sizes["log_size"]   = 0
    sizes["sum_size"]   = 0
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

        line_name = get_line(line)
        if line_name == "":
            continue
        if line_name not in size_line.keys():
            size_line[line_name] = size
        else:
            size_line[line_name] += size

    fr.close()

def cal_rate():
    global size_line_s
    size_line_s = {}
    sum_ = float(sizes["sum_size"])
    if sum_ == 0:
        return False
    for item in sizes:
        rates[item] = (float(sizes[item]) / sum_) * 100
    size_line_s = sorted(size_line, cmp=lambda x,y:cmp(size_line[x],size_line[y]), reverse=True)
    for line in size_line:
        rate_file[line] = (float(size_line[line]) / sum_) * 100

def print_result():
    print("[parse result]")
    if sizes["sum_size"] == 0:
        print("no log meets the condition")
        return False
    print("    size      rate     module/file")
    item = "sum_size"
    print('%10d  %6.2f%%  %s' % (sizes[item], rates[item], item))
    for item in sizes:
        if item == "sum_size":
            continue
        print('%10d  %6.2f%%  %s' % (sizes[item], rates[item], item))
    print("")
    n = 0
    for line in size_line_s:
        n += 1
        if n > 20:
            break
        if rate_file[line] < 0.1:
            break
        print('%10d  %6.2f%%  %s'% (size_line[line], rate_file[line], line))

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
