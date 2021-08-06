# _*_encoding=utf8_*_
# @Time : 2021/5/19 9:23 

# @Author : xuyong

# @Email: yong1.xu@casstime.com

import requests

from giantstar.utils.logger import logger
from giantstar.utils.error import SelenoidError


class SelenoidController:

    def free_devices(self, host):
        """获取selenoid平台空闲设备"""
        free_devices = {}
        devices = self.get_devices(host)
        for browser_name, browser_list in devices.items():
            free_devices[browser_name] = sorted(
                [version for version, status in browser_list.items() if not status], reverse=True
            )
        return free_devices

    def specified_device(self, browser: str, version: str, host):
        """
        获取指定型号、指定版本的浏览器。检查指定设备是否可用
        :param browser: 指定版本浏览器品牌
        :param version: 指定版本浏览器版本号
        :return: bool
        """
        free_devices = self.free_devices(host)
        specified_browser_list = free_devices.get(browser)
        if specified_browser_list and version in specified_browser_list:
            return True
        return False

    def get_devices(self, host):
        """获取selenoid平台所有设备"""
        response = requests.get(host+'/status')
        devices = response.json().get("state").get("browsers")
        return devices

    def get_one(self, host, browser: str = None, version: str = None):
        """
        获取一个可用的设备
        :param browser: 指定版本浏览器品牌
        :param version: 指定版本浏览器版本号
        :return: Dict
        """
        devices = self.free_devices(host)
        if browser:  # 指定浏览器名
            version_list = devices.get(browser)
            if version_list:
                if version and version in version_list: # 指定浏览器名和版本号
                    return {"browserName": browser, "version": version}
                return {"browserName": browser, "version": version_list[0]}
        else:  # 随机获取可用版本
            for browser, version_list in devices.items():
                if version_list:
                    return {"browserName": browser, "version": version_list[0]}
