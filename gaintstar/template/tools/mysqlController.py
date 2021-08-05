from typing import Dict

from pymysql import connect

from gaintstar.utils.logger import logger


class MysqlHandler:
    def __init__(self, database: Dict):
        if not database:
            raise ValueError(f"【数据库错误】请输入数据库链接信息")
        self.database = database

    def __enter__(self):
        self.conn = connect(**self.database)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()
