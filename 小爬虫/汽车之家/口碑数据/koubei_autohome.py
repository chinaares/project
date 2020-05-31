# -*- coding:utf-8 -*-
# 文件 ：全系车型参数(包含历史车型).py
# IED ：PyCharm
# 时间 ：2019/12/13 0013 14:48
# 版本 ：V1.0
import os
import csv
import sys
import time
import json
import logging
import datetime
import requests
from retrying import retry
from multiprocessing import Pool
from fake_useragent import UserAgent


print(os.path.abspath(__file__))  # 当前文件绝对路径
PATH = os.getcwd()  # 文件路径


def run_time(func):
    def new_func(*args, **kwargs):
        start_time = datetime.datetime.now()
        log_init().info("程序开始时间：{}".format(start_time))
        res = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        log_init().info("程序结束时间：{}".format(end_time))
        log_init().info("程序执行用时：{}s".format((end_time - start_time)))
        return res

    return new_func


def log_init():
    # 创建一个日志器
    program = os.path.basename(sys.argv[0])  # 获取程序名
    logger = logging.getLogger(program)
    # 判断handler是否有值,(避免出现重复添加的问题)
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s | %(name)-3s | %(levelname)-6s| %(message)s')  # 设置日志输出格式
        logger.setLevel(logging.DEBUG)

        # 输出日志至屏幕
        console = logging.StreamHandler()  # 设置日志信息输出至屏幕
        console.setLevel(level=logging.DEBUG)  # 设置日志器输出级别，包括debug < info< warning< error< critical
        console.setFormatter(formatter)  # 设置日志输出格式

        # 输出日志至文件
        path = PATH + r'/log/'  # 日志保存路径
        if not os.path.exists(path):
            os.mkdir(path)
        filename = path + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
        fh = logging.FileHandler(filename, encoding='utf-8', mode='a+')  # 设置日志信息保存至文件
        # fh.setLevel(logging.DEBUG)  # 设置日志器输出级别
        fh.setFormatter(formatter)  # 设置日志输出格式
        logger.addHandler(fh)
        logger.addHandler(console)

    return logger


