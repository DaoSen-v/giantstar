from setuptools import setup, find_packages
# pip uninstall gaintstar
# python setup.py sdist bdist_wheel
# pip install E:\CTtest2\dist\gaintstar-1.0.0-py3-none-any.whl
setup(
    name="gaintstar",
    version="1.0.0",
    packages=find_packages(),
    package_data={
        'gaintstar.sessionManage.webSession': ['webdrivers/**/*'],
        'gaintstar.template': ['report/*', 'test_case/**', 'dataTable/*']
    },
    description='There is a toolbox for autotest',
    author="Ze Hua",
    author_email = '1737985326@qq.com',
    url='https://gitlab.casstime.net/qa/TestArchitecture/cttest2',
    license='MIT',
    zip_safe = False,
    install_requires = [
        "requests",
        "har2case",
        "openpyxl",
        "pyyaml",
        'selenium',
        'pytest',
        'allure-pytest',
        'pymysql',
        # 'paramiko',
        'faker',
        'jmespath',
        'Appium-Python-Client',
        'lxml',
        # 'sshtunnel',
        'pytest-rerunfailures',
        'parsel',
        'locust',
        'loguru',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'gaintstar = gaintstar.cli:main',
            'gaintlocust = gaintstar._locust:main_locust'
        ]
    }
)
