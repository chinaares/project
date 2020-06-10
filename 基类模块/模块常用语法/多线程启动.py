# coding=utf-8
# 作者    ： Administrator
# 文件    ：多线程启动.py
# IED    ：PyCharm
# 创建时间 ：2020/5/30 18:42
import threading
from multiprocessing import Pool


def run(i):
    print(f'{i} 这是函数内')


def main():
    """程序入口"""
    # 启动10个线程
    pool = Pool(10)
    for i in range(100):
        # 启动线程
        pool.apply_async(run, (i,))

    pool.close()
    pool.join()


if __name__ == '__main__':

    t_list = []
    for i in range(10):
        print(i)
        t = threading.Thread(target=run, args=(i,))
        t_list.append(t)

    # 启动线程
    for t in t_list:
        t.start()

    # 等待所有线程结束
    for t in t_list:
        t.join()