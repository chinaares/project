# coding=utf-8
# 作者    ： Administrator
# 文件    ：Sqlite_Demo.py
# IED    ：PyCharm
# 创建时间 ：2020/6/3 19:19


import sqlite3


class DBTool(object):
    def __init__(self):
        """初始化函数，创建数据库连接"""

        # 创建数据库 不存在时在py同一目录下自动创建test.db
        self.conn = sqlite3.connect('test.db')
        # 创建游标
        self.cursor = self.conn.cursor()
        # 创建表
        self.connect_db()

    def connect_db(self):
        """创建表 不存在则创建"""
        # 创建koubei表:判断表是否存在,存在则跳过,不存在创建
        test_sql = "select count(*)  from sqlite_master where type='table' and name = 'koubei';"
        test_cur = self.cursor.execute(test_sql)

        if not test_cur.fetchone()[0]:
            self.cursor.execute(
                """create table if not EXISTS koubei
                  (id integer primary key, 
                  用户ID INT(50), 
                  用户姓名 CHAR(255), 
                  车系ID INT(50), 
                  车型ID INT(50),
                  品牌名称 CHAR(255),
                  车系名称 CHAR(255),
                  购买车型 CHAR(255),
                  '购买地点(省)' CHAR(255),
                  '购买地点(市)' CHAR(255),
                  购车经销商 CHAR(255),
                  购买时间 CHAR(255),
                  '油耗(百公里)' CHAR(255),
                  满意内容 text,
                  不满意内容 text,
                  '空间(评分)' INT(50),
                  空间内容 text,
                  '动力(评分)' INT(50),
                  动力内容 text,
                  '操控(评分)' INT(50),
                  操控内容 text,
                  '油耗(评分)' INT(50),
                  油耗内容 text,
                  '舒适性(评分)' INT(50),
                  舒适性内容 text,
                  '外观(评分)' INT(50),
                  外观内容 text,
                  '内饰(评分)' INT(50),
                  内饰内容 text,
                  '性价比(评分)' INT(50),
                  性价比内容 text,
                  购车目的 text
                  )""")
            print('koubei 表创建成功!')
        print(f'koubei 表读取成功!')

    def _update(self, sql, ob):
        """
        数据库的插入、修改函数
        :param sql: 传入的SQL语句
        :param ob: 传入数据
        :return: 返回操作数据库状态
        """
        try:
            self.cursor.execute(sql, ob)
            i = self.conn.total_changes  # 返回修改总行数
            print(f'修改总行数{i}')
        except Exception as e:
            print('错误类型： ', e)
            return False
        finally:
            self.conn.commit()
        if i > 0:
            return True
        else:
            return False

    def _delete(self, sql, ob):
        """
        操作数据库数据删除的函数
        :param sql: 传入的SQL语句
        :param ob: 传入数据
        :return: 返回操作数据库状态
        """
        try:
            self.c.execute(sql, ob)
            i = self.conn.total_changes
        except Exception as e:
            print(e)
            return False
        finally:
            self.conn.commit()
        if i > 0:
            return True
        else:
            return False

    def _query(self, sql, ob):
        """
        数据库数据查询
        :param sql: 传入的SQL语句
        :param ob: 传入数据
        :return: 返回操作数据库状态
        """
        test = self.c.execute(sql, ob)
        return test

    def _close(self):
        """
        关闭数据库相关连接的函数
        :return:
        """
        self.c.close()
        self.conn.close()


if __name__ == '__main__':
    db = DBTool()
    sql = '''INSERT INTO test (name,sex,age, intake)VALUES (?,?,?,?)'''
    da = ('xiaomi', 12, 'age', 'adf')
    db._update(sql, da)


