# _*_encoding=utf8_*_
# @Time : 2021/4/29 15:28 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import inspect

import allure

from giantstar.globalSetting import plus_setting
from giantstar.utils.logger import logger
from giantstar.drivers.basicDriver import BaseDriver

class NodeParser:
    node_info = {}
    node_data = []
    @classmethod
    def node_parser(cls, case_node, analyze_class, uuid=None):
        if not case_node:
            return
        node_type = case_node.get("nodeType", "")
        node_name = case_node.get("nodeName", "")
        node_body = case_node.get("nodeBody", {})
        check_content = case_node.get("check", {})
        check_result = True
        try:
            BaseDriver.check(check_content, response={})
        except AssertionError:
            check_result = False
        node_doc = f"【{node_type}】√ {node_name}" if check_result else f"【{node_type}】X {node_name}"
        if node_type == "BM":  # 如果节点为业务模型时 新增局部变量替换
            logger.info(f"【业务模型】业务执行， 模型名称BM={node_name}")
            uuid = case_node.get("uuid")
            parent_uuid = case_node.get("parent_uuid")
            logger.info(f"【业务模型】业务执行， 业务模型入参参数化，inputParam={case_node.get('inputParam')}")
            input_param = analyze_class.analyze(case_node.get("inputParam"), parent_uuid)
            analyze_class.add_variable(input_param, uuid=uuid)

            with allure.step(node_doc):
                for step_data in node_body:
                    cls.step_parse(step_data, analyze_class, uuid)
            new_variable = analyze_class.analyze(case_node.get("outputParam"))
            analyze_class.add_variable_from_out_param(new_variable, parent_uuid, uuid)
            analyze_class.remove_local_variable(uuid) # 清除局部变量
        else:
            with allure.step(node_doc):
                if check_result:
                    for step_data in node_body:
                        cls.step_parse(step_data, analyze_class, uuid)

    @classmethod
    def step_parse(cls, step_data, analyze_class, uuid=None):
        """
        执行节点下每个步骤测试数据
        :param step_data: 节点下测试步骤数据
            Example:
                {
                "stepName": "查看商品详情",
                "driver": "api",
                "sleep": 2,
                "url": "http://ctsp.casstime.com/post",
                "user": "user1",
                "headers": {},
                "param": {"json": {"username": "@{username}", "password":  "@{password}"}},
                "method": "post",
                "assert": [{"eq":["status_code", 200]}],
                "extract": ["message", "body"]
            }
        :return: None
        """
        if step_data.get("nodeType"):
            cls.node_parser(step_data, analyze_class, uuid)
        else:
            with allure.step(f"{step_data.get('stepName', 'unnamed')}"):
                logger.info(f"{'='*10}{step_data.get('stepName', 'unnamed')}{'='*10}")
                kw = step_data.get('driver')
                kw_path = step_data.get("kwPath")
                data_set = step_data.get("dataSet")
                if isinstance(data_set, str): data_set = analyze_class.analyze(data_set)
                host = step_data.get("host")
                model_set = step_data.get("modelSet")
                driver = getattr(plus_setting.DRIVER_BY, kw, None) or getattr(plus_setting.DRIVER_BY, 'user_kw')
                args = inspect.getfullargspec(driver.run).args
                l = locals()
                driver().run(**{arg: l.get(arg) for arg in args if arg not in ["cls", "self"]})
