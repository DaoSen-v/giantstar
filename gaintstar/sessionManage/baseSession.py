# _*_encoding=utf8_*_
# @Time : 2021/5/7 9:15 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import json
import os
from abc import abstractmethod, ABCMeta
from collections import OrderedDict
from typing import Union

from requests import Session
from selenium.webdriver.remote.webdriver import WebDriver
from appium.webdriver.webdriver import WebDriver as AppDriver

from gaintstar.globalSetting import plus_setting, DYNAMIC_SETTING_FILE
from gaintstar.utils.initTest import _Config
from gaintstar.utils.logger import logger


class BaseSession(metaclass=ABCMeta):
    flag = False
    session_config = {}
    session_list = OrderedDict()
    project_config = _Config

    @classmethod
    @abstractmethod
    def new_session(cls, *args, **kwargs):
        """新建一个会话 """

    @classmethod
    def get_session(cls, session_name,*args, **kwargs) -> Union[WebDriver, AppDriver, Session]:
        """获取一个指定的会话"""
        if not BaseSession.flag:
            setting_file = plus_setting.BASE_DIR + f'/test_case/{DYNAMIC_SETTING_FILE}'
            if not os.path.exists(setting_file):
                setting_file = plus_setting.BASE_DIR + f'/test_case/projectSetting.json'
            with open(setting_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            _Config.set_config(config)
            _Config.load_func()
            cls.session_config = _Config.session_config
        if kwargs.get("unique_uuid"):
            session_name = session_name + kwargs.get("unique_uuid")
        session = cls.session_list.get(session_name)

        if session:
            return session
        else:
            cls.new_session(session_name, *args, **kwargs)
            return cls.session_list.get(session_name)

    @classmethod
    def close(cls, *args, **kwargs):
        """关闭会话"""
