# _*_encoding=utf8_*_
# @Time : 2021/6/16 15:08 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import requests

class GetModelInfo:
    @classmethod
    def get_model(cls, model_id):
        return YAPIController().model(model_id) or FlyBearController().model(model_id)

class Singleton:
    _instance = {}

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        if self.func.__name__ not in self._instance:
            self._instance[self.func.__name__] = self.func(*args, **kwargs)
        return self._instance[self.func.__name__]


@Singleton
class YAPIController:
    """YApi模型接口信息获取刷新信息"""
    def __init__(self):
        USER = {
            "host": "http://10.118.71.202:3000",
            "username": "yong1.xu@casstime.com",
            "password": "123456",
        }
        self.host = USER["host"]
        self.session = requests.session()
        data = {'email': USER["username"], 'password': USER["password"]}
        res = self.session.post(USER["host"] + '/api/user/login', json=data)
        if res.json()['errcode'] != 0:
            raise Exception(f'登录yapi失败！, user_info: {data}, error_info: {res.text}')

    def model(self, model_id):
        """
        更新Interface接口属性信息
        :param model_id: 接口的模型id
        :param model_class: 接口的模型数据属性类
        :return: None
        """
        response = self.session.get(self.host + '/api/interface/get', params={'id': model_id}).json()
        api_info = response.get("data")
        if api_info:
            path = api_info.get('path')
            method = api_info.get("method")
            req_body_type = api_info.get("req_body_type")
            return {"method": method, "req_body_type": req_body_type, "path": path}


@Singleton
class FlyBearController:
    host = "http://10.7.0.96:8070"
    obtain_model_url = "/api/automation/model_info/"
    def __init__(self):
        self.session = requests.session()

    def model(self, model_id):
        response = self.session.get(self.host + self.obtain_model_url, params={"model_id": model_id}).json()
        api_info = response.get("data")
        if response.get("data"):
            path = api_info.get('path')
            method = api_info.get("method")
            req_body_type = api_info.get("req_body_type")
            return {"method": method, "req_body_type": req_body_type, "path": path}
