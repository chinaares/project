# -*- coding:utf-8 -*-
# 文件 ：TwitterComment.py
# IED ：PyCharm
# 时间 ：2020/4/16 0016 16:19
# 版本 ：V1.0
import os
import socket
import sys
import csv
import time
import logging
import datetime
from configparser import ConfigParser
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

print(os.path.abspath(__file__))  # 当前文件绝对路径
PATH = os.getcwd()  # 文件路径


def run_time(func):
    def new_func(*args, **kwargs):
        start_time = datetime.datetime.now()
        log_init().info("Program start time：{}".format(start_time))
        res = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        log_init().info("Program end time：{}".format(end_time))
        log_init().info("Program execution time：{}s".format((end_time - start_time)))
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
        path = PATH + r'/logs/'  # 日志保存路径
        if not os.path.exists(path):
            os.mkdir(path)
        filename = path + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
        fh = logging.FileHandler(filename, encoding='utf-8', mode='a+')  # 设置日志信息保存至文件
        # fh.setLevel(logging.DEBUG)  # 设置日志器输出级别
        fh.setFormatter(formatter)  # 设置日志输出格式
        logger.addHandler(fh)
        logger.addHandler(console)

    return logger


class Twitter:
    def __init__(self):
        log_init().info('Program start')
        log_init().info('chrome start')

        # 开启mitmdump
        self.monitor = Monitor()
        self.monitor.run()

        # 创建数据保存目录
        os.mkdir(PATH + r'/数据')

        options = Options()
        # 使用无头模式
        # options.add_argument('headless')
        # options.add_argument('--disable-gpu')
        desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
        desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出
        prefs = {"profile.managed_default_content_settings.images": 1}  # 1 加载图片 2不加载图片,加快访问速度
        options.add_experimental_option("prefs", prefs)
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(chrome_options=options, desired_capabilities=desired_capabilities)

        self.wait = WebDriverWait(self.driver, 10, 1)  # 设置隐式等待时间
        self.driver.maximize_window()  # 窗口最大化
        log_init().info('chrome initialized successfully')

    def login(self):
        """登录账号"""
        self.driver.get('https://twitter.com/login')
        input('登录账号：登录成功后按ENTER继续运行')
        if 'twitter.com/login' not in self.driver.current_url:
            log_init().info("登录成功")
        else:
            # log_init().info("等待扫码中...")
            # time.sleep(5)
            log_init().info("登录失败")

    def red_ini(self, section, name):
        """读取ini配置文件"""
        file = PATH + '\config\config.ini'  # 文件路径
        cp = ConfigParser()  # 实例化
        cp.read(file, encoding='utf-8')  # 读取文件
        val = cp.get(section, name)  # 读取数据
        return val

    def set_ini(self, section, name, val):
        """读取、修改 ini配置文件"""
        file = PATH + '\config\config.ini'  # 文件路径
        cp = ConfigParser()  # 实例化
        cp.read(file, encoding='utf-8')  # 读取文件
        cp.set(section, name, val)  # 修改数据
        with open(file, 'w', encoding='utf-8') as f:
            cp.write(f)

    def red_csv(self):
        """读取配置文件"""
        file = f'{PATH}/config/输入文件.csv'
        with open(file, 'r', encoding='UTF-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                row = [i for i in row if str(i).replace(' ', '')]
                yield row

    def keep_records(self, model_id, vali=False):
        """保存获取记录"""
        file_name = f'{PATH}/config/valida.txt'
        if not os.path.exists(file_name):
            fi = open(file_name, 'a')
            fi.close()
        if vali:
            with open(file_name, 'r') as f:
                flight = [i.replace('\n', '') for i in f.readlines()]
                if model_id in flight:
                    return True
                return False
        else:
            with open(file_name, 'a+') as f:
                f.write(model_id)
                f.write('\n')

    def get_basic(self, url):
        """获取评论数据"""
        count = 0
        self.driver.get(url)
        time.sleep(5)
        while True:
            log_init().info('Data acquisition...')
            if count > 5:
                return
            Height = self.driver.execute_script("return document.body.scrollHeight;")
            # 获取body的高度，滑到底部
            scroll = "window.scrollTo(0,document.body.scrollHeight)"
            self.driver.execute_script(scroll)
            time.sleep(2)
            # 判断是否到达底部
            page_source = self.driver.page_source
            if '显示更多回复' in page_source or 'Show more replies' in page_source:
                more = self.driver.find_elements_by_xpath(
                    '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div/span')
                if not more:
                    return
                more[0].click()
                time.sleep(3)
            new_Height = self.driver.execute_script("return document.body.scrollHeight;")
            if new_Height == Height:
                count += 1
            else:
                count = 0
            # print(count)

    def retweeted_status(self, url):
        """获取转推日期数据"""
        url = f'{url}/retweets'
        self.driver.get(url)
        log_init().info('转推用户信息数据加载中')
        while True:
            if self.driver.find_elements_by_xpath('//*[@aria-label="时间线：转推者"]'):
                break
            if self.driver.find_elements_by_xpath(
                    '//*[@id="react-root"]/div/div/div[1]/div[2]/div/div/div/div[2]/div[2]/div/div[2]/div/div/div/div/span'):
                break

        # 是否有转推信息
        with open(f'{PATH}/config/转推账户信息.txt', 'r', encoding='utf-8') as f:
            retweeted = [i.replace('\n', '') for i in f.readlines()]
            log_init().info(retweeted)
            if not retweeted:
                return
        for retw in retweeted:
            self.driver.get(f'https://twitter.com/{retw}')
            log_init().info(f'开始获取：https://twitter.com/{retw}')
            count = 0
            while True:
                log_init().info('数据匹配中...')
                if count > 10:
                    log_init().info(f'https://twitter.com/{retw} 没有匹配到转推信息')
                    break
                if self.red_ini('Version', 'id') == self.red_ini('Version', 'retweete_time'):
                    log_init().info(f'https://twitter.com/{retw} 成功抓取转推时间！')
                    break
                Height = self.driver.execute_script("return document.body.scrollHeight;")
                # 获取body的高度，滑到底部
                scroll = "window.scrollTo(0,document.body.scrollHeight)"
                self.driver.execute_script(scroll)
                time.sleep(2)
                # 判断是否到达底部
                page_source = self.driver.page_source
                if '显示更多回复' in page_source or 'Show more replies' in page_source:
                    more = self.driver.find_elements_by_xpath(
                        '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div/span')
                    if not more:
                        break
                    more[0].click()
                    time.sleep(3)
                new_Height = self.driver.execute_script("return document.body.scrollHeight;")
                if new_Height == Height:
                    count += 1
                else:
                    count = 0
            # 修改配置文件
            self.set_ini('Version', 'retweete_time', '0')
        # 删除转推账户信息
        os.remove('config/转推账户信息.txt')

    def save_csv(self, data):
        """
        保存数据
        :return:
        """
        path = PATH + r'/数据'  # 数据保存路径
        if not os.path.exists(path):
            os.mkdir(path)
        FILE_NAME = f'{path}/twitter.csv'
        with open(FILE_NAME, "a+", encoding='UTF-8', newline="") as f:
            k = csv.writer(f, delimiter=',')
            with open(FILE_NAME, "r", encoding='UTF-8', newline="") as f1:
                reader = csv.reader(f1)
                if not [row for row in reader]:
                    k.writerow(
                        ['No.', 'label', 'content', 'source', 'reply numbers', 'retweet numbers', 'likes numbers', 'filename'])
                    k.writerows(data)
                else:
                    k.writerows(data)

    @run_time
    def main(self):
        self.login()
        log_init().info('Read ID data files...')
        for row in self.red_csv():
            num, label, content, url = row
            # 判断是否获取过
            if self.keep_records(url, vali=True):
                print(f'{url} jump over!')
                continue
            log_init().info(f'{url} Data acquisition...')

            # 翻页获取数据
            try:
                self.get_basic(url)
            except Exception as e:
                log_init().error(e)
                continue
            finally:
                # 写入记录文件
                url = str(url).replace('\n', '')
                retweet_count = self.red_ini('Version', 'retweet_count')
                favorite_count = self.red_ini('Version', 'favorite_count')
                reply_count = self.red_ini('Version', 'reply_count')
                filename = f"retweet/{url.split('/')[-1]}.csv"
                data = [[num, label, content, url, reply_count, retweet_count, favorite_count, filename]]
                self.save_csv(data)

                # 写入获取记录
                self.keep_records(url)
                log_init().info('Save acquisition records')

            log_init().info('获取转推数据')
            self.retweeted_status(url)
            log_init().info(f'{url}Data acquisition completed!')

        self.driver.quit()
        # 关闭mitmduimp
        self.monitor.kill()


class Monitor:
    def net_is_used(self, port, ip='127.0.0.1'):
        """
        检测端口是否被占用
        :param port: 端口
        :param ip:IP地址
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
            s.shutdown(2)
            # print(f'sorry, {ip}:{port} 端口已被占用!')
            return True
        except Exception as e:
            # print(f'{ip}:{port}端口未启用!')
            log_init().error(e)
            return False

    def switch_mitmdump(self):
        """启动mitmdump服务"""
        log_init().info('Kill mitmdump Server')
        mitmdump = 'taskkill /F /IM mitmdump.exe'
        cmd = 'taskkill /F /IM cmd.exe'
        os.system(mitmdump)
        os.system(cmd)
        log_init().info('Start mitmdump Server')
        os.system('start /min mitmdump --mode upstream:https://127.0.0.1:1080 -s mitmdump_server.py')
        time.sleep(5)
        if not self.net_is_used(1080):
            log_init().info('mitmdump Service failed to start!')
            os._exit(0)
        log_init().info('mitmdump Service started successfully!')

    def kill(self):
        mitmdump = 'taskkill /F /IM mitmdump.exe'
        cmd = 'taskkill /F /IM cmd.exe'
        os.system(mitmdump)  # 杀死mitmdump进程
        os.system(cmd)  # 关闭命令行窗口
        log_init().info('Kill mitmdump Server')

    def run(self):
        self.switch_mitmdump()


def version():
    # 版本号
    print('*' * 20)
    print('脚本启动')
    print(f'selenium: {webdriver.__version__}')
    print('*' * 20)


if __name__ == '__main__':
    version()
    twitter = Twitter()
    twitter.main()