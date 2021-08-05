

class NoSuchVariableError(Exception):
    """提取变量不存在"""


class MethodError(Exception):
    """参数化方法不存在"""


class YAPIRequestError(Exception):
    """yapi平台请求错误"""


class InvalidParameter(Exception):
    """无效参数"""


class UserNotExits(Exception):
    """用户不存在"""


class AssertNotSupport(Exception):
    """断言方法不支持"""


class UserKeyWordError(Exception):
    """用户自定义关键字不存在"""


class PatchTypeError(Exception):
    """变量匹配方式不存在"""


class CompatError(Exception):
    """版本兼容错误"""


class SelenoidError(Exception):
    """Selenoid平台错误"""


class OpenstfError(Exception):
    """Openstf平台错误"""


class AcquireElementError(Exception):
    """ 获取元素错误 """


class NoSuchBrowser(Exception):
    """浏览器类型不支持"""


class NoAvailableDevice(Exception):
    """云真机平台无可用设备"""


class DatabaseNoSuchData(Exception):
    """数据库无相关数据"""


class DataIndexError(Exception):
    """数据索引错误"""


class NoSuchExtractor(Exception):
    """数据提取表达式类型不支持"""
