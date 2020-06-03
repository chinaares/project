# coding=utf-8
# 作者    ： Administrator
# 文件    ：sqlite3数据库操作.py
# IED    ：PyCharm
# 创建时间 ：2020/5/31 16:35


import sqlite3

# 连接数据库 没有则创建一个
xsgl = sqlite3.connect('xsgl.db')
cur = xsgl.cursor()
# 创建xsxx表
cur.execute('create table if not EXISTS xsxx(id integer primary key, name text, sex text, age integer, intake text)')

# 删除xsxx表中所有数据
# cur.execute('DELETE from xsxx')

# 查询数据
results = cur.execute('SELECT * FROM xsxx')
da = results.fetchall()
print(da)

# 修改数据
update_sql = 'update xsxx set age=age+1'
cur.execute(update_sql)
# 修改数据 把age=10 改成 age=12
update_sql = 'update xsxx set age = "12" where age = "10"'
cur.execute(update_sql)


# 数据写入
xsgl.commit()

# 关闭数据库连接
cur.close()
xsgl.close()