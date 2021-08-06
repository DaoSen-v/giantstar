from typing import Text

from gaintstar.assert_ import comparetors

from gaintstar.utils.dataParser import GlobalVariableMap
from gaintstar.utils.error import AssertNotSupport


def get_uniform_comparator(comparator: Text):
    """ convert comparator alias to uniform name
    """
    if comparator in ["eq", "equals", "equal"]:
        return "equal"
    elif comparator in ["lt", "less_than"]:
        return "less_than"
    elif comparator in ["le", "less_or_equals"]:
        return "less_or_equals"
    elif comparator in ["gt", "greater_than"]:
        return "greater_than"
    elif comparator in ["ge", "greater_or_equals"]:
        return "greater_or_equals"
    elif comparator in ["ne", "not_equal"]:
        return "not_equal"
    elif comparator in ["str_eq", "string_equals"]:
        return "string_equals"
    elif comparator in ["len_eq", "length_equal"]:
        return "length_equal"
    elif comparator in ["len_gt", "length_greater_than"]:
        return "length_greater_than"
    elif comparator in ["len_ge", "length_greater_or_equals"]:
        return "length_greater_or_equals"
    elif comparator in ["len_lt", "length_less_than"]:
        return "length_less_than"
    elif comparator in ["len_le","length_less_or_equals"]:
        return "length_less_or_equals"
    elif comparator in ["reg"]:
        return "regex_match"
    elif comparator in ["in", "contains"]:
        return "contains"
    else:
        return comparator


class AssertFactory:
    def validate(self, comparator, check_value, expect_value, message:Text=""):
        assert_method = get_uniform_comparator(comparator)
        return getattr(self, assert_method)(check_value, expect_value, message)

    def __getattr__(self, item):
        if hasattr(comparetors, item):
            return getattr(comparetors, item)  # 返回系统内部的函数断言逻辑
        elif GlobalVariableMap.func_map.get("item"):
            return GlobalVariableMap.func_map.get("item")
        else:
            raise AssertNotSupport("【断言错误】断言方法中不存在：%s, 请查阅官方文档，或自定义方法中是否存在该断言" % item)
