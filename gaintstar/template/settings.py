import os

from tool.model import GetModelInfo
CTTEST_SETTING = {
    "BASE_DIR": os.path.dirname(os.path.realpath(__file__)),  # 这个是必不可少的
    "TEST_FILES": ["gaintstar_api.json"],
    "DATA_FILES": {"default": "./dataTable/data.xlsx"},
    "PARAMETRIC_CLASS": [GetModelInfo],
    "REMOTE": False,
    "DEBUG": True,
}

DATA_BASE = {
    "host": "database IP",
    "port": 3306,
    "username": "database user",
    "password": "your password",
    "database": "a database name"
}