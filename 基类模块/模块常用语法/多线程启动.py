# coding=utf-8
# 作者    ： Administrator
# 文件    ：多线程启动.py
# IED    ：PyCharm
# 创建时间 ：2020/5/30 18:42
from multiprocessing import Pool


def run(i):
    print(i)


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
    main()