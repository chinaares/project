# -*- coding:utf-8 -*-
# 文件 ：mitmdump_server.py
# IED ：PyCharm
# 时间 ：2019/10/30 0030 16:37
# 版本 ：V1.0
"""
切换至脚本目录下运行脚本
mitmdump -s mitmdump_server.py
OSError: [WinError 87] 参数错误 : 把print注释掉
"""
import re
import os
import csv
import json
import sys
import logging
import datetime
from configparser import ConfigParser

PATH = os.getcwd()
FILE_NAME = f'{PATH}/config/{datetime.datetime.now().strftime("%Y-%m-%d")}.csv'


def response(flow):
    # 评论数据接口
    url_1 = 'https://api.twitter.com/2/timeline/conversation/'
    # 转推数据接口
    url_2 = 'https://api.twitter.com/2/timeline/retweeted_by.json?'
    # 个人主页接口
    url_3 = 'https://api.twitter.com/2/timeline/profile/'
    # 过滤接口和数据
    if flow.request.url.startswith(url_1) and flow.response.text:
        # print(f'*******************************')
        ID = re.findall(r'conversation/(.*?)\.json', flow.request.url)

        # 获取评论json数据
        text = flow.response.text
        # print(f'抓到的包：{text}')
        # 将已编码的json字符串解码为python对象
        content = json.loads(text)
        # 评论数据字典
        tweets = content['globalObjects']['tweets']
        # 写入配置文件
        status_id = tweets[ID[0]].get('quoted_status_id_str')
        status_id = status_id if status_id else '0'
        set_ini('Version', 'id', ID[0])
        set_ini('Version', 'quoted_id', status_id)
        # 获取评论数据字典的值
        for i in tweets:
            if red_ini('Version', 'id') == str(i) or str(i) == red_ini('Version', 'quoted_id'):
                print(f'重复数据跳过:{i}')
                # 转推数量
                retweet_count = tweets[i].get('retweet_count')
                # 点赞数量
                favorite_count = tweets[i].get('favorite_count')
                # 评论数量
                reply_count = tweets[i].get('reply_count')
                set_ini('Version', 'retweet_count', str(retweet_count))
                set_ini('Version', 'favorite_count', str(favorite_count))
                set_ini('Version', 'reply_count', str(reply_count))
                continue
            # 推特ID
            screen_name = tweets[i].get('entities')
            screen_name = screen_name['user_mentions'][0].get('screen_name') if 'user_mentions' in screen_name else ' '

            ID_url = f'https://mobile.twitter.com/{screen_name}/status/{ID[0]}'
            # 发布时间
            release_date = tweets[ID[0]].get('created_at').split(' ')
            release_date = f'{" ".join(release_date[:3])} {release_date[-1]}'

            created_at = tweets[i].get('created_at')  # 时间
            full_text = tweets[i].get('full_text')  # 内容
            full_text = str(full_text).replace('\n', '')
            # retweet_count = tweets[i].get('retweet_count')  # 回复数量
            # favorite_count = tweets[i].get('favorite_count')  # 转发信息
            # favorite_count = f'{ID[0]}转发数据.csv'  # 转发数据
            # reply_count = tweets[i].get('favorite_count')  # 点赞数
            # new_time = datetime.datetime.now()
            data = [[ID_url, release_date, full_text, created_at]]
            sav_data(data, ID[0])
            # print('成功写入一条数据!')

    # 过滤转推数据
    if flow.request.url.startswith(url_2) and flow.response.text:
        print(f'*************过滤转推数据******************')
        # 获取评论json数据
        text = flow.response.text
        # print(f'抓到的包：{text}')
        # 将已编码的json字符串解码为python对象
        content = json.loads(text)
        # 转推数据
        users = content['globalObjects']['users']
        with open(f'{PATH}/config/转推账户信息.txt', 'a+', encoding='utf-8') as f:
            for i in users:
                screen_name = users[i].get('screen_name')
                f.write(screen_name)
                f.write('\n')

    # 过滤个人信息数据 抓取转推时间
    if flow.request.url.startswith(url_3) and flow.response.text:
        print(f'************过滤个人信息数据*******************')
        # 获取评论json数据
        text = flow.response.text
        # print(f'抓到的包：{text}')
        # 将已编码的json字符串解码为python对象
        content = json.loads(text)
        tweets = content['globalObjects']['tweets']
        for i in tweets:
            # 被转推ID
            retweeted_status_id = tweets[i].get('retweeted_status_id_str')
            if red_ini('Version', 'id') != retweeted_status_id:
                print('跳过')
                continue
            # 转推者ID
            user_id = tweets[i].get('user_id_str')
            # 转推时间
            retweete_time = tweets[i].get('created_at')
            data = [[retweeted_status_id, user_id, retweete_time]]
            # 保存
            sav_retweete_time(data, retweeted_status_id)
            print('成功写入数据')
            # 被转推ID写入配置文件 效验是否已获取转推时间用
            set_ini('Version', 'retweete_time', retweeted_status_id)


def red_ini(section, name):
    """读取ini配置文件"""
    file = PATH + '\config\config.ini'  # 文件路径
    cp = ConfigParser()  # 实例化
    cp.read(file, encoding='utf-8')  # 读取文件
    val = cp.get(section, name)   # 读取数据
    return val


def set_ini(section, name, val):
    """读取、修改 ini配置文件"""
    file = PATH + '\config\config.ini'  # 文件路径
    cp = ConfigParser()  # 实例化
    cp.read(file, encoding='utf-8')  # 读取文件
    cp.set(section, name, val)  # 修改数据
    with open(file, 'w', encoding='utf-8') as f:
        cp.write(f)


def sav_data(data, name):
    """
    保存数据
    :return:
    """
    path = PATH + r'/数据/reply'  # 数据保存路径
    if not os.path.exists(path):
        os.mkdir(path)
    FILE_NAME = f'{path}/{name}.csv'
    with open(FILE_NAME, "a+", encoding='UTF-8', newline="") as f:
        k = csv.writer(f, delimiter=',')
        with open(FILE_NAME, "r", encoding='UTF-8', newline="") as f1:
            reader = csv.reader(f1)
            if not [row for row in reader]:
                k.writerow(
                    ['Twitter ID', 'date', 'reply', 'reply date'])
                k.writerows(data)
            else:
                k.writerows(data)


def sav_retweete_time(data, name):
    """
    保存数据
    :return:
    """
    path = PATH + r'/数据/retweet'  # 数据保存路径
    if not os.path.exists(path):
        os.mkdir(path)
    FILE_NAME = f'{path}/{name}.csv'
    with open(FILE_NAME, "a+", encoding='UTF-8', newline="") as f:
        k = csv.writer(f, delimiter=',')
        with open(FILE_NAME, "r", encoding='UTF-8', newline="") as f1:
            reader = csv.reader(f1)
            if not [row for row in reader]:
                k.writerow(
                    ['Twitter ID', '转推ID', '转推时间'])
                k.writerows(data)
            else:
                k.writerows(data)
