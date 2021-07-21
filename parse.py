#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import sys

counts = {}
rates = {}
count_type = {}
count_module = {}
count_file = {}
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
    #print(type_str)
    #print(switch_type(type_str))
    type_ = switch_type(type_str)
    return type_
    
def get_module(line):
    module_str = line.split(' ')[4]
    if not module_str.startswith('['):
        return ""
    if not module_str.endswith(']'):
        return ""
    module_str = module_str[1:len(module_str)-1]
    #print(module_str)
    return module_str

def get_file(line):
    file_str = re.search(r'[a-z_]+\.[a-z]+:[1-9][0-9]*', line, 0)
    if file_str == None:
        return ""
    file_str = file_str.group()
    #file_str = file_str[0:file_str.find(':')]
    return file_str

def read_file(file_):
    # 初始化
    counts["blank_num"] = 0
    counts["no_type"]   = 0
    counts["log_num"]   = 0
    counts["line_num"]  = 0
    # 打开文件
    fr=open(file_,'r')
    # 读取文件所有行
    content=fr.readlines()

    # 依次迭代所有行
    for line in content:
        counts["line_num"] += 1
        # 去除空格
        line=line.strip()
        #如果是空行，则跳过
        if len(line)==0:
            counts["blank_num"] += 1
            continue
        log_type = get_type(line)
        if log_type == "":
            counts["no_type"] += 1
            continue
        counts["log_num"] += 1
        if log_type not in count_type.keys():
            count_type[log_type] = 1
        else:
            count_type[log_type] += 1

        module_name = get_module(line)
        if module_name not in count_file.keys():
            count_file[module_name] = {}
        if module_name not in count_module.keys():
            count_module[module_name] = 1
        else:
            count_module[module_name] += 1

        file_name = get_file(line)
        if file_name == "":
            continue
        if file_name not in count_file[module_name].keys():
            count_file[module_name][file_name] = 1
        else:
            count_file[module_name][file_name] += 1

    fr.close()

def cal_rate():
    global count_module_s
    global count_file_s
    count_file_s = {}
    count_module_s = sorted(count_module, cmp=lambda x,y:cmp(count_module[x],count_module[y]), reverse=True)
    sum_ = float(counts["line_num"])
    for item in counts:
        rates[item] = (float(counts[item]) / sum_) * 100
    for module in count_module_s:
        rate_module[module] = (float(count_module[module]) / sum_) * 100
        rate_file[module] = {}
        count_file_s[module] = sorted(count_file[module], cmp=lambda x,y:cmp(count_file[module][x],count_file[module][y]), reverse=True)
        for file_ in count_file[module]:
            rate_file[module][file_] = (float(count_file[module][file_]) / sum_) * 100


def print_result():
    print("[parse result]")
    print("count     rate     module/file")
    item = "line_num"
    print('%-8d  %6.2f%%  %s' % (counts[item], rates[item], item))
    for item in counts:
        if item == "line_num":
            continue
        print('%-8d  %6.2f%%  %s' % (counts[item], rates[item], item))
    print("")
    n1 = 0
    for module in count_module_s:
        n1 += 1
        if n1 > 10:
            break
        if module == "":
            print('%-8d  %6.2f%%  (no mudule)' % (count_module[module], rate_module[module]))
        else:
            print('%-8d  %6.2f%%  [%s]' % (count_module[module], rate_module[module], module))
        n2 = 0
        for file_ in count_file_s[module]:
            n2 += 1
            if n2 > 10:
                break
            print('  %-8d%6.2f%%  %s'% (count_file[module][file_], rate_file[module][file_], file_))
        print("")

if __name__ == '__main__':
    print("start parse\n")
    read_file(sys.argv[1])
    cal_rate()
    print_result()
    print("\nend parse")
