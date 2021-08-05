# _*_encoding=utf8_*_
# @Time : 2021/5/7 9:18 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import inspect
import os
import time
from typing import Dict
from uuid import uuid1

import allure
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from gaintstar.globalSetting import plus_setting
from gaintstar.sessionManage.baseSession import BaseSession
from gaintstar.sessionManage.webSession.element import FindElement, CTElement
from gaintstar.sessionManage.webSession.selenoidController import SelenoidController
from gaintstar.utils.logger import logger
from gaintstar.utils.dataParser import JsonParser
from gaintstar.utils.error import SelenoidError, NoSuchBrowser
from gaintstar.utils.js import send_message
from gaintstar.utils.system import is_windows, get_canonical_os_name


class WEBSession(BaseSession):
    selenoid_host = plus_setting.SELENOID_HOSTS
    session_list: Dict[str, WebDriver] = {}
    session_type = "webUser"
    web_session_config = {}
    host = ''
    video_name = 'null'
    # session_config = {
    #     "httpUser": ...,
    #     "appUser": ...,
    #     "webUser": {
    #         "build_type": "yaml",
    #         "user1": {
    #             "caps": {"browser": "chrome", "version": "80.0"},
    #             "login_step": [
    #                 {"eventName":"打开页面", 'event': "open", "url": "http://www.demo.com/index/login"},
    #                 {"eventName": "输入用户名", "event": "input", "location": [["id", "username"],[]], "input": "A02441"},
    #                 {"eventName": "输入密码", "event": "input", "location": [["id", "password"], []], "input": "123456"},
    #                 {"eventName": "点击登录", "event": "click", "location": [["id", "loginBtn"],[]]}
    #             ]
    #         },
    #         "user2": {},
    #         "user3": {}
    #     }
    # }

    @classmethod
    def new_session(cls, session_name):
        if not cls.session_list:
            cls.web_session_config = cls.session_config.get(cls.session_type)

        build_content = cls.web_session_config.get(session_name)
        cls.build_session_by_step(session_name, build_content)


    @classmethod
    def build_session_by_step(cls, session_name, step_content):
        if isinstance(step_content, str) and step_content.startswith('$'):  # 自定义函数登录
            session = JsonParser.analyze(step_content)
        else:
            if plus_setting.REMOTE:
                session = cls.remote_session(step_content)  # 通过测试步骤远程登录
            else:
                session = cls.local_session(step_content)  # 通过测试步骤本地登录

            for step in step_content.get("login_step"):
                step = JsonParser.analyze(step)
                event = step.get("event")
                event_name = step.get("eventName")
                location = step.get("location")
                target = step.get("target")
                step["analyze_class"] = JsonParser

                if target:
                    step["target"] = FindElement.find_element(session, target, event=event)
                if location:
                    send_message(session, event + event_name)
                    step["ele"] = FindElement.find_element(session, location, event=event)
                step["browser"] = session
                eve_func = getattr(CTElement, event)
                args = inspect.getfullargspec(eve_func).args
                eve_func(**{arg: step.get(arg) for arg in args if arg != "cls"})
        cls.session_list[session_name] = session

    @classmethod
    def close(cls):
        for session in cls.session_list.values():
            session.quit()

    @classmethod
    def get_options(cls, browser):
        if browser == "chrome":
            option = webdriver.ChromeOptions()
            option.add_argument("--start-maximized")
            option.add_experimental_option("excludeSwitches", ['enable-automation', 'load-extension'])
            prefs = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
            option.add_experimental_option("prefs", prefs)
            return option
        elif browser == "firefox":
            option = webdriver.FirefoxOptions()
            option.add_argument("--start-maximized")
            return option

    @classmethod
    def local_session(cls, step_content):
        caps = step_content.get('caps', {})
        browser: str = caps.get('browser', 'chrome')
        if browser == "chrome":
            try:
                print('正在启动浏览器...')
                return webdriver.Chrome(options=cls.get_options(browser))
            except WebDriverException:
                driver_path = cls._get_web_driver('chromedriver')
                return webdriver.Chrome(executable_path=driver_path, options=cls.get_options('chrome'))
        elif browser == "firefox":
            try:
                print('正在启动浏览器···')
                return webdriver.Firefox(options=cls.get_options(browser), service_log_path=None)
            except WebDriverException:
                driver_path = cls._get_web_driver('geckodriver')
                return webdriver.Chrome(
                    executable_path=driver_path,
                    options=cls.get_options('firefox'),
                    service_log_path=None
                )
        raise NoSuchBrowser(f'【浏览器】仅支持火狐（firefox）与谷歌浏览器（chrome），{browser}不被支持')

    @classmethod
    def remote_session(cls, step_content):
        caps = step_content.get('caps', {})
        browser = {}
        for host in cls.selenoid_host:
            cls.host = host
            browser = SelenoidController().get_one(**caps, host=cls.host + ":8080")
            if browser:
                break
        if not browser:
            raise SelenoidError(f"【seleniod】无可用浏览器，请尝试更换浏览器版本")
        cls.video_name = f'{time.strftime("%Y-%m-%d_%H-%M_%S", time.localtime())}'+str(uuid1()).replace('-', '')+'.mp4'
        capabilities = {
            "enableVNC": False,
            "enableVideo": True,
            "videoName": cls.video_name
        }
        capabilities.update(browser)
        session = webdriver.Remote(
            command_executor=f"{cls.host}:4444/wd/hub",
            desired_capabilities=capabilities,
            options=cls.get_options(browser.get("browser")),
        )
        session.maximize_window()
        return session

    @classmethod
    def _get_web_driver(cls, driver_name):
        """获取对应操作系统的浏览器驱动"""
        if is_windows():
            driver_name += '.exe'
        current_dir = os.path.dirname(__file__)
        driver_path = os.path.join(
            current_dir, 'webdrivers', get_canonical_os_name(), driver_name
        )
        return driver_path

    @classmethod
    def video_url(cls):
        from gaintstar.drivers.compatorDriver import CompatWEBDriver
        CompatWEBDriver.video_url = cls.host + ":8080/video/" + cls.video_name
        return cls.host + ":8080/video/" + cls.video_name

    @classmethod
    def send(cls, step, session, analyze_class, uuid=None):
        if isinstance(step, str):
            step = analyze_class.analyze(step)
        step = analyze_class.analyze(step, uuid)
        event = step.get("event")
        ele_name = step.get("eleName")
        location = step.get("location")
        target = step.get("target")
        # 添加步骤参数类，与业务模型id
        step["analyze_class"] = analyze_class
        step["uuid"] = uuid

        # 调试模式
        send_message(session, f"查找元素【{ele_name} event={event}】")

        if target: step["target"] = FindElement.find_element(session, target, event)

        if location:
            logger.info(f"【元素定位】event={event}, ele_name={ele_name}")
            step["ele"] = FindElement.find_element(session, location, event)

        allure.attach(
            body=session.get_screenshot_as_png(),
            name=f"查找元素【{ele_name}】event={event}",
            attachment_type=allure.attachment_type.PNG
        )
        step["browser"] = session
        # 获取元素处理函数，执行函数
        eve_func = getattr(CTElement, event)
        args = inspect.getfullargspec(eve_func).args
        try:
            eve_func(**{arg: step.get(arg) for arg in args if arg not in ["cls", 'self']})
            # session.switch_to.default_content()
            logger.info(f"【元素操作】--> success event={event}, ele_name={ele_name}")
        except Exception as e:
            logger.info(f"【元素操作】--> failed event={event}, ele_name={ele_name}")
            raise e


