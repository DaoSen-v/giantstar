# _*_encoding=utf8_*_
# @Time : 2021/5/13 17:15 

# @Author : xuyong

# @Email: yong1.xu@casstime.com

from gaintstar.drivers.basicDriver import BaseDriver


class DebugDriver(BaseDriver):
    @classmethod
    def run(cls, data_set, uuid):
        """
        用于平台功能调试的驱动，不做业务测试，检查平台用例编写的业务逻辑
        :param data_set: eg.
            {
                "debug": {"name": "@{param.0}", "func": "${func('args1', kwargs='args')}"}
                "assert": {
                    "eq":['name', 'name'],
                    "eq": [1, 2],
                    "eq": ["@{param.0}", "2"]
                }
                "extract": {
                    "arg1": "value",
                    "arg2": "value"
                }
            }
        :param uuid: 当前节点的
        :return: None
        """
        debug = data_set.get("debug")
        assert_ = data_set.get("assert")
        extract = data_set.get("extract")
        cls.analyze(debug)
        assert_content = cls.analyze(assert_)
        cls.check(assert_content)
        cls.extract(extract, extract.keys())
