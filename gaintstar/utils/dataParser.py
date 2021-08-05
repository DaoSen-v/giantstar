import importlib
import re

from faker import Faker
from requests import Session
from selenium.webdriver.remote.webdriver import WebDriver

from gaintstar.utils.error import NoSuchVariableError
from gaintstar.utils.extractor import patch_expr
from gaintstar.utils.logger import logger
from gaintstar.globalSetting import plus_setting
from gaintstar.utils.fileReader import ExcelReader, MysqlReader


class GlobalVariableMap:
    """
    返回值参数化保存的全局变量视图，函数视图, 类视图
    """
    func_map = {}
    class_map = plus_setting.PARAMETRIC_CLASS + [ExcelReader, MysqlReader, Faker(locale='zh_CN')]
    var_map = {}


var_compile = re.compile(r'@{(.*?)}')
func_compile = re.compile(r'\${(.*?)\((.*?)\)}')
int_compile = re.compile(r'(^\d+$)')
parsel_compile = re.compile(r'^(xpath|reg|css):(.*)')
header_compile = re.compile(r'^header:(.*)')
jmespath_compile = re.compile(r'[\[\]]')


class JsonParser:
    global_map = GlobalVariableMap
    user_map = {}
    @classmethod
    def get_variable(cls, var_name, uuid, owner_var_map=None):
        # 兼容版本函数
        var_map = owner_var_map or cls.global_map.var_map
        var_map = var_map if not uuid else var_map.get(uuid)
        return var_map.get(var_name)

    @classmethod
    def get_class_map_setting(cls, setting_file='settings'):
        """
        从项目配置文件中获取类注册的视图CLASS_MAP = []
        :return: None
        """
        settings = importlib.import_module(setting_file)
        if hasattr(settings, 'CLASS_MAP'):
            cls.global_map.class_map.extend(settings.CLASS_MAP)
            
    @classmethod
    def extract(cls, save_key_list, response, uuid=None, owner_var_map: dict=None):
        """
        保存接口返回的响应数据
        :param uuid:
        :param save_key_list: 需要保存的数据列表
        :param response: 会话返回对象
        :return: type: dict
        """
        extract_result = {}
        var_map = owner_var_map or cls.global_map.var_map
        var_map = var_map if not uuid else var_map.get(uuid)
        for content in save_key_list:
            default = []
            if isinstance(content, list) and len(content) == 3:
                default.append(content.pop(2))
            expr, key = content if isinstance(content, list) else (content, content)
            result = patch_expr(response, expr)
            if isinstance(result, (Session, WebDriver)):
                cls.user_map[key] = result
            else:
                if default and not result:
                    extract_result[key] = default
                elif not default and result == None:
                    raise NoSuchVariableError(
                        f"【变量提取错误】不存在该变量, 变量提取内容为空, extract_content={save_key_list} "
                        f"提取表达式={expr}. 可添加default默认值. "
                        f"eg:{{'variable_name': 'gameId_1', 'variable_expression': 'gameId',"
                        f"'variable_type': 'json', 'default': 11}}"
                    )
                else:
                    extract_result[key] = result
        var_map.update(extract_result)
        return extract_result

    @classmethod
    def get_user(cls, user):
        if not user:
            return user
        user_session = cls.user_map[user]
        logger.info(f"【用户替换】user={user} changed into {user_session}, type={type(user_session).__name__}")
        return user_session

    @classmethod
    def get_var_map_value(cls, var_key, uuid, owner_var_map=None):
        """

        :param uuid:
        :param var_key: 需要替换数据的key值
        :return: 返回key在视图中对应得值
        """
        var_map = owner_var_map or cls.global_map.var_map
        var_map = var_map if not uuid else var_map.get(uuid)
        var_key_list = var_key.strip(' ').split('.')
        try:
            if len(var_key_list) == 1:
                var_key_list.append('0')
            value, index = var_map[var_key_list[0]], var_key_list[1]
            if int_compile.findall(index):
                index = int(index)
                value = value[index] if isinstance(value, list) else value
            elif index == 'all':
                pass
            logger.info(f'【数据替换】 success --> @{{{var_key}}} changed into {value}, type={type(value).__name__}')
            return value
        except Exception:
            raise ValueError(f'【数据替换】--> failed @{{{var_key}}}, can`t get expected value, please '
                             f'check {var_key_list[0]} has been saved before use or index number is not empty')

    @classmethod
    def get_class_func(cls, func_name, arg_string):
        """
        获取设置类下面所有函数查找需要的函数进行替换
        :param func_name: 获取到需要替换的函数名称
        :param arg_string: 函数参数字符串
        :return: 返回类方法的掉用结果
        """
        for class_fun in cls.global_map.class_map:
            if hasattr(class_fun, func_name):
                value = eval(f'''class_fun.{func_name}({arg_string})''')
                return value
        logger.error(f'【函数替换】failed --> can`t find function name like {func_name}()')

    @classmethod
    def get_func_map_value(cls, func_name, func_args):
        """
        使用函数计算值
        :param func_name: 函数名称
        :param func_args: 函数参数字符串
        :return:
        """
        # 此处做版本兼容后续恢复后删除此内容 random.int()
        func_name = func_name.replace('.', '__')
        try:
            if func_name not in cls.global_map.func_map:
                func_value = cls.get_class_func(func_name, func_args)
                logger.info(
                    f'【数据处理】success --> func_name=${{{func_name}({func_args})}} changed into {func_value} '
                    f'type={type(func_value).__name__}'
                )
                return func_value
            else:
                _ = cls.global_map.func_map[func_name]
                func_value = eval(f'''_({func_args})''')
                logger.info(
                    f'【数据处理】success -->func_name=${{{func_name}({func_args})}} changed into {func_value} '
                    f'type={type(func_value).__name__}'
                )
                return func_value
        except Exception as e:
            logger.error(f'【参数错误】：请检查参数是否合法，Exception={str(e)}')
            raise e
        
    @classmethod
    def analyze_string(cls, raw_string, uuid, owner_var_map=None):
        """
        分析请求参数的value
        :param uuid:
        :param raw_string:
        :return:
        """
        replace_var_list = var_compile.findall(raw_string)
        if replace_var_list:
            if raw_string == f'@{{{replace_var_list[0]}}}':
                return cls.get_var_map_value(replace_var_list[0], uuid=uuid, owner_var_map=owner_var_map)
            for var_key in replace_var_list:
                raw_string = raw_string.replace('@{%s}' % var_key, str(cls.get_var_map_value(var_key, uuid=uuid, owner_var_map=owner_var_map)))
        replace_func_list = func_compile.findall(raw_string)
        if replace_func_list:
            string1 = f'${{{replace_func_list[0][0]}({replace_func_list[0][1]})}}'
            if raw_string == string1:
                return cls.get_func_map_value(replace_func_list[0][0], replace_func_list[0][1])
            for func in replace_func_list:
                func_name, args = func
                raw_string = raw_string.replace(
                    '${%s(%s)}' % (func_name, args), str(cls.get_func_map_value(func_name, args))
                )

        return raw_string

    @classmethod
    def analyze(cls, raw_data, uuid=None, owner_var_map: dict=None):
        """
        分析请求数据结构
        :param uuid:
        :param raw_data:
        :return:
        """
        if isinstance(raw_data, dict):
            analyzed_data = {}
            for key, value in raw_data.items():
                key = cls.analyze(key, uuid=uuid, owner_var_map=owner_var_map)
                analyzed_data[key] = cls.analyze(value, uuid=uuid, owner_var_map=owner_var_map)
            return analyzed_data
        elif isinstance(raw_data, (list, tuple, set)):
            return [
                cls.analyze(items, uuid=uuid, owner_var_map=owner_var_map) for items in raw_data
            ]

        elif isinstance(raw_data, str):
            raw_data.strip(' \t')
            return cls.analyze_string(raw_data, uuid=uuid, owner_var_map=owner_var_map)

        else:
            return raw_data

    @classmethod
    def remove_local_variable(cls, uuid):
        if uuid:
            cls.global_map.var_map.pop(uuid)

    @classmethod
    def add_variable(cls, add_params, uuid=None, owner_var_map=None):
        if not add_params:
            add_params = {}

        add_params = cls.analyze(raw_data=add_params, uuid=uuid, owner_var_map=owner_var_map)
        var_map = owner_var_map or cls.global_map.var_map

        if uuid:
            if var_map.get(uuid):
                var_map[uuid].update(add_params)
            else:
                var_map[uuid] = add_params
        else:
            var_map.update(add_params)

    @classmethod
    def add_variable_from_out_param(cls, variable_list, parent_uuid, uuid, owner_var_map=None):
        var_map = owner_var_map or cls.global_map.var_map
        bm_map = var_map[uuid]
        new_variable = {k: bm_map.get(k) for k in variable_list}
        cls.add_variable(new_variable, parent_uuid, owner_var_map=owner_var_map)
