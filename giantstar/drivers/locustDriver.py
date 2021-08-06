import json
import time
from collections import OrderedDict

import requests

from giantstar.drivers.basicDriver import BaseDriver
from giantstar.globalSetting import plus_setting
from giantstar.sessionManage.baseSession import BaseSession
from giantstar.utils.dataParser import JsonParser
from giantstar.utils.initTest import _Config


class LocustSession(BaseSession):
    """
    一个用于管理Http会话的类
    """
    session_list = OrderedDict()
    session_type = "httpUser"
    http_user_code = {}

    @classmethod
    def new_session(cls, session_name, locust_session=None, unique_uuid=None):
        """
        新建会话
        :param session_name: 会话名称/用户名称
        :param build_content: "httpUser"用户登录配置
        :return: None
        """
        if not cls.session_list:
            cls.http_session_config = cls.session_config.get(cls.session_type)
            cls.build_type = cls.http_session_config.get("build_type", "yaml")
        if cls.build_type == "yaml":
            build_content = cls.http_session_config.get("yaml_user").get(session_name)
            cls.build_session_by_step(session_name, build_content, locust_session=locust_session, unique_uuid=unique_uuid)
        else:
            raise NotImplemented(f"【登录方式】登录类型错误暂时不支持该类型登录")

    @classmethod
    def get_session(cls, session_name, *args, **kwargs):
        """获取一个指定的会话"""
        if not cls.flag:
            with open(plus_setting.BASE_DIR + '/test_case/projectSetting.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            _Config.set_config(config)
            _Config.load_func()
            cls.session_config = config.get("loginSetting")
            cls.flag = True
        session = cls.session_list.get(session_name+kwargs.get("unique_uuid"))

        if session:
            return session
        else:
            cls.new_session(session_name, *args, **kwargs)
            return cls.session_list.get(session_name+kwargs.get("unique_uuid"))

    @classmethod
    def build_session_by_step(cls, session_name, step_data, locust_session=None, unique_uuid=""):
        if isinstance(step_data, str) and step_data.startswith('$'):
            session = JsonParser.analyze(step_data)
            if locust_session:
                locust_session.headers = session.headers
                session = locust_session
        else:
            session = locust_session or requests.session()
            for login_step in step_data:
                after = login_step.pop("after", {})
                login_step = JsonParser.analyze(login_step)
                method = login_step.get('method')
                session.headers.update(login_step.get('header', {}))
                url = login_step.get('url')
                body_type = login_step.get("bodyType", '')
                data = login_step.get("data", {})
                extract = login_step.get("extract")
                if method.lower() == "get":
                    response = session.request(url=url, method='get', params=data)
                elif body_type in ['raw', "json"]:
                    response = session.request(url=url, method=method, json=data)
                else:
                    response = session.request(url=url, method=method, files=data)
                JsonParser.extract(extract, response)
                if after:
                    after = JsonParser.analyze(after)
                    header = after.get('header')
                    session.headers.update(header)
        session_name = session_name + unique_uuid
        cls.session_list[session_name] = session

    @classmethod
    def send(cls, session, **kwargs):
        response = session.request(**kwargs)
        return response


class HTTPDriver(BaseDriver):
    header = plus_setting.HTTP_REQUEST_HEADER
    session_class = LocustSession

    @classmethod
    def run(cls, data_set, model_set, uuid=None, host='', locust_session=None, unique_uuid=None, var_map=None):
        host = host or _Config.environment.get("default")
        user = data_set.get("session")
        http_session = cls.session_class.get_session(session_name=user, locust_session=locust_session, unique_uuid=unique_uuid)
        req_query = cls.analyze(data_set.get("req_query") or {}, uuid, var_map=var_map)  or {}# 参数化求数据
        req_body = cls.analyze(data_set.get("req_body") or {}, uuid, var_map=var_map) or {}
        headers = cls.analyze(data_set.get("headers") or {}, uuid, var_map=var_map) or {}
        sleep = data_set.get('sleep')

        method = model_set.get("method")
        path = model_set.get("path")
        req_body_type = model_set.get("req_body_type") or model_set.get("dataType")
        if data_set.get("key_path"):
            path = path.format(**data_set.pop("key_path"))
        http_session.headers.update(headers)
        # request_param_patch = cls.request_param_type_match(req_body, req_body_type)
        response = cls.session_class.send(  # 发送session会话请求
            http_session,
            method=method,
            url=cls.analyze(host+path, uuid, var_map=var_map),
            params = req_query,
            **cls.request_param_type_match(req_body, req_body_type)
        )
        if sleep: time.sleep(sleep)
        try:
            cls.check(data_set.get("assert", {}), response, uuid=uuid)  # 执行数据断言操作
            extract_content = cls.analyze(data_set.get("extract"), uuid, var_map)or {}
            cls.extract(response, extract_content, uuid, var_map=var_map) or {}  # 执行保存变量操作
        except Exception as e:
            raise e

    @classmethod
    def request_param_type_match(cls, request_data, req_body_type):
        if isinstance(request_data, str) and req_body_type:
            request_data = json.loads(request_data)

        request_data = request_data or None
        if req_body_type == "form":
            data = {"data": request_data}
            return data
        elif req_body_type in ["raw", "json"]:
            data = {"json": request_data}
            return data
        elif req_body_type == "file":
            data = {"files": request_data}
            return data
        return {"json": request_data}



