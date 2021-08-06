# _*_encoding=utf8_*_
# @Time : 2021/6/10 16:07 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import json
from typing import List

import pymysql
import pandas
from giantstar.globalSetting import plus_setting
from giantstar.utils.error import DatabaseNoSuchData, DataIndexError


class ExcelReader:
    files = plus_setting.DATA_FILES

    @classmethod
    def get_excel_data(cls, index: str, use:str ='default', index_col="dataid"):
        sheet, _id = cls.refresh_index(index)
        df = pandas.read_excel(cls.files.get(use), sheet_name=sheet, index_col=index_col, keep_default_na=False)
        data = df.loc[_id].to_dict()
        if isinstance(data["host"], dict):
            raise DataIndexError(f"【数据索引】data index error，index must be unique. but get many index result")

        for k, v in data.items():
            if k in ["headers", "request", "assert", "extract"]:
                data[k] = json.loads(v) if v else {}
        return data

    @classmethod
    def refresh_index(cls, index):
        index_list:List = index.split('.')
        if len(index_list) == 2:
            return index_list
        raise DataIndexError(f"【数据索引】data index error，expect get 'a.b', but get '{index}'.")


class MysqlReader:
    database_config = plus_setting.DATABASE
    @classmethod
    def get_mysql_data(cls,sql, use='default'):
        """
        获取数据库一行数据
        :param use: 使用数据库配置名
        :param sql: 执行的sql语句
        :return: dict
        """
        connect = pymysql.connect(**cls.database_config.get(use))
        cursor = connect.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(sql)
        res = cursor.fetchone()
        cursor.close()
        connect.close()
        if res: return res
        raise DatabaseNoSuchData(f"【数据查询错误】数据库不存在该条数据, sql={sql}")


class YamlReader:
    pass
