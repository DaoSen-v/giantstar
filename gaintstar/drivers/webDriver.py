# _*_encoding=utf8_*_
# @Time : 2021/4/29 17:38

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import time
from typing import Dict

import allure
from appium.webdriver.webdriver import WebDriver as AppDriver

from gaintstar.utils.logger import logger
from gaintstar.assert_.web import WEBAssert
from gaintstar.drivers.basicDriver import BaseDriver
from gaintstar.globalSetting import plus_setting
from gaintstar.sessionManage.webSession.seleniumSession import WEBSession
from gaintstar.utils.dataParser import patch_expr
from gaintstar.drivers.appDriver import APPDriver


class WEBDriver(BaseDriver):
    session_class = WEBSession
    assert_class = WEBAssert

    @classmethod
    def run(cls, data_set, uuid, host, **kwargs):
        """
        Webdriver驱动执行浏览器元素定位与元素动作操作
        :param host:
        :param data_set: 测试用例节点信息
            {
                "path": "/login",
                "user": "user1",
                "request": [
                    {"eventName": "元素点击", "event": "click", "locations": ["css selector", "#kw"]},
                    {"eventName": "输入内容", "event": "input", "locations": ["xpath", "#btn"], "input": "输入内容"},
                    {"eventName": "打开网页", "event": "open", "url": "输入内容"},
                    {"eventName": "键盘输入", "event": "key_event", "input": "回车/其他" },
                    {"eventName": "元素移动", "event": "move_to_element", "location": ["id", "kw"], "target": ["id", "kw"]},
                    {"eventName": "元素移动", "event": "move_to_point", "location": ["id", "kw"], "target": [1, 2]},
                    {"eventName": "鼠标移动", "event": "mouse_hover", "target": ["id", "kw"]},
                    {"eventName": "标签属性保存", "event": "get_tag_attr", "location": ["id", "kw"], "attr": ["expr", "alias_name"]},
                    {"eventName": "标签属性变更", "event": "set_tag_attr", "location": ["id", "kw"], "attr": ["name", "value"]},
                ],
                "assert": [
                    {"ele_exits":["css", "#id"]},
                    {"title_exits": "title"},
                    {'eq': ["xpath://*[@name='小明']::value", "expect_value"]},...
                ]
            }
        :param uuid: 模型的uuid
        :return:
        """
        request = data_set.get("request")
        user = data_set.get("session")
        browser = cls.session_class.get_session(user)
        if isinstance(browser, AppDriver):
            APPDriver.run(data_set, uuid, host, **kwargs)
        else:
            path = data_set.get('path').replace(' ', '')
            if path:
                time.sleep(1)
                logger.info(f"【打开网址】正在打开网址：{host+path}")
                browser.get(host+path)

            if plus_setting.REMOTE:
                logger.info(f"【视频生成】视频链接地址：{cls.session_class.video_url()}")
                allure.dynamic.link(cls.session_class.video_url(), name="用例视频连接")

            for step in request:
                cls.session_class.send(step, browser, cls.analyze_class, uuid)
            assert_ = data_set.get("assert", [])
            cls.check(assert_, browser, uuid=uuid)

    @classmethod
    def check(cls, assert_content: Dict, response, **kwargs):
        assert_content = cls.analyze(assert_content, kwargs.get("uuid"))
        for assert_line in assert_content:
            for comparator, value in assert_line.items():
                if comparator in ['ele_exits', 'title_exits', 'url_exits']:
                    cls.assert_class().validate(comparator, response, value)
                else:
                    translate_content = patch_expr(response, value[0])
                    result = translate_content[0] if translate_content else "不存在的内容"
                    cls.assert_class().validate(comparator, result, value[1])


class SimpleWEBDriver(BaseDriver):
    session_class = WEBSession
    assert_class = WEBAssert

    @classmethod
    def run(cls, user, param, assert_content, **kwargs):
        """
        Webdriver驱动执行浏览器元素定位与元素动作操作
        :param user: "user1",
        :param param:

            {"eventName": "元素点击", "event": "click", "locations": ["css selector", "#kw"]}
            {"eventName": "输入内容", "event": "input", "locations": ["xpath", "#btn"], "input": "输入内容"}
            {"eventName": "打开网页", "event": "open", "url": "输入内容"}
            {"eventName": "键盘输入", "event": "key_event", "input": "回车/其他" }
            {"eventName": "元素移动", "event": "move_to_element", "location": ["id", "kw"], "target": ["id", "kw"]}
            {"eventName": "元素移动", "event": "move_to_point", "location": ["id", "kw"], "target": [1, 2]}
            {"eventName": "鼠标移动", "event": "mouse_hover", "target": ["id", "kw"]}
            {"eventName": "标签属性保存", "event": "get_tag_attr", "location": ["id", "kw"], "attr": ["expr", "alias_name"]}
            {"eventName": "标签属性变更", "event": "set_tag_attr", "location": ["id", "kw"], "attr": ["name", "value"]}

        :param assert_content: [
            {"ele_exits":["css", "#id"]},
            {"title_exits": "title"},
            {'eq': ["xpath://*[@name='小明']::value", "expect_value"]},...
        ]
        :return:
        """
        browser = cls.session_class.get_session(user or "default")

        if plus_setting.REMOTE:
            logger.info(f"【视频生成】视频链接地址：{cls.session_class.video_url()}")
            allure.dynamic.link(cls.session_class.video_url(), name="用例视频连接")

        cls.session_class.send(param, browser, cls.analyze_class)
        cls.check(assert_content or [], browser)

    @classmethod
    def check(cls, assert_content: Dict, response, **kwargs):
        assert_content = cls.analyze(assert_content, kwargs.get("uuid"))
        for assert_line in assert_content:
            for comparator, value in assert_line.items():
                if comparator in ['ele_exits', 'title_exits', 'url_exits']:
                    cls.assert_class().validate(comparator, response, value)
                else:
                    translate_content = patch_expr(response, value[0])
                    result = translate_content[0] if translate_content else "不存在的内容"
                    cls.assert_class().validate(comparator, result, value[1])
