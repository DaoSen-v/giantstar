import os

from tool.model import GetModelInfo
GIANT_SETTING = {
    "BASE_DIR": os.path.dirname(os.path.realpath(__file__)),  # 这个是必不可少的
    "TEST_FILES": ["gaintstar_api.json"],
    "DATA_FILES": {"default": "./dataTable/data.xlsx"},
    "PARAMETRIC_CLASS": [GetModelInfo],
    "REMOTE": False,
    "DEBUG": True,
}

