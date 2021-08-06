from setuptools import setup, find_packages
# pip uninstall giantstar
# python setup.py sdist bdist_wheel
# pip install E:\CTtest2\dist\giantstar-1.0.0-py3-none-any.whl
setup(
    name="giantstar",
    version="1.0.0",
    packages=find_packages(),
    package_data={
        'giantstar.sessionManage.webSession': ['webdrivers/**/*'],
        'giantstar.template': ['report/*', 'test_case/**', 'dataTable/*']
    },
    description='There is a toolbox for autotest',
    author="Ze Hua",
    author_email = '1737985326@qq.com',
    url='https://github.com/DaoSen-v/gaintstar',
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
            'giantstar = giantstar.cli:main',
            'gaintlocust = giantstar._locust:main_locust'
        ]
    }
)
