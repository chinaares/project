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
from configparser import ConfigParser
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
        # st=0:缩略，1：满意，2：不满意，3：空间，4：动力，5：操控，6：油耗，7：舒适性，8：外观，9：内饰，10：性价比，11：满意度
        # 12：电耗，13：店铺环境，17：能耗，18：
        self.SeriesUrl = 'https://koubei.app.autohome.com.cn/autov9.1.0/alibi/seriesalibiinfos-pm2-ss3170-st0-p1-s50-isstruct0-o0.json'
        # 口碑详细数据接口 eid=3052096 口碑详情页ID， self.SeriesUrl接口返回
        self.NewEvaluationUrl = 'https://koubeiipv6.app.autohome.com.cn/autov9.13.0/alibi/NewEvaluationInfo.ashx?eid='
        # 评论
        'https://koubeiipv6.app.autohome.com.cn/autov9.13.0/news/koubeicomments.ashx?pm=2&koubeiid=1936376&pagesize=20&lastid=0&hot=0'
        # 数据
        self.content = dict()

    def red_ini(self):
        """读取ini配置文件"""
        file = PATH + '\config.ini'  # 文件路径
        cp = ConfigParser()  # 实例化
        cp.read(file, encoding='utf-8')  # 读取文件
        model = cp.get('Version', 'model')  # 读取数据
        return model

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

    def get_eid(self, car):
        """获取车型口碑ID列表"""
        log_init().info(f'车系：{car} 口碑数据获取中...')
        p = 1
        while True:
            # 解析口碑ID
            url = f'https://koubei.app.autohome.com.cn/autov9.1.0/alibi/seriesalibiinfos-pm2-ss{car}-st0-p{p}-s50-isstruct0-o0.json'
            try:
                response = self._parse_url(url).json()
            except:
                log_init().info(f'{url} 口碑数据解析失败!')
                return
            koubeiids = response.get('result').get('list')
            if not koubeiids:
                log_init().info(f'车系：{car}车型口碑ID列表获取完成。')
                return

            for koubeiid in koubeiids:
                self.content[koubeiid['Koubeiid']] = {}

            # 解析口碑详细数据
            for st in range(1, 11):
                url = f'https://koubei.app.autohome.com.cn/autov9.1.0/alibi/seriesalibiinfos-pm2-ss{car}-st{st}-p{p}-s50-isstruct0-o0.json'

                response = self._parse_url(url).json()
                results = response.get('result').get('list')
                for result in results:
                    self.content[result['Koubeiid']][result['contents'][0]['structuredname']] = result['contents'][0]['content']

            for eid in self.content.keys():
                yield eid
            p += 1

    def get_content(self, model, eid):
        """解析口碑详情数据"""
        url = f'{self.NewEvaluationUrl}{eid}'
        log_init().info(f'车系：{model} 口碑：{eid} 数据获取中...')
        response = self._parse_url(url).json()
        result = response.get('result')
        if not result:
            log_init().info(f'{eid}无数据!')
            return
        specid = result.get('specid')  # 车型ID
        userId = result.get('userId')  # 用户ID
        userName = result.get('userName')  # 用户姓名
        specname = result.get('specname')  # 购买车型
        boughtprovincename = result.get('boughtprovincename')  # 购买地点(省)
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
        boughtcityname = result.get('boughtcityname')  # 购买地点(市)

        satisfaction_content = self.content[eid]['满意']  # 满意内容
        Dissatisfied_content = self.content[eid]['不满意']  # 不满意内容
        space_content = self.content[eid]['空间']  # 空间内容
        power_content = self.content[eid]['动力']  # 动力内容
        Control_content = self.content[eid]['操控']  # 操控内容
        oilScene_content = self.content[eid]['油耗']  # 油耗内容
        Comfort_content = self.content[eid]['舒适性']  # 舒适性内容
        Exterior_content = self.content[eid]['外观']  # 外观内容
        Interior_content = self.content[eid]['内饰']  # 内饰内容
        Costeffective_content = self.content[eid]['性价比']  # 性价比内容

        data = [[userId, userName, model, specid, brandname, seriesname, specname, boughtprovincename, boughtcityname,
                 dealername, boughtdate, boughtPrice, actualOilConsumption, drivekilometer, satisfaction_content,
                 Dissatisfied_content, spaceScene, space_content, powerScene, power_content, maneuverabilityScene,
                 Control_content, oilScene, oilScene_content, comfortablenessScene, Comfort_content, apperanceScene,
                 Exterior_content, internalScene, Interior_content,
                 costefficientScene, Costeffective_content, purpose]]
        return data

    def keep_records(self, eid, vali=False):
        """保存获取记录"""
        file_name = '获取记录.txt'
        if not os.path.exists(file_name):
            fi = open(file_name, 'a')
            fi.close()
        if vali:
            with open(file_name, 'r') as f:
                flight = [i.replace('\n', '') for i in f.readlines()]
                if str(eid) in flight:
                    return True
                return False
        else:
            with open(file_name, 'a+') as f:
                f.write(str(eid))
                f.write('\n')

    def scv_data(self, data):
        """保存数据"""
        with open("口碑数据.csv", "a+", encoding='utf-8', newline="") as f:
            k = csv.writer(f, delimiter=',')
            with open("口碑数据.csv", "r", encoding='utf-8', newline="") as f1:
                reader = csv.reader(f1)
                if not [row for row in reader]:
                    k.writerow(['用户ID', '用户姓名', '车系ID', '车型ID', '品牌名称', '车系名称', '购买车型', '购买地点(省)', '购买地点(市)',
                                '购车经销商', '购买时间', '裸车购买价', '油耗(百公里)', '目前行驶', '满意内容', '不满意内容', '空间(评分)', '空间内容',
                                '动力(评分)', '动力内容', '操控(评分)', '操控内容', '油耗(评分)', '油耗内容', '舒适性(评分)', '舒适性内容',
                                '外观(评分)', '外观内容', '内饰(评分)', '内饰内容', '性价比(评分)', '性价比内容', '购车目的'])
                    k.writerows(data)
                else:
                    k.writerows(data)

    def run(self, model, eid):
        # 判断是否获取
        if self.keep_records(eid, vali=True):
            log_init().info(f'{eid} 已获取跳过!')
            return

        # 第三步 获取口碑详情数据
        data = self.get_content(model, eid)
        # 第四步 保存数据
        self.scv_data(data)
        log_init().info(f'车系：{model} 口碑：{eid} 数据保存成功!')
        # 保存获取记录
        self.keep_records(eid)
        time.sleep(1)

    @run_time
    def main(self, num):
        """程序入口"""
        # 多线程启动
        pool = Pool(num)
        # 第一步 读取车型ID
        model = self.red_ini()
        # 第二步 获取口碑eid
        for eid in self.get_eid(model):
            # 启动线程
            pool.apply_async(self.run, (model, eid,))

        pool.close()
        pool.join()
        log_init().info(f'车系：{model} 口碑数据获取完成!')


if __name__ == '__main__':
    spider = Spider()
    spider.main(10)
    # spider.get_eid(4502)

