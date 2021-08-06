##### 1、安装
```dos
pip install gaintstar
```
##### 2、用例编写
- [目前已脚手架模板文件为主](doc/1、用例编写.md)
- [用例关联数据保存、使用](doc/2、关联数据保存、使用.md)
- [使用自定义函数参数化](doc/3、使用自定义函数参数化.md)
- [用例断言](doc/4、用例断言.md)

##### 3、项目配置说明

```python
CTTEST_SETTING = {
    "DEBUG": True,  # 调试模式开关、web ui用例生效，打开后会有定位元素高亮显示，浏览器右下角会弹出提示框
    "TEST_FILES": ['cttest_case.json'], # testCase文件夹下收集测试文件名
    "DATA_FILES": {"default": "./dataTable/data.xlsx"}  # 数据表文件获取表数据get_excel_data(index='sheet.id', use='default')
}
```
##### 4、新建项目：

```dos
gaintstart startproject {项目名}
```
##### 5、执行用例

1、通过执行run.py文件即可执行

2、通过manage.py + 命令参数执行（用于远程脚本执行，对接测试平台）

3、locustMange.py + 命令行参数 执行性能测试

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

 - GIANT_SETTING：giantstar内部逻辑控制，与响应的解析驱动配置