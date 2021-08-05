# _*_encoding=utf8_*_
# @Time : 2021/5/27 17:25 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import time
from typing import List, Union, Type, NoReturn

import allure
from appium.webdriver import WebElement
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, InvalidSelectorException
from selenium.webdriver import ActionChains
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as ec
from appium.webdriver.common.mobileby import MobileBy

from gaintstar.globalSetting import plus_setting
from gaintstar.sessionManage.webSession.element import _Select, Input, MouseEvent, WindowEvent, CompatElement
from gaintstar.utils.logger import logger
from gaintstar.utils.controller import OCRDiscern
from gaintstar.utils.error import AcquireElementError
# from gaintstar.utils.dataParser import JsonParser

def interceptor_operations(timeout):
    exception = {"e": None}
    # out_time = timeout
    def out(func):
        def interceptor(cls, browser: WebDriver,  locations: List, event):
            start_time = int(time.time())
            end_time = int(time.time())
            # browser.switch_to.default_content()

            if event == 'scroll_into_view':
                out_time = timeout + 10
            else:
                out_time = timeout
            while end_time-start_time < out_time:
                time.sleep(1)
                ele = func(cls, browser, locations, event, exception)
                if ele: return ele
                end_time = int(time.time())
            if event == "click_if_exits":
                logger.info(f"【可见则点击】没有发现可见则点击的元素")
            else:
                logger.error(f'【元素定位】遍历所有元素后定位失败, location={locations}')
                allure.attach(
                    body=browser.get_screenshot_as_png(),
                    name=f"【页面等待超时】locations={locations}",
                    attachment_type=allure.attachment_type.PNG
                )
                raise exception["e"]

        return interceptor
    return out


class FindElement:
    @classmethod
    @interceptor_operations(plus_setting.TIMEOUT_SEARCH)
    def find_element(
            cls, browser: WebDriver, locations: List, event: str, exception
    ) -> Union[Type[OCRDiscern], WebElement, List]:
        """
        通过location定位方式定位元素
        :param driver: WebDriver对象
        :param by: in [OCR XPATH LINK_TEXT PARTIAL_LINK_TEXT NAME TAG_NAME CLASS_NAME CSS_SELECTOR]
            Example:
                IOS_PREDICATE
                IOS_UIAUTOMATION
                IOS_CLASS_CHAIN
                ANDROID_UIAUTOMATOR
                ANDROID_VIEWTAG
                ANDROID_DATA_MATCHER
                ANDROID_VIEW_MATCHER
                WINDOWS_UI_AUTOMATION
                ACCESSIBILITY_ID
                IMAGE
                CUSTOM
        :param location:
            元素定位时定位的表达式 eg. XPATH的location： //input[@id='kw']
        :return: 返回元素对象或者，OCR坐标
        """
        if event == "scroll_into_view":
            window_size_info = browser.get_window_size()
            x, y = window_size_info['width'], window_size_info['height']
            start_x, start_y, end_x, end_y = 1/2*x, 3/4*y, 1/2*x, 1/4*y
            logger.info(f"【屏幕滑动】======上滑半个屏幕======")
            browser.swipe(start_x, start_y, end_x, end_y)
        elif event == "swipe_screen":
            window_size_info = browser.get_window_size()
            x, y = window_size_info['width'], window_size_info['height']
            start_x, start_y, end_x, end_y = 1 / 2 * x, 2 / 3 * y, 1 / 2 * x, 1 / 3 * y
            logger.info(f"【屏幕滑动】======上滑半个屏幕======")
            browser.swipe(start_x, start_y, end_x, end_y)
        for location in locations:
            by, value, offset = location
            if by == 'OCR':
                return OCRDiscern.acquire_coords_by_word(browser, location)
            elif by == 'IMG':
                return OCRDiscern.acquire_coords_by_image(browser, location)
            else:
                by = getattr(MobileBy, by.upper())
                try:
                    # WebDriverWait(browser, 1, 0.5).until(ec.visibility_of_element_located((by, value)))
                    # WebDriverWait(browser, 1, 0.5).until(ec.visibility_of_all_elements_located((by, value)))
                    # logger.info(f'【元素定位】location={location}, by={by}, offset={offset}, event={event}')
                    ele = browser.find_element(by, value)
                    if isinstance(ele, list):
                        raise AcquireElementError(f"【元素获取】期望获取到一个元素定位，但获得了{len(ele)}个元素")
                    logger.info(f'【元素定位】元素定位成功, location={location}, event={event}')
                    return ele
                except InvalidSelectorException as e:
                    continue
                except (NoSuchElementException, TimeoutException) as e:
                    exception["e"] = e
                    continue


