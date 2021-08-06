# 来源于HttpRunner
"""
Built-in validate comparators.
"""

import re
from typing import Text, Any, Union


def equal(check_value: Any, expect_value: Any, message: Text = "", desc=""):
    assert check_value == expect_value, message if message else f"{check_value} 等于 {expect_value} 不成立"


def greater_than(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = "", desc=""
):
    assert check_value > expect_value, message if message else f"{check_value} 大于 {expect_value} 不成立"


def less_than(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = "", desc=""
):
    assert check_value < expect_value, message if message else f"{check_value} 小于 {expect_value} 不成立"


def greater_or_equals(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = "", desc=""
):
    assert check_value >= expect_value, message if message else f"{check_value} 大于等于 {expect_value} 不成立"


def less_or_equals(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = "", desc=""
):
    assert check_value <= expect_value, message if message else f"{check_value} 小于等于 {expect_value} 不成立"


def not_equal(check_value: Any, expect_value: Any, message: Text = "", desc=""):
    assert check_value != expect_value, message if message else f"{check_value} 不等于 {expect_value} 不成立"


def string_equals(check_value: Text, expect_value: Any, message: Text = "", desc=""):
    assert str(check_value) == str(expect_value), message if message else f"{check_value} 字符串相等 {expect_value} 不成立"


def length_equal(check_value: Text, expect_value: int, message: Text = "", desc=""):
    assert isinstance(expect_value, int), "expect_value should be int type"
    assert len(check_value) == expect_value, message if message else f"{check_value} 长度等于 {expect_value} 不成立"


def length_greater_than(
    check_value: Text, expect_value: Union[int, float], message: Text = "", desc=""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) > expect_value, message if message else f"{check_value} 长度大于 {expect_value} 不成立"


def length_greater_or_equals(
    check_value: Text, expect_value: Union[int, float], message: Text = "", desc=""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) >= expect_value, message if message else f"{check_value} 长度大于等于 {expect_value} 不成立"


def length_less_than(
    check_value: Text, expect_value: Union[int, float], message: Text = "", desc=""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) < expect_value, message if message else f"{check_value} 长度小于 {expect_value} 不成立"


def length_less_or_equals(
    check_value: Text, expect_value: Union[int, float], message: Text = "", desc=""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) <= expect_value, message if message else f"{check_value} 长度小于等于 {expect_value} 不成立"


def contains(check_value: Any, expect_value: Any, message: Text = "", desc=""):
    # assert isinstance(
    #     check_value, (list, tuple, dict, str, bytes)
    # ), "expect_value should be list/tuple/dict/str/bytes type"
    check_value = str(check_value)
    assert expect_value in check_value, message if message else f"{check_value} 包含 {expect_value} 不成立"


def contained_by(check_value: Any, expect_value: Any, message: Text = "", desc=""):
    assert isinstance(
        check_value, (list, tuple, dict, str, bytes)
    ), "expect_value should be list/tuple/dict/str/bytes type"
    assert check_value in expect_value, message if message else f"{check_value} 被包含于 {expect_value} 不成立"


def type_match(check_value: Any, expect_value: Any, message: Text = "", desc=""):
    def get_type(name):
        if isinstance(name, type):
            return name
        elif isinstance(name, str):
            try:
                return __builtins__[name]
            except KeyError:
                raise ValueError(name)
        else:
            raise ValueError(name)

    if expect_value in ["None", "NoneType", None]:
        assert check_value is None, message if message else f"{check_value} in {expect_value} 不成立"
    else:
        assert type(check_value) == get_type(expect_value), message if message else f"{check_value} = {expect_value} 不成立"


def regex_match(check_value: Text, expect_value: Any, message: Text = "", desc=""):
    check_value = str(check_value)
    # assert isinstance(expect_value, str), "expect_value should be Text type"
    assert isinstance(check_value, str), "check_value should be Text type"
    assert re.match(expect_value, check_value), message if message else f"{check_value} 没有 {expect_value} 正则匹配内容"


def startswith(check_value: Any, expect_value: Any, message: Text = "", desc=""):
    assert str(check_value).startswith(str(expect_value)), message if message else f"{check_value} 以 {expect_value} 开头不成立"


def endswith(check_value: Text, expect_value: Any, message: Text = "", desc=""):
    assert str(check_value).endswith(str(expect_value)), message if message else f"{check_value} 以 {expect_value} 结尾不成立"


def old_contains(check_value: Text, expect_value: Any, message: Text = "", desc=""):
    if type(expect_value) in [list, dict]:
        assert expect_value in check_value
    else:
        assert str(expect_value) in str(check_value)


