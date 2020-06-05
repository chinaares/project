# coding=utf-8
# 作者    ： Administrator
# 文件    ：Sqlite_Demo.py
# IED    ：PyCharm
# 创建时间 ：2020/6/3 19:19
import sqlite3


class DBTool(object):
    def __init__(self, filename="stsql"):
        """
        初始化数据库，默认文件名 stsql.db
        filename：文件名
        """
        # 创建数据库 不存在时在py同一目录下自动创建test.db
        self.filename = filename + ".db"
        self.conn = sqlite3.connect(self.filename)
        # 创建游标
        self.cursor = self.conn.cursor()
        # 创建表
        self.connect_db()

    def connect_db(self):
        """创建表 不存在则创建"""
        # 创建test表:判断表是否存在,存在则跳过,不存在创建
        # test_sql = "select count(*)  from sqlite_master where type='table' and name = 'test';"
        # test_cur = self.cursor.execute(test_sql)
        #
        # if not test_cur.fetchone()[0]:
        #     self.cursor.execute(
        #         """create table if not EXISTS test
        #           (id integer primary key,
        #           用户ID INT(50),
        #           用户姓名 CHAR(255))""")

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
                  裸车购买价 CHAR(255),
                  '油耗(百公里)' CHAR(255),
                  '目前行驶' CHAR(255),
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

    def close(self):
        """
        关闭数据库
        """
        self.conn.close()
        self.cursor.close()

    def execute(self, sql, param=None):
        """
        执行数据库的增、删、改
        sql：sql语句
        param：数据，可以是list或tuple，亦可是None
        retutn：成功返回True
        """
        try:
            if param is None:
                self.cursor.execute(sql)
            else:
                if type(param) is list:
                    self.cursor.executemany(sql, param)
                elif type(param) is tuple:
                    self.cursor.execute(sql, param)
                else:
                    print('数据类型错误')
                    return
            # 返回插入数据数量
            count = self.conn.total_changes
        except Exception as e:
            print(e)
            return False, e
        finally:
            # 提交事务
            self.conn.commit()
        if count > 0:
            return True
        else:
            return False

    def query(self, sql, param=None):
        """
        查询语句
        sql：sql语句
        param：参数,可为None
        retutn：成功返回True
        """
        if param is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, param)
        return self.cursor.fetchall()


if __name__ == '__main__':
    sql = """INSERT INTO koubei ('用户ID', '用户姓名', '车系ID', '车型ID', '品牌名称', '车系名称', '购买车型', '购买地点(省)', '购买地点(市)',
                                    '购车经销商', '购买时间', '裸车购买价', '油耗(百公里)', '目前行驶', '满意内容', '不满意内容', '空间(评分)', '空间内容',
                                    '动力(评分)', '动力内容', '操控(评分)', '操控内容', '油耗(评分)', '油耗内容', '舒适性(评分)', '舒适性内容',
                                    '外观(评分)', '外观内容', '内饰(评分)', '内饰内容', '性价比(评分)', '性价比内容', '购车目的') VALUES 
                                  (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    # data = 列表或者元祖
    data = None
    # 连接数据库
    db = DBTool()
    i = db.execute(sql, data)