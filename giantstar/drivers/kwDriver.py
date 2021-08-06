# _*_encoding=utf8_*_
# @Time : 2021/5/13 17:14 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import importlib
import sys
import types

from giantstar.drivers.basicDriver import BaseDriver
from giantstar.utils.logger import logger
from giantstar.utils.error import UserKeyWordError


class KeyWordDriver(BaseDriver):
    key_word_module = {}
    flag = False

    @classmethod
    def run(cls, data_set, kw, uuid=None):
        """
        :param kw: 关键字路径
        :param data_set: 关键字数据表
            Example:
                {
                    "request": {"arg1": "value1", "arg2": "value2"},
                    "extract": [["id", "alias"], ["$", "alias"]]
                }
        :param uuid: 模型uuid
        :return: None
        """
        data_set = cls.analyze(data_set, uuid=uuid)
        kw_func = cls.acquire_kw(kw)
        kw_args = data_set.get("request")
        try:
            response = kw_func(**kw_args)
            cls.extract(response=response, extract_list=data_set.get("extract"), uuid=uuid)
        except Exception as e:
            logger.error(f"【关键字执行出错】执行用户关键字kw={kw}, kw_args={kw_args}")
            raise e

    @classmethod
    def acquire_kw(cls, kw: str):
        package, func = kw.rsplit(".")
        if not hasattr(cls.key_word_module[package], func):
            cls.key_word_module[package] = importlib.import_module(package)
        attr_func = getattr(cls.key_word_module[package], func)
        if isinstance(attr_func, types.FunctionType):
            return  attr_func
        else:
            return attr_func().excute