class Spider:
    def __init__(self):
        # 口碑数据接口 ss:车系ID, p:页数, s:一页返回数据个数最多50
        self.SeriesUrl = 'https://koubei.app.autohome.com.cn/autov9.1.0/alibi/seriesalibiinfos-pm2-ss3170-st0-p112-s50-isstruct0-o0.json'
        # 口碑详细数据接口 eid=3052096 口碑详情页ID， self.SeriesUrl接口返回
        self.NewEvaluationUrl = 'https://koubeiipv6.app.autohome.com.cn/autov9.13.0/alibi/NewEvaluationInfo.ashx?eid='

    @retry(stop_max_attempt_number=30)
    def _parse_url(self, url):
        """url请求"""
        headers = {"User-Agent": UserAgent().random}
        while True:
            try:
                # allow_redirects关闭页面跳转
                response = requests.get(url, headers=headers, allow_redirects=False, timeout=300)
            except Exception as e:
                log_init().info(e)
                continue
            return response

    def get_model(self):
        """获取所有车型数据"""
        # 所有车型js文件
        url = 'https://car.autohome.com.cn/javascript/NewSpecCompare.js?20131010'
        response = self._parse_url(url)
        content = response.content.decode('GBK')  # GBK解码
        # 剔除开头和结尾处多余字符 转换为json
        content = content.replace('var listCompare$100= ', '').replace(';', '')
        content = json.loads(content)
        # print(content)
        for i in content:
            for q in i['List']:
                # 车系ID
                for L in q['List']:
                    yield L['I']

    def get_eid(self, car):
        """获取车型口碑ID列表"""
        log_init().info(f'车系：{car} 口碑数据获取中...')
        p = 1
        while True:
            url = f'https://koubei.app.autohome.com.cn/autov9.1.0/alibi/seriesalibiinfos-pm2-ss{car}-st0-p{p}-s50-isstruct0-o0.json'
            try:
                response = self._parse_url(url).json()
            except:
                return
            koubeis = response.get('result').get('list')
            if not koubeis:
                log_init().info(f'车系：{car}车型口碑ID列表获取完成。')
                return
            eids = [i['Koubeiid'] for i in koubeis]
            for eid in eids:
                yield eid
            p += 1

    def get_content(self, cars, eid):
        """解析口碑详情数据"""
        url = f'{self.NewEvaluationUrl}{eid}'
        log_init().info(f'车系：{cars} 口碑：{eid} 数据获取中...')
        response = self._parse_url(url).json()
        result = response.get('result')
        if not result:
            log_init().info(f'{eid}无数据!')
            return
        specid = result.get('specid')  # 车型ID
        userId = result.get('userId')  # 用户ID
        userName = result.get('userName')  # 用户姓名
        specname = result.get('specname')  # 购买车型
        boughtprovincename = result.get('boughtprovincename')  # 购买地点
        dealername = result.get('dealername')  # 购买经销商
        boughtdate = result.get('boughtdate')  # 购买时间
        boughtPrice = result.get('boughtPrice')  # 裸车购买价
        actualOilConsumption = result.get('actualOilConsumption')  # 油耗
        drivekilometer = result.get('drivekilometer')  # 目前行驶
        spaceScene = result.get('spaceScene').get('score')  # 空间
        powerScene = result.get('powerScene').get('score')  # 动力
        maneuverabilityScene = result.get('maneuverabilityScene').get('score')  # 操控
        oilScene = result.get('oilScene').get('score')  # 油耗
        comfortablenessScene = result.get('comfortablenessScene').get('score')  # 舒适性
        apperanceScene = result.get('apperanceScene').get('score')  # 外观
        internalScene = result.get('internalScene').get('score')  # 内饰
        costefficientScene = result.get('costefficientScene').get('score')  # 性价比
        purpose = ','.join([i['purposename'] for i in result.get('purpose')])  # 购车目的

        brandname = result.get('brandname')  # 品牌名称
        seriesname = result.get('seriesname')  # 车系名称
        boughtcityname = result.get('boughtcityname')  # 车系名称

        data = [[userId, userName, cars, specid, brandname, seriesname, specname, boughtprovincename, boughtcityname, dealername,
                 boughtdate, boughtPrice, actualOilConsumption, drivekilometer, spaceScene, powerScene,
                 maneuverabilityScene, oilScene, comfortablenessScene, apperanceScene, internalScene,
                 costefficientScene, purpose]]
        return data

    def keep_records(self, car, vali=False):
        """保存获取记录"""
        file_name = '获取记录.txt'
        if not os.path.exists(file_name):
            fi = open(file_name, 'a')
            fi.close()
        if vali:
            with open(file_name, 'r') as f:
                flight = [i.replace('\n', '') for i in f.readlines()]
                if str(car) in flight:
                    return True
                return False
        else:
            with open(file_name, 'a+') as f:
                f.write(str(car))
                f.write('\n')

    def scv_data(self, data):
        """保存数据"""
        with open("口碑数据.csv", "a+", encoding='utf-8', newline="") as f:
            k = csv.writer(f, delimiter=',')
            with open("口碑数据.csv", "r", encoding='utf-8', newline="") as f1:
                reader = csv.reader(f1)
                if not [row for row in reader]:
                    k.writerow(['用户ID', '用户姓名', '车系ID', '车型ID', '品牌名称', '车系名称', '购买车型', '购买地点', '购买地点',
                                '购车经销商', '购买时间', '裸车购买价', '油耗', '目前行驶', '空间', '动力', '操控', '油耗', '舒适性',
                                '外观', '内饰', '性价比', '购车目的'])
                    k.writerows(data)
                else:
                    k.writerows(data)

    def run(self, car):
        # 判断是否获取
        if self.keep_records(car, vali=True):
            log_init().info(f'{car} 已获取跳过!')
            return
        # 第二步 获取口碑eid
        for eid in self.get_eid(car):
            # 第三步 获取口碑详情数据
            data = self.get_content(car, eid)
            # 第四步 保存数据
            self.scv_data(data)
            log_init().info(f'车系：{car} 口碑：{eid} 数据保存成功!')
            time.sleep(1)
        log_init().info(f'车系：{car} 口碑数据获取完成!')
        # 保存获取记录
        self.keep_records(str(car))
        log_init().info(f'车系：{car} 获取记录保存成功!')

    @run_time
    def main(self, num):
        """程序入口"""
        # 多线程启动
        pool = Pool(num)
        for car in self.get_model():
            # 启动线程
            pool.apply_async(self.run, (car,))

        pool.close()
        pool.join()


if __name__ == '__main__':
    spider = Spider()
    spider.main(20)

