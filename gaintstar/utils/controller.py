# -*- coding: utf-8 -*-
# 用于管理
import mimetypes
import os
import uuid
from json import JSONDecodeError
from typing import List, Union

import jmespath
import requests

from selenium.webdriver.remote.webdriver import WebDriver
from appium.webdriver.webdriver import WebDriver as AppDriver

from gaintstar.utils.logger import logger
from gaintstar.globalSetting import plus_setting
from gaintstar.utils.initTest import _Config


class OCRDiscern:
    """ OCR识别 """
    location = {}
    coord = []
    @classmethod
    def acquire_coords_by_word(cls, driver: WebDriver, location: List):
        """
        获取OCR元素定位坐标
        :param driver: selenium webdriver 对象
        :param location:
            {"target": "被识别文字/图片路径", "offset_x": "1", "offset_y": "2", "element_id": 123}
        :return:
        """
        img_name, file_data = cls.save_screen(driver, location)
        file_data["discern_word"] = (None, location[1])
        response = requests.post(_Config.platform_host+ '/api/img_word/get_xy/', files=file_data)
        try:
            os.remove(img_name)  # 删除临时图片
            coords_list = jmespath.search('data.wordCoordinate', response.json())
            logger.info(f'【OCR文字识别】 识别结果={response.json()}')
            if coords_list:
                for value in coords_list:
                    for k, v in value.items():
                        cls.coord = v
                        break
                logger.info(f"【OCR点击坐标信息】info={coords_list[0]} , coord={cls.coord}")
            else:
                logger.error(f"【OCR文字识别错误】没有识别到期望结果")
            # 处理已'%'开头和'%'结尾的location

            return cls
        except JSONDecodeError as e:
            logger.error(e)
            logger.error(f'【OCR文本识别】failed 接口返回信息{response.text}, status_code={response.status_code}')

    @classmethod
    def acquire_coords_by_image(cls, driver: WebDriver, location: List):
        img_name, file_data = cls.save_screen(driver, location)
        file_data["target_img_url"] = (None, location[1])
        response = requests.post(_Config.platform_host + '/api/img_word/get_xy/', files=file_data)
        try:
            os.remove(img_name)  # 删除临时图片
            cls.coord = jmespath.search('data.imgCoordinate', response.json())
            logger.info(f'【OCR图片识别】 识别结果={response.json()}')
            return cls
        except JSONDecodeError as e:
            logger.error(e)
            logger.error(f'【OCR文本识别】failed 接口返回信息{response.text}, status_code={response.status_code}')

    @classmethod
    def acquire_coords(cls, driver, location, by):
        if by == 'OCR':
            return OCRDiscern.acquire_coords_by_word(driver, location)
        elif by == 'IMG':
            return OCRDiscern.acquire_coords_by_image(driver, location)

    @staticmethod
    def save_screen(driver: Union[WebDriver, AppDriver], location: List):
        UUID = uuid.uuid1()
        current_dir = plus_setting.BASE_DIR
        temp_dir = f'{current_dir}/temp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        img_name = f"{temp_dir}/{UUID}.png"
        if not isinstance(driver, AppDriver):
            driver.execute_script('window.onload')
        driver.get_screenshot_as_file(img_name)
        with open(img_name, 'rb') as f:
            content = f.read()
        file_data = {
            "originalImg": (img_name, content, mimetypes.guess_type(img_name)[0]),
            "type": (None, "aliocr"),
            "offset_x": (None, location[2][0]),
            "offset_y": (None, location[2][1]),
        }
        return img_name, file_data
