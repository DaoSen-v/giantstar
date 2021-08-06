# _*_encoding=utf8_*_
# @Time : 2021/4/29 17:27 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
from abc import ABCMeta, abstractmethod
from typing import Dict

from giantstar.assert_.publicAssert import AssertFactory
from giantstar.sessionManage.baseSession import BaseSession
from giantstar.utils.dataParser import patch_expr, JsonParser
from giantstar.utils.logger import logger


class BaseDriver(metaclass=ABCMeta):
    analyze_class = JsonParser
    assert_class = AssertFactory
    session_class = BaseSession

    @classmethod
    @abstractmethod
    def run(cls, *args, **kwargs):
        pass
    
    @classmethod
    def analyze(cls, raw_data, uuid=None, var_map=None):
        raw_data = cls.analyze_class.analyze(raw_data, uuid, owner_var_map=var_map)
        return raw_data

    @classmethod
    def extract(cls, response, extract_list, uuid=None, var_map=None):
        return cls.analyze_class.extract(extract_list, response, uuid, owner_var_map=var_map)

    @classmethod
    def check(cls, assert_content: Dict, response, **kwargs):
        """
        将表达式
        :param assert_content:
            Example:
                [
                    {"eq": ["返回结果提取表达式", "期望返回结果", "错误消息提示"]},
                    {"eq": ["实际返回结果", "期望返回结果", "断言错误时返回消息提示"]},
                    {"eq": ["status_code", "200", "接口返回状态码不等于200"]},
                    {"lt": ["id", "123", "接口返回状态码不等于200"]},
                ]
            官方文档： 飞熊社区XXX
        :param response:
            接口返回的response对象
        :return: dict 经过解析后的断言文本内容
        """
        assert_content = cls.analyze(assert_content, kwargs.get("uuid"), kwargs.get("var_map"))
        for assert_line in assert_content:
            for comparator, value in assert_line.items():
                # 兼容代码
                extract_value = cls.analyze_class.get_variable(var_name=value[0], uuid=kwargs.get("uuid"), owner_var_map=kwargs.get("owner_var_map"))
                translate_content = extract_value or patch_expr(response, value[0])
                result = translate_content[0] if isinstance(translate_content, list) and translate_content else translate_content
                logger.info(f"【结果断言】constant={translate_content} {type(result)}{result} {comparator}  {value[1]}{type(value[1])}")
                cls.assert_class().validate(comparator, result, value[1])

        return assert_content

    @classmethod
    def close(cls):
        pass
