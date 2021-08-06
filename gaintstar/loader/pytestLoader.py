import allure
import pytest
import yaml
import json

from gaintstar.loader.easyNodeParser import  NodeParser
from gaintstar.globalSetting import plus_setting, DYNAMIC_FILE
from gaintstar.utils.initTest import _Config


plus_setting.TEST_FILES.append(DYNAMIC_FILE)


def pytest_collect_file(parent, path):
    if path.ext == ".json" and path.basename in plus_setting.TEST_FILES:
        return TestFile.from_parent(parent, fspath=path)


class Level:
    P0 = "blocker"
    P1 = "critical"
    P2 = "normal"
    P3 = "minor"
    P4 = "trivial"


class TestFile(pytest.File):
    def collect(self):
        case_list = json.load(self.fspath.open(mode="r", encoding="utf-8"))
        # 初始化项目信息
        for spec in case_list:  # 遍历测试计划列表生成可执行的测试用例
            case_tier = spec.get("caseTier").split("-")  # 获取用例的层级目录
            spec["caseTier"] = case_tier
            module_name = case_tier[0]  # 获取用例所在模块名称
            parametrize = spec.get("parametrize")
            case_name = spec.get("caseName")
            if parametrize and isinstance(parametrize, list):
                for param in parametrize:  # 数据TDD驱动生成多条用例
                    title = param.get("_title")
                    extent_name = f"({title})"
                    yield LoadItem.from_parent(
                        self,
                        name=f"{module_name}::{case_name+extent_name}",
                        spec=spec,
                        platform_host=_Config.platform_host,
                        extent_name = extent_name,
                        param = param
                    )
            else:
                yield LoadItem.from_parent(
                    self,
                    name=f"{module_name}::{case_name}",
                    spec=spec,
                    platform_host=_Config.platform_host
                )


class LoadItem(pytest.Item):
    def __init__(self, name, parent, spec, platform_host, extent_name="", param=None):
        super().__init__(name, parent)
        self.spec = spec
        self.platform_host = platform_host
        self.extent_name = extent_name
        self.param = param or {}

    def dynamic_label(self):
        """
        动态标记用例信息
        :return: None
        """
        case_tier = self.spec.get("caseTier")  # 获取用例层级
        title = self.spec.get("caseName", "untitled")
        if len(case_tier) >= 1:
            allure.dynamic.label('epic', case_tier[0])  # 标记用例模块
        allure.dynamic.tag(self.spec.get("caseLevel", "P3")) # 标记用例tag
        allure.dynamic.severity(getattr(Level, self.spec.get("caseLevel", "P3"), "normal"))  # 标记用例严重等级
        if len(case_tier) >= 2:
            allure.dynamic.feature(case_tier[1])  # 标记用例功能
        if len(case_tier) >= 3:
            allure.dynamic.story(case_tier[2])  # 标记用例分支
            title = ">>"+">>".join(case_tier[3:]) + ">>" + title + self.extent_name
        allure.dynamic.title(f'{title}')  # 标记用例标题

    def runtest(self):
        if self.param:
            allure.attach(
                name="【TDD】",
                body=yaml.dump(self.param, default_flow_style=False, encoding='utf-8', allow_unicode=True),
                attachment_type=allure.attachment_type.YAML
            )
        self.dynamic_label()  # 为用例添加层级结构，描述
        plus_setting.ANALYZE_CLASS.add_variable(self.param)
        case_nodes = self.spec.get("caseNodes")
        for case_node in case_nodes:
            NodeParser.node_parser(case_node, plus_setting.ANALYZE_CLASS)

        # if name != value:
        #     raise YamlException(self, name, value)

    def repr_failure(self, excinfo, **kwargs):
        """Called when self.runtest() raises an exception.
        :param excinfo:
        :param **kwargs:
        """
        if plus_setting.PRINT_STACK:
            return super().repr_failure(excinfo, **kwargs)
        else:
            return excinfo.typename + ":" + "\n".join(excinfo.value.args)

    def reportinfo(self):
        return self.fspath, 0, f"usecase: {self.name}"


class YamlException(Exception):
    """Custom exception for error reporting."""
