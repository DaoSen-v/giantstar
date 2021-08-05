# _*_encoding=utf8_*_
# @Time : 2021/5/8 13:46 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import importlib

import types
from typing import Dict, AnyStr

from gaintstar.utils.logger import logger
from gaintstar.utils.dataParser import GlobalVariableMap


class _Config:
    session_config: Dict = {}
    platform_host: AnyStr = ""
    environment: Dict = {}
    version: int = 1
    code_string: str = ""
    first_tier: str = ""

    @classmethod
    def set_config(cls, raw):
        cls.session_config = raw.get("loginSetting")
        cls.environment = raw.get("environment")
        cls.platform_host = raw.get('platformHost', "127.0.0.1")
        cls.code_string = raw.get("codeString", "pass")
        cls.first_tier = raw.get("firstTier", True)


    @classmethod
    def load_func(cls):
        LoadFunction.load_builtin_func()  # 加载CTtest plus的内置函数
        LoadFunction.load_project_func()


class LoadFunction:
    @classmethod
    def load_module_functions(cls, module):
        for name, item in vars(module).items():
            if isinstance(item, types.FunctionType):
                GlobalVariableMap.func_map[name] = item
            elif name == "CLASS_MAP":
                GlobalVariableMap.class_map.extend(item)

    @classmethod
    def load_builtin_func(cls, module='gaintstar._miracle'):
        """
        获取指定文件的函数视图
        :param module:
        :return:
        """
        imported_module = importlib.import_module(module)
        imported_module = importlib.reload(imported_module)
        return cls.load_module_functions(imported_module)

    @classmethod
    def load_project_func(cls):
        try:
            logger.info(f'【加载miracle】:正在加载，miracle.py文件函数')
            imported_module = importlib.import_module('miracle')
            imported_module = importlib.reload(imported_module)
            cls.load_module_functions(imported_module)
        except ModuleNotFoundError:
            logger.warning(f'【加载miracle】:项目文件未添加miracle.py文件')

    @classmethod
    def load_func_from_code_string(cls, code_string):
        """
        通过加载远程平台字符串代码来加载函数
        :param code_string: eg.
            def func_name(*args, **kwargs):
                # make your own magic func here
                return "your expect value"
        :return: None
        """

        exec(code_string+"\npass")
        for name, item in locals().items():
            if isinstance(item, types.FunctionType):
                GlobalVariableMap.func_map[name] = item
            elif name == "CLASS_MAP":
                GlobalVariableMap.class_map.extend(item)
