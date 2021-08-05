import re
from typing import Text

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from gaintstar.utils.js import send_message
from gaintstar.utils.logger import logger
from gaintstar.assert_.publicAssert import AssertFactory


class WEBAssert(AssertFactory):
    @classmethod
    def ele_exits(cls, driver: WebDriver, attr, message):
        """

        :param driver:
        :param attr: location定位
        :return:
        """
        send_message(driver, f"【Assert元素存在】location={attr}")
        try:
            WebDriverWait(driver, 5, 0.5).until(ec.visibility_of_element_located(attr[0][0:2]))
            logger.info(f"【元素断言】期望元素存在, 断言成立")
            assert True
        except TimeoutException:
            logger.info(f"【元素断言】期望元素location={attr} 不存在, 断言不成立")
            raise AssertionError(f"【元素断言】期望元素location={attr} 不存在, 断言不成立=={message}==")

    @classmethod
    def title_exits(cls, driver: WebDriver, attr: str, message):
        send_message(driver, f"【Assert标题存在】location={attr}")
        title = driver.title
        attr = f"^{attr.replace('%', '.+')}$"
        result = re.findall(attr, title)
        assert result, message

    @classmethod
    def url_exits(cls, driver: WebDriver, attr: str, message):
        send_message(driver, f"【Assert URL存在】location={attr}")
        url = driver.current_url
        attr = f"^{attr.replace('%', '.+')}$"
        result = re.findall(attr, url)
        assert result, message
