# _*_encoding=utf8_*_
# @Time : 2021/6/16 15:18 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
from miracle import get_model, get_data
from tool.step import Step


class TestCase(Step):

    def test_03(self):
        self.step(
            'api',
            data_set=get_data('Sheet1.a1', source='excel'),
            model_set={'method': "get", "path": "/api", "req_body_type": "json"}
        )
        self.step('api', data_set=get_data('Sheet1.a2', source='excel'), model_set=get_model(123))
        self.step('web', data_set={})
        self.step('app', data_set={})