# _*_encoding=utf8_*_
# @Time : 2021/7/26 11:02 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import inspect

from giantstar.globalSetting import plus_setting


class NodeParser:
    node_info = {}
    node_data = []

    @classmethod
    def node_parser(cls, case_node, analyze_class):
        """
        执行节点下每个步骤测试数据
        :param step_data: 节点下测试步骤数据
            Example:
                {
                    "stepName": "测试步骤名称",
                    "driver": "测试步骤关键字",
                    "modelSet":{},
                    "dataId": 1,
                    "host": "https://saasdemo.s2.ewewo.com/Center2Service",
                    "dataSet": {}
                }
        :return: None
        """
        if isinstance(case_node, str): case_node = analyze_class.analyze(case_node)
        kw = case_node.pop('driver', 'api')
        driver = getattr(plus_setting.DRIVER_BY, kw, None) or getattr(plus_setting.DRIVER_BY, 'user_kw')
        args = inspect.getfullargspec(driver.run).args
        driver().run(**{arg: case_node.get(arg) for arg in args if arg not in ["cls", "self"]})

if __name__ == '__main__':
    a = {}
    print(a.pop("name", 123))
