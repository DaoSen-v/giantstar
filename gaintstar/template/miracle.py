"""
This file function is used for parameterization only
"""
import calendar
import datetime
import time
from random import random

from gaintstar.utils.fileReader import ExcelReader, MysqlReader


def get_data(dataid, source, use='default'):
    if source == 'excel':
        return ExcelReader.get_excel_data(index=dataid, use=use)
    elif source == 'mysql':
        return MysqlReader.get_mysql_data(sql=dataid, use=use)


def random_vin():
    # 内容的权值
    content_map = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
        'F': 6, 'G': 7, 'H': 8, 'I': 0, 'J': 1, 'K': 2, 'L': 3,
        'M': 4, 'N': 5, 'O': 0, 'P': 7, 'Q': 8, 'R': 9, 'S': 2, 'T': 3,
        'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9, "0": 0, "1": 1,
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9
    }
    # 位置的全值
    location_map = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    vin = ''.join(random.sample('0123456789ABCDEFGHJKLMPRSTUVWXYZ', 17))
    num = 0
    for i in range(len(vin)):
        num = num + content_map[vin[i]] * location_map[i]
    vin9 = num % 11
    if vin9 == 10:
        vin9 = "X"
    list1 = list(vin)
    list1[8] = str(vin9)
    vin = ''.join(list1)
    return vin


def random_birthday():
    a1 = (1976, 1, 1, 0, 0, 0, 0, 0, 0)  # 设置开始日期时间元组（1976-01-01 00：00：00）
    a2 = (2017, 12, 31, 23, 59, 59, 0, 0, 0)  # 设置结束日期时间元组（1990-12-31 23：59：59）
    start = time.mktime(a1)  # 生成开始时间戳
    end = time.mktime(a2)  # 生成结束时间戳
    t = random.randint(start, end)  # 在开始和结束时间戳中随机取出一个
    # date_touple = time.localtime(t)  # 将时间戳生成时间元组
    # date = time.strftime("%Y-%m-%d", date_touple)  # 将时间元组转成格式化字符串（1976-05-21）
    # logger.info('【数据处理】success -->${random_birthday()} changed into --> %s' % t)
    return t


def month_start_timestamp():
    now = datetime.date.today()
    this_month_start = datetime.datetime(now.year, now.month, 1)
    time_array = time.strptime(str(this_month_start), "%Y-%m-%d %H:%M:%S")
    return str(int(time.mktime(time_array)) * 1000)


def month_end_timestamp():
    now = datetime.date.today()
    this_month_end = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    time_array = time.strptime(str(this_month_end), "%Y-%m-%d %H:%M:%S")
    return str(int(time.mktime(time_array)) * 1000)


def year_start_timestamp():
    now = datetime.date.today()
    this_year_start = datetime.datetime(now.year, 1, 1)
    time_array = time.strptime(str(this_year_start), "%Y-%m-%d %H:%M:%S")
    return str(int(time.mktime(time_array))*1000)


def year_end_timestamp():
    now = datetime.date.today()
    this_year_end = datetime.datetime(now.year + 1, 1, 1) - datetime.timedelta(days=1)
    time_array = time.strptime(str(this_year_end), "%Y-%m-%d %H:%M:%S")
    return str(int(time.mktime(time_array))*1000)


def today_start_timestamp():
    today = datetime.date.today()
    yesterday_end_time = int(time.mktime(time.strptime(str(today), '%Y-%m-%d'))) - 1
    today_start_time = yesterday_end_time + 1
    return str(today_start_time*1000)


def today_end_timestamp():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    today_end_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d'))) - 1
    return str(today_end_time*1000)


def sleep(num):
    """
    执行用例时暂停
    """
    time.sleep(num)
    return f'\n【执行步骤】Wait {num} seconds for ES to synchronize data'
