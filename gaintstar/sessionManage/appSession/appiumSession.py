# _*_encoding=utf8_*_
# @Time : 2021/5/7 9:17 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import inspect

import allure
from appium import webdriver
from appium.webdriver.webdriver import WebDriver

from gaintstar.globalSetting import plus_setting
from gaintstar.sessionManage.appSession.element import FindElement, CTElement
from gaintstar.sessionManage.appSession.openstfController import OpenstfController
from gaintstar.sessionManage.baseSession import BaseSession
from gaintstar.sessionManage.appSession.devicesManage import DevicesManage
from gaintstar.utils.dataParser import JsonParser
from gaintstar.utils.error import NoAvailableDevice
from gaintstar.utils.sshClient import SftpClient
from gaintstar.utils.logger import logger


class APPSession(BaseSession):
    session_list = {}
    session_type = "appUser"
    openstf_info = plus_setting.OPENSTF
    app_session_config = {}
    base_android_caps = {
        "skipServerInstallation": True,
        "skipDeviceInitialization": True,
        "resetKeyboard": True,
        # "unicodeKeyboard": True,
        "newCommandTimeout": 60,
    }
    base_ios_caps = {
        "automationName": "XCUITest",
        "useNewWDA": False,
        "newCommandTimeo": "60",
        "resetKeyboard": True,
        "unicodeKeyboard": True,
        # "app":plus_setting.IPA
    }
    # Example:
    # {
    #     "httpUser": ...,
    #     "webUser": ...,
    #     "appUser": {
    #         "build_type": "yaml",
    #         "user1": {
    #             "hub": "",
    #             "caps": {"platformName": "android", "deviceName": "", "appPackage": "", "appActivity": ""},
    #             "login_step": [
    #                 {"eventName": "输入用户名", "event": "input", "location": ["xpath", "XXX"], "input": "a02441"},
    #                 {"eventName": "输入密码", "event": "input", "location": ["xpath", "XXX"], "input": "123456"},
    #                 {"eventName": "点击登录", "event": "click", "location": ["xpath", "XXX"]},
    #             ]
    #         }
    #     },
    # }

    @classmethod
    def new_session(cls, session_name):

        if not cls.session_list:
            cls.app_session_config = cls.session_config.get(cls.session_type)
            cls.build_type = cls.app_session_config.get("build_type", "yaml")

        if cls.build_type == "yaml":
            build_content = cls.app_session_config.get('yaml_user').get(session_name)
            cls.build_session_by_step(session_name, build_content)
        elif cls.build_type == "code":
            cls.build_session_by_code(session_name)
        else:
            raise NotImplemented(f"【登录方式】登录类型错误暂时不支持该类型登录")

    @classmethod
    def get_session(cls, session_name, *args, **kwargs) -> WebDriver:
        session = super().get_session(session_name, *args, **kwargs)
        return session

    @classmethod
    def build_session_by_step(cls, session_name, step_content):
        if isinstance(step_content, str) and step_content.startswith('$'):
            session = JsonParser.analyze(step_content)
        else:
            if plus_setting.REMOTE:
                session = cls.remote_session(step_content)
            else:
                session = cls.local_session(step_content)
            for step in step_content.get("login_step"):
                cls.send(step, session, plus_setting.ANALYZE_CLASS)
        cls.session_list[session_name] = session

    @classmethod
    def build_session_by_code(cls, code_string):
        pass

    @classmethod
    def local_session(cls, step_content):
        caps = step_content.get("caps")
        platform = caps.get('platformName', 'android')
        device_name = caps.get('deviceName')
        if platform.lower() == 'android':
            cls.base_android_caps.update(caps)
            cls.base_android_caps["deviceName"] = device_name
            session = webdriver.Remote(
                command_executor='http://127.0.0.1:4723/wd/hub',
                desired_capabilities=cls.base_android_caps
            )
            return session
        elif platform.lower() == 'ios':
            cls.base_ios_caps.update(caps)
            cls.base_ios_caps["deviceName"] = device_name
            session = webdriver.Remote(
                command_executor='http://127.0.0.1:4723/wd/hub',
                desired_capabilities=cls.base_android_caps
            )
            return session
        raise NoAvailableDevice(f"【设备支持】请使用Android或iOS设备，获得了一个不支持的设备'{platform}'")

    @classmethod
    def remote_session(cls, step_content):
        """远程会话登录"""
        # caps = {
        #     "appPackage": "com.xx.xxx",
        #     "appActivity": "com.ui.activity",
        #     "platformVersion": "version",
        #     "automationName": "",
        #     "deviceName": "",
        #     "platformName": "ios/android"
        # }
        caps = step_content.get("caps")
        platform = caps.get('platformName', 'android')
        device_name = caps.get('deviceName')
        if platform.lower() == 'android':
            provider = cls.openstf_info.get("android_provider")
            OpenstfController.host = cls.openstf_info.get("host")
            OpenstfController.headers = {'Authorization': f'Bearer {cls.openstf_info.get("token")}'}
            hub, device_name = DevicesManage(**provider).get_device_caps(platform, device_name)
            OpenstfController.occupy_device(device_name)
            cls.base_android_caps.update(caps)
            app_package = cls.base_android_caps.pop("appPackage")
            app_activity = cls.base_android_caps.pop("appActivity")
            cls.base_android_caps["deviceName"] = device_name
            session = webdriver.Remote(command_executor=hub, desired_capabilities=cls.base_android_caps)
            session.start_activity(app_package=app_package, app_activity=app_activity)
            return session
        else:
            raise NoAvailableDevice(f"【设备分配】IOS设备将在后续版本添加, 请优先使用Android设备")

    @classmethod
    def send(cls, step, session, analyze_class, uuid=None):
        if isinstance(step, str):
            step = analyze_class.analyze(step)
        step = analyze_class.analyze(step, uuid)
        event = step.get("event")
        ele_name = step.get("eleName")
        location = step.get("location")
        target = step.get("target")
        step["analyze_class"] = analyze_class
        step["uuid"] = uuid

        if target:
            step["target"] = FindElement.find_element(session, target, event)
        if location:
            logger.info(f"【元素定位】event={event}, ele_name={ele_name}")
            step["ele"] = FindElement.find_element(session, location, event)

        allure.attach(
            body=session.get_screenshot_as_png(),
            name=f"查找元素【{ele_name}】event={event}",
            attachment_type=allure.attachment_type.PNG
        )

        step["browser"] = session
        eve_func = getattr(CTElement, event)
        args = inspect.getfullargspec(eve_func).args
        eve_func(**{arg: step.get(arg) for arg in args if arg not in ["cls", "self"]})
        return session

    @classmethod
    def close(cls):
        for session in cls.session_list.values():
            OpenstfController.release_device()
            session.quit()

    @classmethod
    def update_app(cls, app_path: str, session: WebDriver, platform='android'):

        if not app_path.startswith('http'):
            openstf_setting = plus_setting.get("OPENSTF")
            provider = openstf_setting[f"{platform}_provider"]
            remote_dir = openstf_setting[f"{platform}_package_dir"]
            client = SftpClient().connect(**provider)
            app_path = client.upload(app_path, remote_dir=remote_dir)

        session.install_app(app_path, grantPermissions=True, allowTestPackages=True, timeout=120000)


if __name__ == '__main__':

    config = {
        "httpUser": ...,
        "webUser": ...,
        "appUser": {
            "build_type": "yaml",
            "user1": {
                "caps": {
                    "platformName": "android",
                    "deviceName": "",
                    "appPackage": "com.casstime.ec",
                    "appActivity": "com.casstime.ec.main.splash.CECSplashActivity"
                },
            }
        },
    }
    APPSession.session_config = config
    res = APPSession.remote_session(config.get("appUser").get("user1"))
    print(res)
    res.quit()
    APPSession.close()
