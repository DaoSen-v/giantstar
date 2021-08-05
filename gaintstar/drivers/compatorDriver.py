# _*_encoding=utf8_*_
# @Time : 2021/6/30 11:22 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
from gaintstar.utils.logger import logger
from gaintstar.utils.dataParser import JsonParser

class CompatWEBDriver:
    driver = None
    video_url = None

    @classmethod
    def run(cls, *args, **kwargs):
        if cls.driver:
            cls.driver.quit()
        if cls.video_url:
            logger.info(f"【视频地址】{cls.video_url}")


class CompatAPPDriver:
    driver = None
    # video_url = None

    @classmethod
    def run(cls, *args, **kwargs):
        if cls.driver:
            cls.driver.quit()
        # if cls.video_url:
            # logger.info(f"【视频地址】{cls.video_url}")


class SetVariable:
    @classmethod
    def run(cls, data_set, uuid=None, owner_var_map=None, *args, **kwargs):
        param = data_set.get("request").get("test_data")
        param = JsonParser.analyze(param, uuid=uuid, owner_var_map=owner_var_map)
        JsonParser.add_variable(param, uuid=uuid)


# class SysDatabase:
#     @classmethod
#     def run(cls):