class AppWindowEvent(WindowEvent):
    @classmethod
    def scroll_into_view(cls, ele: WebElement, browser: WebDriver) -> NoReturn:
        pass


class Button:
    @classmethod
    def click(cls, ele: Union[Type[OCRDiscern], WebElement], browser: WebDriver) -> NoReturn:
        # ActionChains(browser).reset_actions()

        if isinstance(ele, WebElement):
            # coord, size = ele.location, ele.size
            # x = coord["x"] + size['width'] / 2
            # y = coord["y"] + size['height'] / 2
            # logger.info(f"元素坐标【{x}, {y}】")
            # ActionChains(browser).move_by_offset(x, y).click().perform()
            ele.click()

        elif issubclass(ele, OCRDiscern):
            coords = ele.coord
            logger.info(f"【正在点击坐标】coord={coords}")
            TouchAction(browser).tap(x=coords[0], y=coords[1]).perform()
            # ActionChains(browser).move_by_offset(*coords).click().perform()
        time.sleep(1)

    @classmethod
    def right_click(cls, browser: WebDriver, ele: WebElement) -> NoReturn:
        ActionChains(browser).context_click(ele).perform()

    @classmethod
    def double_click(cls, browser: WebDriver, ele: WebElement) -> NoReturn:
        ActionChains(browser).double_click(ele).perform()

    @classmethod
    def click_if_exits(cls, ele: Union[Type[OCRDiscern], WebElement], browser: WebDriver):
        if isinstance(ele, WebElement):
            cls.click(ele, browser)
            logger.warning(f'【click_if_exits】执行存在则点击操作成功')
        elif ele and issubclass(ele, OCRDiscern) and ele.coord:
            cls.click(ele, browser)
            logger.warning(f'【click_if_exits】执行存在则点击操作成功')
        else:
            logger.warning(f'【click_if_exits】没找到元素不执行点击操作')


class CTElement(_Select, Button, Input, MouseEvent, AppWindowEvent, CompatElement):
    """ 元素对象处理 """


class Swipe:

    def _gen_swipe_args(self, browser, direction='down', max_swipe_screen_count=3.0):
        '''
        生成滑动屏幕参数
        :param direction: 滑动方向 up/down/left/right
        :param max_swipe_screen_count: 滑动屏幕距离
        :return: start_x, start_y, end_x, end_y, swipe_step, swipe_total_distance
        '''
        window_size_info = browser.get_window_size()
        x, y = window_size_info['width'], window_size_info['height']

        start_x = start_y = end_x = end_y = 0
        swipe_step, swipe_total_distance = 100, 2000
        if direction == 'up':
            start_x, start_y, end_x, end_y = x / 2, y / 2, x / 2, y / 3
            swipe_step, swipe_total_distance = y / 2 - y / 3, y * max_swipe_screen_count
        elif direction == 'down':
            start_x, start_y, end_x, end_y = x / 2, y / 3, x / 2, y * 5 / 6
            swipe_step, swipe_total_distance = y * 5 / 6 - y / 3, y * max_swipe_screen_count
        elif direction == 'left':
            start_x, start_y, end_x, end_y = x / 2, y / 2, x / 3, y / 2
            swipe_step, swipe_total_distance = x / 2 - x / 3, x * max_swipe_screen_count
        elif direction == 'right':
            start_x, start_y, end_x, end_y = x / 3, y / 2, x / 2, y / 2
            swipe_step, swipe_total_distance = x / 2 - x / 3, x * max_swipe_screen_count

        return start_x, start_y, end_x, end_y, swipe_step, swipe_total_distance

