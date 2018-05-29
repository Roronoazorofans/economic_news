# coding=utf-8
# 公共的工具文件
def do_rank(index):
    # 根据传入的索引,返回first, second, third
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return " "