if __name__ == '__main__':
    selenoid = {
        "name": "selenoid_ui_2",
        "hostname": "10.118.71.155",
        "port": 22,
        "username": "root",
        "password": "Casstime@com1112XSW@",
        "selenoid_ui_port": "8080",
        "selenoid_hub_port": "4444",
        "selenoid_video_dir": "/home/selenoid_ui/video",
        "nginx_video_dir": "/html/video/web",
        "video_url_prefix": "/video/web",
    }
    session_config = {
        "httpUser": ...,
        "appUser": ...,
        "webUser": {
            "build_type": "yaml",
            "yaml_user": {
                "user1": {
                    "caps": {"browser": "firefox"},
                    "login_step": [
                        {"eventName": "打开页面", 'event': "open", "url": "http://ctsp.casstime.com/login"},
                        {"eventName": "输入用户名", "event": "input", "location": ["id", "username"], "input": "A02441"},
                        {"eventName": "输入密码", "event": "input", "location": ["id", "password"], "input": "Xu173798"},
                        {"eventName": "点击登录", "event": "click", "location": ["id", "loginBtn"]},
                    ]
                },
                "user2": {}
            },
            "codeUser": "python string code"
        },
    }
    # WEBSession.get_session("user1")
    # res = WEBSession.remote_session(session_config.get("webUser").get("user1"))
    # print(res)
    # time.sleep(2)
    # res.quit()
    #
    # WEBSession.close()
    # print(os.path.dirname(__file__))
    allure.parent_suite()
    print(time.strftime("%Y-%m-%d_%H-%M_%S", time.localtime()))
