# _*_encoding=utf8_*_
# @Time : 2021/5/7 16:47 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
from functools import reduce


def add(*args):
    return reduce(lambda x, y: x + y, args)


# 减
def sub(*args):
    return reduce(lambda x, y: x - y, args)


# 乘
def mul(*args):
    return reduce(lambda x, y: x * y, args)


# 除
def div(*args):
    return reduce(lambda x, y: x / y, args)


def _splice_str(target_arg, start_index=None, end_index=None):
    target_arg = str(target_arg)
    str_len = len(target_arg)
    start_index = start_index if start_index else 0
    end_index = str_len if not end_index else end_index + 1
    return str(target_arg)[start_index:end_index]

def to_str(target_arg, start_index=None, end_index=None):
    return _splice_str(target_arg, start_index, end_index)


def to_int(self, target_arg, start_index=None, end_index=None):
    target_arg = self._splice_str(target_arg, start_index, end_index).replace(',', '')
    return int(target_arg)


def to_float(self, target_arg, start_index=None, end_index=None):
    target_arg = self._splice_str(target_arg, start_index, end_index).replace(',', '')
    return float(target_arg)
