# coding=utf-8
# 作者    ： Administrator
# 文件    ：批量添加子站.py
# IED    ：PyCharm
# 创建时间 ：2019/8/17 21:35
import re
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
"""
网站验证规则：
1.ID
2.ip
"""


class Spider:
    def __init__(self):
        print('**********程序启动中**********')
        # selenium无界面模式
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # keep_alive 设置浏览器连接活跃状态
        # self.driver = webdriver.Chrome(chrome_options=chrome_options, keep_alive=False)
        print('**********程序启动成功**********')
        # 有界面模式
        self.driver = webdriver.Chrome(keep_alive=False)
        # 隐形等待时间
        self.wait = WebDriverWait(self.driver, 10, 0.5)
        # 浏览器窗口最大化
        self.driver.maximize_window()

    def get_url(self):
        for i in range(100):
            headers = {'User-Agent': str(UserAgent().random),
                       'Cookie': 'PHPSESSID=85428e66fcce44d93c4d336643f934c2; UM_distinctid=16c9ef8ba591b0-09e54315ed0905-36624209-1aeaa0-16c9ef8ba5a129; kt_qparams=id%3D2502%26dir%3Dj811; kt_ips=111.199.54.21; CNZZDATA1277632329=215466018-1566031934-%7C1566048148; kt_tcookie=1; kt_is_visited=1'}
            url = 'https://www.v99two.com/?mode=async&function=get_block&block_id=list_videos_most_recent_videos&sort_by=post_date&from={}'.format(i)
            try:
                response = requests.get(url, headers=headers, timeout=10)
                html = response.text
            except Exception as e:
                print(e)
                break

            # 添加cookie前 需要先打开页面
            self.driver.get('https://www.v99two.com/')
            # 获取登录前cookies
            # for ck in self.driver.get_cookies():
            #     print(ck)
            # 登录
            # time.sleep(30)
            # 获取登录后cookies
            # for ck in self.driver.get_cookies():
            #     print(ck)
            # driver请求添加cookie参数
            cookies = {'domain': '.v99two.com', 'name': 'PHPSESSID', 'value': '6cc7af233de034dd73d6333a2db5e5d8'}
            self.driver.add_cookie(cookie_dict=cookies)
            # 提取二级页面url
            urls = re.findall(r'<a href="(.*?)" title="', html, re.S | re.M)
            for video_url in urls:
                self.driver.get(video_url)
                html = self.driver.page_source
                # 提取视频url
                b_url = re.findall(r'<video src="(.*?)"', html, re.S | re.M)
                print(b_url)


if __name__ == '__main__':
    spider = Spider()
    spider.get_url()