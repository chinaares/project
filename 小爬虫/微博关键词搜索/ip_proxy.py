# -*- coding:utf-8 -*-
# 文件 ：ip_proxy.py
# IED ：PyCharm
# 时间 ：2020/3/14 0014 16:06
# 版本 ：V1.0
'''
在使用requests 时,

* 需要安装 pip install -U 'requests[socks]'

* HTTPS 网站必须使用socks5连接

* 提取代理是选择socks5 协议

* 为运行程序的机器添加白名单 最多添加五个 个人中心 IP白名单 添加本地的IP地址进去

一天可以免费获取20个IP
'''
import sys
import json
import base64
import requests
from retrying import retry


class Proxy:
    def __init__(self):
        # self.username = '1033383881@qq.com'  # 账号
        # self.password = 'chenxiaoli2013'  # 密码
        self.username = '412037638@qq.com'  # 账号
        self.password = 'Chenxiaoli2013'  # 密码
        #  账号密码base64加密 构造headers
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36',
            'Proxy-Authorization': f'Basic {self.base_code()}'
        }

    def base_code(self):
        """账号密码base64加密 构造headers"""
        user_psd = f'{self.username}:{self.password}'
        encodestr = base64.b64encode(user_psd.encode('utf-8'))
        return encodestr.decode()

    @retry(stop_max_attempt_number=3)
    def get_proxy_ip(self):
        """请求代理IP 一次返回一个IP地址"""
        # 1033383881
        # url = r'http://api.wandoudl.com/api/ip?app_key=61056a77cc2115e31eb27ca62aec7ecc&pack=0&num=1&xy=3&type=2&lb=\n&mr=2&'
        # 412037638
        url = r'http://api.wandoudl.com/api/ip?app_key=61056a77cc2115e31eb27ca62aec7ecc&pack=0&num=1&xy=3&type=2&lb=\n&mr=2&'
        res = requests.get(url, timeout=10)
        content = json.loads(res.text)
        if content['code'] != 200:
            print(f'代理IP获取失败:\n错误代码：{content["code"]}\nmsg:{content["msg"]}')
            return
        print(content)
        ip = content['data'][0]['ip']  # ip
        port = content['data'][0]['port']  # 端口
        expire_time = content['data'][0]['expire_time']  # 过期时间
        # proxy = f'{ip}:{port}'
        # print(proxy)
        return ip, port, expire_time

    @retry(stop_max_attempt_number=3)
    def censor_ip(self, ip):
        """效验代理是否可用"""
        # 效验请求IP地址 请求此url返回请求的IP地址
        url = "http://whatismyip.akamai.com/"  # 爱尔兰

        print(f'代理前IP：{requests.get(url, timeout=5).text}')
        # 代理
        proxy = {
            'http': 'socks5://{}'.format(ip),
            'https': 'socks5://{}'.format(ip)
        }
        res = requests.get(url, proxies=proxy, headers=self.headers, timeout=5)
        print(f'代理后IP：{res.text}')

        return res.text

    def main(self):
        i = 1
        while i < 4:
            # 从api中提取出代理IP:PORT 一次提取一个
            ip, port, expire_time = self.get_proxy_ip()
            if not ip:
                return
            ip_port = f'{ip}:{port}'
            try:
                self.censor_ip(ip_port)
            except:
                print(f'代理IP验证失败，ip:{ip}不可用, 切换新IP!')
                i += 1
                continue

            print(f'ip:{ip_port}可用,过期时间:{expire_time}')
            return ip_port, expire_time
        print('代理效验失败,请检查代理配置。')
        sys.exit()


if __name__ == '__main__':
    proxy = Proxy()
    ip, expire_time = proxy.main()
