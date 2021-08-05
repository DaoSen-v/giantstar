##### 1、安装
```dos
pip install gaintstar
```
##### 2、用例编写
- 目前已脚手架模板文件为主
##### 3、项目配置说明

```python
CTTEST_SETTING = {
    "DEBUG": True,  # 调试模式开关、web ui用例生效
    "REMOTE": False,  # 是否远程执行，True：远程使用selenoid执行ui或者openstf执行ui用例 False：本地执行用例
    "TEST_FILES": ['cttest_case.json'], # testCase文件夹下收集测试文件名
    "DATA_FILES": {"default": "./dataTable/data.xlsx"}  # 数据表文件获取表数据get_excel_data(index='sheet.id', use='default')
}
```
##### 4、新建项目：
```dos
gaintstart startproject {项目名}
```
##### 5、本地执行用例
```python
# 执行run文件
```
##### 6、目录说明

dataTable：默认存放数据表

kword：存放关键字

report：报告文件

testCase：测试用例文件

- projectSetting.json运行测试用例的项目环境和全局账号设置
- cttest_XXX.json 测试用例文件

tool：工具文件

hookimpl：钩子函数调用

manage：shell命令入口

run：本地执行入口

setting：项目配置

 - CTTEST_SETTING：gaintstar内部逻辑控制，与响应的解析驱动配置