# _*_encoding=utf8_*_
# @Time : 2021/4/29 17:37 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import json
import time

import allure

from gaintstar.drivers.basicDriver import BaseDriver
from gaintstar.globalSetting import plus_setting
from gaintstar.sessionManage.requestsSession import HTTPSession
from gaintstar.utils.logger import logger
from gaintstar.utils.initTest import _Config
from gaintstar import globalSetting


def retry(func):
    def inner(cls, data_set, model_set, uuid=None, host='', locust_session=None):
        retry = data_set.get("retry") or 1
        delay = data_set.get("delay") or 0
        while retry:
            try:
                globalSetting.WAIT_TIME_COUNT += delay
                time.sleep(delay)
                func(cls, data_set, model_set, uuid=uuid, host=host, locust_session=locust_session)
                break
            except Exception as e:
                retry -= 1
                if retry:
                    logger.error(f"【执行错误】{e}")
                    logger.info(f"【正在重试】正在进行下一次尝试···")
                else:
                    raise e
    return inner


class HTTPDriver(BaseDriver):
    header = plus_setting.HTTP_REQUEST_HEADER
    session_class = HTTPSession

    @classmethod
    @retry
    def run(cls, data_set, model_set, uuid=None, host='', locust_session=None):
        """
        请求接口执行并返回接口请求结果
        :param model_set: 模型信息
        :param uuid: 当前节点的uuid
        :param data_set: 接口用例请求数据集，根据项目可自定，run方法实现接口请求
        :param locust_session: Http请求会话
        :return: 返回一个接口请求结果
        """
        host = host or _Config.environment.get("default")  # 获取所有接口的默认前置域名
        session = data_set.get("session")
        http_session = cls.session_class.get_session(session, locust_session=locust_session)
        req_query = cls.analyze(data_set.get("req_query") or None, uuid)  # 参数化求数据
        req_body = cls.analyze(data_set.get("req_body"), uuid)
        headers = cls.analyze(data_set.get("headers") or {}, uuid)
        sleep = data_set.get('sleep')
        method = model_set.get("method")
        path = model_set.get("path")
        req_body_type = model_set.get("req_body_type") or model_set.get("dataType")
        # 解析url中路径参数
        # /api/{project}/interface/{id}/
        # {"key_path": {"project": 12, "id":2}}
        if data_set.get("key_path"):
            path = path.format(**data_set.pop("key_path"))
        path = cls.analyze(path, uuid)
        request_param_patch = cls.request_param_type_match(req_body, req_body_type)
        with allure.step("发送请求"):
            http_session.headers.update(headers)
            response = cls.session_class.send(  # 发送session会话请求
                http_session,
                method=method,
                url=host+path,
                params=req_query,
                **request_param_patch
            )

            if sleep:
                logger.info(f"【等待】等待 {sleep} 秒")
                time.sleep(sleep)
                globalSetting.WAIT_TIME_COUNT += sleep

            logger.info(f"【请求信息】api={host+path} method={method} req_body={json.dumps(request_param_patch, ensure_ascii=False)}"
                        f"req_body_type={req_body_type} param={json.dumps(req_query, ensure_ascii=False)}")

            # allure.attach(name='请求信息',
            #               body=f"api={host+path}\n"
            #                    f"req_body={json.dumps(request_param_patch, ensure_ascii=False)}\n"
            #                    f"req_body_type={req_body_type}\n"
            #                    f"method={method}\n"
            #                    f"param={json.dumps(req_query, ensure_ascii=False)}",
            #               attachment_type=allure.attachment_type.JSON
            #               )
        try:
            if "</html>" in response.text:
                logger.info(f"【接口返回】html响应数据")
            else:
                logger.info(f"【接口返回】response={response.text}")

            with allure.step("变量提取"):
                extract_content = cls.analyze(data_set.get("extract"), uuid) or {}
                logger.info(f"【变量提取】extract_expression={json.dumps(extract_content, ensure_ascii=False)}")
                extract_result = cls.extract(response, extract_content, uuid) or {}  # 执行保存变量操作
                # allure.attach(
                #     name="提取结果",
                #     body=f"extract_content={json.dumps(extract_content, ensure_ascii=False)}\n"
                #          f"extract_result={json.dumps(extract_result, ensure_ascii=False)}\n"
                #          f"response={response.text}",
                #     attachment_type=allure.attachment_type.JSON
                # )
            logger.info(f"【提取结果】extract_result={json.dumps(extract_result, ensure_ascii=False)}")
            with allure.step("请求断言"):

                # 解析断言内容
                cls.check(data_set.get("assert", {}), response, uuid=uuid)  # 执行数据断言操作

        except AssertionError as e:
            allure.attach(
                name="断言出错",
                body=f"origin={json.dumps(data_set.get('assert', []), ensure_ascii=False)}\nresponse={response.text}",
                attachment_type=allure.attachment_type.JSON,
            )
            logger.error(
                f"【请求数据】：path={path}， req_query={req_query}, req_body={req_body}, method={method}, body_type={req_body_type}")
            logger.error(f"【返回数据】：path={path}， status_code={response.status_code},response={response.text}")
            raise e
        except Exception as e:
            logger.error(f"【请求数据】：path={path}, req_query={req_query}, req_body={req_body}, method={method}, body_type={req_body_type}")
            # logger.error(f"【数据提取】：expression={extract_content}")
            logger.error(f"【返回数据】：path={path}, status_code={response.status_code},response={response.text}")
            raise e

    @classmethod
    def request_param_type_match(cls, request_data, req_body_type):
        if request_data and isinstance(request_data, str) and req_body_type:
            request_data = json.loads(request_data)

        if request_data == "":
            request_data = None

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


class SimpleHttpDriver(BaseDriver):
    session_class = HTTPSession
    header = plus_setting.HTTP_REQUEST_HEADER  # type: dict

    @classmethod
    def run(cls, step_name, url:str, user, method, param, assert_content, extract=(), headers=None):
        url = cls.analyze(url)  # type: str
        if not url.startswith('http'):
            url = _Config.environment.get("default")
        path_param = param.pop('key_path', {})
        url = url.format(**path_param)
        headers = cls.header.update(headers or {})
        param = cls.analyze(param)
        with allure.step(step_name):
            logger.info(f"【请求信息】url={url}, method={method}, user={user}, param={param}")
            response = cls.session_class.send(
                user=user,
                method=method,
                url=url,
                headers=headers,
                **param
            )
        assert_content = cls.analyze(assert_content)
        cls.check(assert_content=assert_content, response=response)
        extract = cls.analyze(extract)
        extract_result = cls.extract(response, extract)
        logger.info(f"【提取结果】extract_result={extract_result}")


