# -*- coding:utf-8 -*-
# 文件 ：DatabaseQuery.py
# IED ：PyCharm
# 时间 ：2020/6/4 0004 15:55
# 版本 ：V1.0
import os
from configparser import ConfigParser

from Sqlite_DB import DBTool

print(os.path.abspath(__file__))  # 当前文件绝对路径
PATH = os.getcwd()  # 文件路径


class DatabaseQuery(object):
    def __init__(self):
        self.db = DBTool()

    def red_ini(self):
        """读取ini配置文件"""
        file = PATH + '\config.ini'  # 文件路径
        cp = ConfigParser()  # 实例化
        cp.read(file, encoding='utf-8')  # 读取文件
        model = cp.get('Version', 'model')  # 读取数据
        return model.split(',')

    def run(self):
        models = self.red_ini()
        for model in models:
            sql = """SELECT * FROM "koubei" WHERE "eid" = "{0}";""".format(model)
            print(sql)
            contents = self.db.query(sql)
            if contents:
                print(f'没有查询到车系：{model}相关数据!')
                return False
            return True


if __name__ == '__main__':
    spider = DatabaseQuery()
    spider.run()