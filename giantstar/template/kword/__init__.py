"""
    A keyword entry file where you can directly define functions to call as keywords.
    In some cases too many keywords can lead to administrative maintenance difficulties,
    which you can do under the project Create a new keyword management folder of your own,
    and then import it into this module.

    eg. from package.module import *
        from module import func1, func2

     We have give an example that you can operating database

     To better use the keywords, specify the necessary parameters and return values.
     This way you will see good intelligence on the platform
"""
from typing import Dict

from tool.mysqlController import MysqlHandler
from settings import DATA_BASE
from giantstar.drivers.basicDriver import BaseDriver


def add_variable(prams: Dict, uuid: str = None):
    """
    添加全局或者局部变量
    :param prams: 需要添加变量的值
    :param uuid: 当在业务模型添加局部变量需要uuid参数
    :return: None
    """
    handler = BaseDriver.analyze_class
    handler.add_variable(prams, uuid)


def sql_extract(sql):
    """
    处理数据库SQL语句执行
    :param sql: sql语句
    :return: 一个想要的结果
    """
    with MysqlHandler(database=DATA_BASE) as f:
        f.execute(sql)
        result = f.fetchall()
        # You can do some further data manipulation with the results
        return result


def other_keyword():
    pass