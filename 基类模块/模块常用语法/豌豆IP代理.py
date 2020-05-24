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

* 为运行程序的机器添加白名单 最多添加五个

一天可以免费获取20个IP
'''
import json
import base64
import requests
from retrying import retry


class Proxy:
    def __init__(self):
        self.username = '1033383881@qq.com'  # 账号
        self.password = 'chenxiaoli2013'  # 密码
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

        print(f'代理前IP：{requests.get(url, timeout=10).text}')
        # 代理
        proxy = {
            'http': 'socks5://{}'.format(ip),
            'https': 'socks5://{}'.format(ip)
        }
        res = requests.get(url, proxies=proxy, headers=self.headers, timeout=10)
        print(f'代理后IP：{res.text}')

        return res.text

    def main(self):
        # 从api中提取出代理IP:PORT 一次提取一个
        ip, port, expire_time = self.get_proxy_ip()
        if not ip:
            return
        ip_port = f'{ip}:{port}'
        res_ip = self.censor_ip(ip_port)
        if ip != res_ip:
            print(f'代理IP验证失败，ip:{ip}不可用')
            return
        print(f'ip:{ip_port}可用 {expire_time} 过期!')
        return ip_port, expire_time


if __name__ == '__main__':
    proxy = Proxy()
    ip, expire_time = proxy.main()



"""调用"""
def proxy(self):
    """
    调用IP代理
    :return:
    """
    # 判断代理IP是否过期
    new_time = datetime.datetime.now()
    if self.expire_time and new_time < datetime.datetime.strptime(self.expire_time, "%Y-%m-%d %H:%M:%S"):
        # # 当前时间小于代理到期时间证明代理可用
        # if new_time < datetime.datetime.strptime(self.expire_time, "%Y-%m-%d %H:%M:%S"):
        print(f'{self.proxies} 未过期 过期时间：{self.expire_time}')
        return
    proxy = Proxy()
    ip_port, expire_time = proxy.main()
    self.headers = proxy.headers
    self.proxies = {
        'http': 'socks5://{}'.format(ip_port),
        'https': 'socks5://{}'.format(ip_port)
    }
    self.expire_time = expire_time