# # -*- coding: utf-8 -*-
# """
#   @Time  : 2020/7/15 21:04
#   @Auth  : zhifang.li
#   @Detail: YapiRequest Hooks
# """
# import ast
# import json
# import time
# from typing import List
# from urllib.parse import quote
# from hashlib import md5
# import pluggy
# from giantstar.utils.logger import logger
#
# hookspec = pluggy.HookspecMarker('YApiRequest')
# hookimpl = pluggy.HookimplMarker('YApiRequest')
#
#
# class CTTestSpec(object):
#     """A fxhook specification namespace.
#     """
#
#     @hookspec
#     def before_request(self, request_session, **kwargs):
#         """ 请求yapiRequest执行前 """
#
#     @hookspec
#     def after_request(self, request_session, **kwargs):
#         """ 请求yapiRequest执行后 """
#
#     @hookspec
#     def signature(self, session, secretKey, accessKey):
#         """
#         处理信息头签名函数
#         :param session: requests 请求对象
#         :param interface: 接口请求数据
#         :param kwargs: 其他自定义参数， 飞熊云平台auth接收的kwargs参数
#         :return: None
#         """
#     @hookspec
#     def check_if(self, DT, config, decide, node_info, assert_factory):
#         """
#         解析node条件判断是否成立，成立用例继续执行。否则跳过该节点
#         """
#
#
# class CTTestPlugin(object):
#     """A fxhook implementation namespace.
#     """
#     @hookimpl
#     def before_request(self, request_session):
#         """ """
#
#     @hookimpl
#     def after_request(self, request_session):
#         """ """
#
#     @hookimpl
#     def signature(self, session, secretKey, accessKey):
#         """
#         处理信息头签名函数
#         :param session: requests 请求对象
#         :param interface: 接口请求数据
#         :param kwargs: 其他自定义参数， 飞熊云平台auth接收的kwargs参数
#         :return: None
#         """
#         i = session.interface
#         body = i.req_body or i.req_query
#         quote_str = quote(str(body)).replace('%20', '+').replace('%27', '%22')
#         length = sum(map(lambda x: ord(x), quote_str))
#         timestamp = int(round(time.time() * 1000))
#         newString = str(secretKey) + str(timestamp) + str(length)
#         md5_content = md5(bytes(newString, "utf8")).hexdigest().upper()
#         session.session.headers.update({'accessSign': md5_content, 'timestamp': str(timestamp), "accessKey": accessKey})
#
#     @hookimpl
#     def check_if(self, DT, node_info, decide, assert_factory):
#         """
#         :param DT: DataTreating数据处理
#         :param config:
#         :param decide:
#         return True执行该节点，False跳过该节点
#         """
#         uuid = node_info.get('c_uuid') or ''
#         decide = DT.analyze_data(decide, uuid)
#         result = []
#         for decide_step in decide:
#             if isinstance(decide, str):
#                 result.append(ast.literal_eval(decide_step))
#             else:
#                 result.append(assert_factory.validate(var_space_name=uuid, raise_error=False, **decide_step))
#             logger.info(f'【节点入口判断】{result}')
#             return all(result), result
#         return True
#
#
# CT_TEST_PM = pluggy.PluginManager('YApiRequest')
# CT_TEST_PM.add_hookspecs(CTTestSpec)
# CT_TEST_PM.register(CTTestPlugin())
#
#
# class Hook:
#     """
#     记录所有hook类别
#     """
#     setup_hooks = []
#     teardown_hooks = []
#     before_hook = None
#     check_hook = ['check_if']
#
#     @staticmethod
#     def call_hook(hook_list, **kwargs):
#         try:
#             for hook_info in hook_list:
#                 logger.info(f'【hook函数执行】hook_name={hook_info}, hook_list={hook_list}')
#                 if isinstance(hook_info, str):
#                     return getattr(CT_TEST_PM.hook, hook_info)(**kwargs)
#                 elif hasattr(CT_TEST_PM.hook, hook_info.get('func', hook_info)):
#                     hook = getattr(CT_TEST_PM.hook, hook_info.get('func'))
#                     res = hook(**kwargs, **hook_info.get('kwargs', {}))
#                     if res:
#                         return res
#         except Exception as e:
#             logger.error(e)

def cttest_name(age, name):
    pass