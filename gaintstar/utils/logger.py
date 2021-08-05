# _*_encoding=utf8_*_
# @Time : 2021/5/7 9:44 

# @Author : xuyong

# @Email: yong1.xu@casstime.com

import logging
from loguru import logger

from gaintstar.globalSetting import plus_setting


class PlusHandler(logging.Handler):
    def emit(self, record):
        logging.getLogger(record.name).handle(record)


logger.add(PlusHandler(), format="{time:YYYY-MM-DD HH:mm:ss} | {message}", level=plus_setting.LEVEL)
