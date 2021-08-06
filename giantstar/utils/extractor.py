# _*_encoding=utf8_*_
# @Time : 2021/5/18 15:00 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import re
import json

import jmespath
from parsel import Selector
from requests import Response
from selenium.webdriver.remote.webdriver import WebDriver

from giantstar.utils.logger import logger
from giantstar.utils.error import PatchTypeError, NoSuchExtractor

int_compile = re.compile(r'(^\d+$)')
parsel_compile =  re.compile(r'^(xpath|reg|css):(.*)')
header_compile = re.compile(r'^header:(.*)')
jmespath_compile = re.compile(r'[\[\]]')


def patch_expr(response, expresion: str):
    """
    使用表达式提取会话返回结果
    :param response: 会话返回对象
    :param expresion: eg. expresion in
        "id",
        "data.0.project_name",
        "data[?id=`12`].project_name",
        "xpath://a[@name='username']",
        "reg:^test_plus",
        "header:Content-type",
        "$",
        "status_code"
    :return: list
    """
    if isinstance(response, WebDriver):  # 用于web UI解析
        parsel_search = parsel_compile.findall(expresion)
        if expresion == "$":  # 返回文本本身
            return response
        if  parsel_search:
            return parsel_extract(response.page_source, parsel_search)
        raise NoSuchExtractor(f"【数据提取】数据提取表达式错误，webdriver response 不支持此表达式：{expresion}")

    elif isinstance(response, Response): # 用于http Api解析
        parsel_search = parsel_compile.findall(expresion)
        header_search = header_compile.findall(expresion)
        jmespath_search = jmespath_compile.findall(expresion)
        if expresion == "$":  # 返回文本本身
            return [response.text]
        elif expresion == "status_code":  # 返回http响应状态码
            return [response.status_code]
        elif header_search: # 处理头部返回结果提取
            return header_extract(response.headers, header_search[0])
        elif parsel_search:  # 处理结果返回html页面结果
            return parsel_extract(response.text, parsel_search)
        elif '.' not in expresion:  # 返回key形式保存的结果
            return key_extract(response.json(), expresion)
        elif jmespath_search:  # 返回jmespath保存的结果 data[0].id
            return jmespath_extract(response.json(), expresion)
        elif "." in expresion:  # 返回通过json层级取值的结果 data.0.id
            return json_extract(response.json(), expresion)
        raise NoSuchExtractor(f"【数据提取】数据提取表达式错误，api response 不支持此表达式：{expresion}")

    else:
        if expresion == "$":  # 返回文本本身
            return response
        else:
            return key_extract(response, expresion)


def key_extract(raw_data, key):
    """
    遍历返回的json数据获取想要保存的值
    :param raw_data: 提取key的json对象
    :param key: 需要提取的key
    :return: 一个保存的结果
    """
    value = []
    if isinstance(raw_data, dict):
        for k, v in raw_data.items():
            if k == key:
                value.append(v)
            value.extend(key_extract(v, key))
    elif isinstance(raw_data, (list, tuple)):
        for v in raw_data:
            value.extend(key_extract(v, key))
    return value


def json_extract(raw_data, expr):
    var_path_list = expr.split('.')
    new_data = raw_data.copy()
    try:
        for var in var_path_list:
            if int_compile.findall(var):
                new_data = new_data[int(var)]
            else:
                new_data = new_data[var]
        return [new_data] if new_data != None else None
    except (KeyError, IndexError) as e:
        logger.error(f"【变量提取】【failed】提取表达式={expr}, raw_data={json.dumps(raw_data, ensure_ascii=False)}")
        return None
        # raise e


def header_extract(header, expr):
    return json_extract(header, expr)


def jmespath_extract(raw_data, expr):
    expr = expr.replace('"', "'")
    result = jmespath.search(expr, raw_data)
    return result if isinstance(result, list) else [result]


def parsel_extract(html, patch_content):
    """
    使用parsel解析html返回对象
    :param patch_content: 匹配内容
        Example：
            [('xpath', '//*[@name="baidu"]/@href')]
    :param html: html页面源码
    :return:
    """
    patch_type, expr = patch_content[0]
    if patch_type == 'xpath':
        return Selector(html).xpath(expr).getall()
    elif patch_type == 'reg':
        return Selector(html).re(expr)
    elif patch_type == 'css':
        return Selector(html).css(expr).getall()
    raise PatchTypeError(
        f"【提取类型】不支持提取类型 patch_type={patch_type}, gaintstar支持方式：[xpath, css, reg, header]"
    )
