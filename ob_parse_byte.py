#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import os
import sys
import datetime

sizes = {}
rates = {}
size_line = {}
rate_line = {}
size_line_s = {}

def get_log_line(line):
    file_str = re.search(r'[a-z_]+\.[a-z]+:[1-9][0-9]*', line, 0)
    if file_str == None:
        return ""
    file_str = file_str.group()
    return file_str

def get_log_time(line):
    if len(line.split(' ')) < 2:
        return None
    time_str = line.split(' ')[0] + ' ' + line.split(' ')[1]
    time_str = time_str[1:len(time_str) - 1]
    try:
        time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        time = None
    return time

def get_file_time(file):
    time = None
    time_str = re.search(r'[0-9]{14}', file, 0)
    if time_str != None:
        time_str = time_str.group()
        try:
            time = datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S")
        except ValueError:
            time = None
    return time

def parse_file(file_, start_time = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), end_time = datetime.datetime.now()):
    # 初始化
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
        log_time = get_log_time(line)
        if log_time == None:
            sizes["no_time"] += size
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

        line_name = get_log_line(line)
        if line_name == "":
            continue
        if line_name not in size_line.keys():
            size_line[line_name] = size
        else:
            size_line[line_name] += size

    fr.close()

def parse_dir(dir_, start_time = datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), end_time = datetime.datetime.now()):
    print("select from [%s] to [%s]" % (start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S")))
    # 初始化文件列表
    file_list = {}
    file_list["election"] = []
    file_list["observer"] = []
    file_list["rootservice"] = []
    for name in os.listdir(dir_):
        file_path = os.path.join(dir_, name)
        # 如果不是文件
        if not os.path.isfile(file_path):
            continue
        # 如果是wf类型的日志
        if ".wf" in name:
            continue
        file_time = get_file_time(name)
        # 如果没有时间戳，或时间戳不符合条件
        if file_time != None and (file_time < start_time or file_time > end_time):
            continue
        # 满足条件，进行分类
        if "election.log" in name:
            file_list["election"].append(file_path)
        elif "observer.log" in name:
            file_list["observer"].append(file_path)
        elif "rootservice.log" in name:
            file_list["rootservice"].append(file_path)
    
    # 对文件进行分析
    for type_ in file_list:
        if len(file_list[type_]) == 0:
            print("\n(no %s log file)" % type_)
            continue
        sizes.clear()
        rates.clear()
        size_line.clear()
        rate_line.clear()
        sizes["blank_size"] = 0
        sizes["no_time"]    = 0
        sizes["log_size"]   = 0
        sizes["sum_size"]   = 0
        for file in file_list[type_]:
            parse_file(file, start_time, end_time)
        cal_rate()
        print("\n[parse result of %s]" % type_)
        print_result()


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
        rate_line[line] = (float(size_line[line]) / sum_) * 100

def print_result():
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
        if rate_line[line] < 0.1:
            break
        print('%10d  %6.2f%%  %s'% (size_line[line], rate_line[line], line))

if __name__ == '__main__':
    argv_num = len(sys.argv)
    if argv_num < 2 and argv_num > 4:
        print("invalid arguments! please input like this:\n"
              "python parse.py log_dir_path [xxxx-xx-xx-xx:xx:xx] [xxxx-xx-xx-xx:xx:xx]")
        exit(-1)
    path = sys.argv[1]
    if not os.path.isdir(path):
        print("\"%s\" is not a directory")
        exit(-1)
    if argv_num >= 3:
        try:
            start_time = datetime.datetime.strptime(sys.argv[2], "%Y-%m-%d-%H:%M:%S")
        except ValueError:
            print("time format error")
            exit(-1)
    if argv_num >=4:
        try:
            end_time = datetime.datetime.strptime(sys.argv[3], "%Y-%m-%d-%H:%M:%S")
        except ValueError:
            print("time format error")
            exit(-1)
    print("start parse\n")
    if argv_num == 2:
        parse_dir(path)
    elif argv_num == 3:
        parse_dir(path, start_time)
    elif argv_num == 4:
        parse_dir(path, start_time, end_time)
    print("\nend parse")
