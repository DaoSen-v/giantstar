import requests

from gaintstar.globalSetting import plus_setting


def build_file(url, filename):
    BASE_DIR = plus_setting.BASE_DIR
    response = requests.get(url)
    test_dir = BASE_DIR + '/test_case/' + filename
    with open(test_dir, mode='wb+') as f:
        f.write(response.content)