import re
import random
from datetime import timedelta

from django.utils.crypto import get_random_string
from django.utils.datetime_safe import datetime


def natural_sort_key(s, _nsre=re.compile(r"(\d+)")):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def rand_str(length=32, type="lower_hex"):
    """
    生成指定长度的随机字符串或者数字, 可以用于密钥等安全场景
    :param length: 字符串或者数字的长度
    :param type: str 代表随机字符串，num 代表随机数字
    :return: 字符串
    """
    if type == "str":
        return get_random_string(length, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_str":
        return get_random_string(length, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789")
    elif type == "lower_hex":
        return random.choice("123456789abcdef") + get_random_string(length - 1, allowed_chars="0123456789abcdef")
    else:
        return random.choice("123456789") + get_random_string(length - 1, allowed_chars="0123456789")


def submission_aggregate(submissions, now, offset):
    date_list = [{'date': str((now - timedelta(days=i)).date()), 'ac': 0, 'submit': 0, 'rate': 0.0} for i in
                 range(offset, 0, -1)]

    for submission in submissions:
        off = (now - submission['create_time']).days
        date_list[-(off + 1)]['submit'] += 1

        if submission['result'] == 0:
            date_list[-(off + 1)]['ac'] += 1

    for date in date_list:
        if date['submit'] == 0:
            continue
        date['rate'] = date['ac'] / date['submit']
    return date_list
