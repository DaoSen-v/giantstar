# _*_encoding=utf8_*_
# @Time : 2021/6/16 16:40 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
from giantstar.drivers.httpDriver import HTTPDriver
from giantstar.drivers.webDriver import WEBDriver
from giantstar.drivers.kwDriver import KeyWordDriver
from giantstar.drivers.appDriver import APPDriver


class Step:

    def step(self, kw_path, **kwargs):
        kwargs["data_set"]["version"] = 2
        if kw_path == "api":
            # kwargs: {
            #     "data_set": {"request":{}, "extract":[], "assert":{}, "user": "user1"},
            #     "mode_set": {"method": "get", "path":"index/login", "req_body_type": "json"},
            #     "host": ""   非必填，接口请求时重置域名
            # }
            # host 不传时默认使用settingConfig.json environment default地址
            # data_set user：不传时默认用户名default
            HTTPDriver.run(**kwargs)
        elif kw_path == "web":
            # kwargs: {
            #     "data_set": {"request":{}, "assert":{}, "user": "user", "path": "/"},
            # user：不传时默认用户名default
            # }
            kwargs["data_set"]["request"] = [kwargs["data_set"]["request"]]
            WEBDriver.run(**kwargs)
        elif kw_path == 'app':
            # kwargs: {
            #     "data_set": {"request":{}, "assert":{}, "user": "user"},
            # }
            kwargs["data_set"]["request"] = [kwargs["data_set"]["request"]]
            APPDriver.run(**kwargs)
        else:
            # kwargs: {
            #     "data_set": {"request":{}, "extract":[]},
            #     "kw": "kw_path",
            # }
            KeyWordDriver.run(kw=kw_path, **kwargs)

