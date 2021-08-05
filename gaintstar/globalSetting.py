import os
import importlib
import uuid


IMPORT_STRINGS = [
    "KW_DRIVER",
    "ANALYZE_CLASS",
    "ASSERT_CLASS",
    "APP_DRIVER",
    "HTTP_DRIVER",
    'WEB_DRIVER',
    "DRIVER_BY",
    "DEBUG_DRIVER",
    "APP_SIMPLE_DRIVER",
    "WEB_SIMPLE_DRIVER",
    "HTTP_SIMPLE_DRIVER"
]

WAIT_TIME_COUNT = 0

REMOVED_SETTINGS = []

DYNAMIC_FILE = f"{str(uuid.uuid1())}.json"

DYNAMIC_SETTING_FILE = f"{str(uuid.uuid1())}.json"

DEFAULTS = {
    "BASE_DIR": os.path.dirname(os.path.realpath(__file__)),
    "PRINT_STACK": False,
    "DEBUG": True,  #
    "LEVEL": "INFO",
    "SELENOID_HOSTS": ['http://10.118.71.154', 'http://10.118.71.155'],
    "TEST_FILES": ['cttest_case.json'],
    "DATA_FILES": {"default": ""},
    "HTTP_REQUEST_HEADER": {},
    "PARAMETRIC_CLASS": [],
    "TIMEOUT_SEARCH": 10,
    "DATABASE": {
        "default":{
            'host': '10.118.71.122',
            'user': 'murphy',
            'port': 3306,
            'password': 'hkoe;dlh&dsfVF5zv',
            'database': 'data_manage',
            'charset': 'utf8'
        }
    },
    "ANALYZE_CLASS": "gaintstar.utils.dataParser.JsonParser",
    "DRIVER_BY": "gaintstar.drivers.driverBy.DriverBy",
    "KW_DRIVER":"gaintstar.drivers.kwDriver.KeyWordDriver",
    'HTTP_DRIVER': "gaintstar.drivers.httpDriver.HTTPDriver",
    'WEB_DRIVER': "gaintstar.drivers.webDriver.WEBDriver",
    'APP_DRIVER': "gaintstar.drivers.appDriver.APPDriver",
    "DEBUG_DRIVER": "gaintstar.drivers.debugDriver.DebugDriver",
    "HTTP_SIMPLE_DRIVER":"gaintstar.drivers.httpDriver.SimpleHttpDriver",
    "WEB_SIMPLE_DRIVER":"gaintstar.drivers.webDriver.SimpleWEBDriver",
    "APP_SIMPLE_DRIVER":"",
    "APK": None,
    "IPA": None,
    "REMOTE": True,
    "SELENOID": {
        "hosts":  ['http://10.118.71.154', 'http://10.118.71.155'],
        "selenoid_video_dir": "/home/selenoid_ui/video",
        "nginx_video_dir": "/html/video/web",
        "video_url_prefix": "/video/web",
    },
    "OPENSTF": {
        "host": "",
        "token": "",
        "android_provider": {
            "host": "",
            "port": 22,
            "username": "",
            "password": "",
        },
        "ios_provider": {
            "host": "",
            "port": 22,
            "username": "",
            "password": "",
        },
        "android_package_dir": "",
        "ios_package_dir": ""
    }
}


try:
    CUSTOMER_SETTINGS = importlib.import_module('settings')  ## 导入用户自定义CT_TEST设置
except ModuleNotFoundError as e:
    CUSTOMER_SETTINGS = {}


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        ) from err

def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        raise e

class Setting:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(CUSTOMER_SETTINGS, 'CTTEST_SETTING', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        SETTINGS_DOC = "https://zhishiku.casstime.com/pages/viewpage.action?pageId=65350353"
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError("The '%s' setting has been removed. Please refer to '%s' for available settings." % (
                setting, SETTINGS_DOC))
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')

plus_setting = Setting()
