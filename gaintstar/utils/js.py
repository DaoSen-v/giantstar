# _*_encoding=utf8_*_
# @Time : 2021/5/22 10:59 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import time

from selenium.common.exceptions import JavascriptException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from gaintstar.globalSetting import plus_setting
from gaintstar.utils.initTest import _Config
message_box_css ="""
.cttest {
    width: 360px;
    position: absolute;
    right: 20px;
    bottom: 20px;
    padding: 25px 15px;
    text-align: left;
    border-radius: 5px;
    background-color: rgba(162, 250, 84, 0.65);
    border: 1px solid #f6db7b;
    z-index: 999;
}
"""

message_box_func = """function sendMessage(message) {
var style = document.createElement('style');
style.type = 'text/css';
style.innerHTML = '%s';
document.getElementsByTagName('head')[0].appendChild(style);
var newDiv = document.createElement('div');
newDiv.className = 'cttest';
var t = document.createTextNode(message);
newDiv.appendChild(t);
document.body.appendChild(newDiv);
setTimeout(function(){newDiv.remove()}, 2000)
}""" % message_box_css.replace('\n',' ').strip()

inject_js = """
var body = document.getElementsByTagName('body')[0];
var script = document.createElement('script');
script.type='text/javascript';
script.innerHTML= "%s";
body.appendChild(script);
""" % message_box_func.replace('\n',' ').strip()


def add_message_box(driver: WebDriver):
    driver.execute_script(inject_js)


def send_message(driver: WebDriver, message:str):
    if plus_setting.DEBUG:
        try:
            driver.execute_script('sendMessage("%s")' % message)
        except JavascriptException:
            driver.execute_script('window.onload')
            add_message_box(driver)
            driver.execute_script('sendMessage("%s")' % message)

def highlight_with_element(driver: WebDriver, ele: WebElement):
    if plus_setting.DEBUG:
        driver.execute_script("""arguments[0].style.boxShadow = '0px 0px 6px 6px rgba(255, 55, 169, 0.5)';""", ele)
        time.sleep(1)
        driver.execute_script("arguments[0].style.boxShadow = '0px 0px 0px 0px rgba(0, 0, 0)';", ele)

# if __name__ == '__main__':
#     from selenium import webdriver
#     f = webdriver.Firefox()
#     f.get('https://www.baidu.com')
#     time.sleep(2)
#     f.execute_script(inject_js)
#     f.execute_script('sendMessage("woshixiaoxi")')
