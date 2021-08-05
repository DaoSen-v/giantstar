# _*_encoding=utf8_*_
# @Time : 2021/5/7 9:16 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
from collections import OrderedDict

import requests

from gaintstar.sessionManage.baseSession import BaseSession
from gaintstar.utils.error import UserNotExits
from gaintstar.utils.dataParser import JsonParser

class HTTPSession(BaseSession):
    """
    一个用于管理Http会话的类
    """
    session_list = OrderedDict()
    session_type = "httpUser"
    http_user_code = {}

    @classmethod
    def new_session(cls, session_name, locust_session=None):
        """
        新建会话
        :param session_name: 会话名称/用户名称
        :param build_content: "httpUser"用户登录配置
        :return: None
        """
        if not cls.session_list:
            cls.http_session_config = cls.session_config.get(cls.session_type)

        build_content = cls.http_session_config.get(session_name)
        cls.build_session_by_step(session_name, build_content, locust_session=locust_session)

    @classmethod
    def build_session_by_code(cls, session_name, locust_session=None):
        """
        通过执行python代码实现登录会话
        :param session_name: 用户名（会话名）
        :param code_string: 用户登录可执行的python代码字符串
            class HttpUser:
                def user_1():
                    import requests
                    session = requests.session()
                    login_data = {"username": "your name", "password": "your password"}
                    response = .post("http://www.demo.com/login", json=login_data)
                    # 校验是否登陆成功session返回一个成功登录的session
                    return session
                def user_2():
                    return user2 session

            class WebUser:
                # 填写web user 登录代码

            class AppUser:
                # 填写app user 登录代码
        :return:
        """
        if cls.http_user_code:  # 判断是否执行过code_string
            pass
        else:
            code_string = cls.session_config.get("codeString")
            exec(code_string, cls.http_user_code)
        if "HttpUser" in cls.http_user_code and hasattr(cls.http_user_code["HttpUser"], session_name):
            cls.session_list[session_name] = getattr(cls.http_user_code["HttpUser"], session_name)()
        else:
            raise UserNotExits(f"【用户错误】用户名：{session_name} 不存在，请检查项目登录配置是否添加该用户")

    @classmethod
    def build_session_by_step(cls, session_name, step_data, locust_session=None):
        """
        通过接口访问，来实现http会话登录
        :param session_name: 会话名称
        :param step_data: 实现登录的数据步骤
            Example:
            [
                {
                    "url": "https://demo.com/login",
                    "data"={}, "bodyType": "json",
                    "extract":[
                        "token",
                        ["data.0.project_name", "project_name"],
                        ["data[?id=`12`].project_name", "project_name"],
                        ["xpath://a[@name='username']::value", "name"],
                        ["reg:^test_plus", "runner"],
                        ["css:#id", "id"],
                        ["header:Content-type", "content_type"],
                        ["$", "text"],
                        ["status_code", "code"]
                    ],
                    "header":{}
                    "after":{"headers":{"authration": "Bear @{token}"}}
                },
                {"url": "https://demo.com/login", "data"={}, "bodyType": "json", "extract":[], "header":{}},
            ...
            ]
            or
            "${function(*args, **kwargs)}"
        :return: NoReturn
        """
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
        cls.session_list[session_name] = session

    @classmethod
    def send(cls, user, **kwargs):
        session = cls.get_session(user)
        response = session.request(**kwargs)
        return response

