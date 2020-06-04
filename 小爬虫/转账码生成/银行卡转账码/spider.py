#!/usr/bin/env python 
# encoding: utf-8
# @version: v1.0
# @author: xxxx
# @site: 
# @software: PyCharm
# @file: 批量添加子站.py
# @time: 2019/9/3 13:01

"""
1.根据GUI写入数据拼接URL
  # 获取GUI写入数据保存至txt 主程序读取txt文件 拼接url
2.URL转换为短链接
  # 百度短链转换，每天一万条免费额度 至关重要 有些短链网站转换后会出现中文乱码
  # 中文需转码 quote
3.短链接生成二维码
  # 聚合数据 短链接生成二维码
  # 中文需转码 quote

短链接 转换 ：百度短链接
查询银行代码
https://ccdcapi.alipay.com/validateAndCacheCardInfo.json?cardNo=6216698100000331190&cardBinCheck=true

alipays://platformapi/startapp?appId=09999988&actionType=toCard&sourceId=bill&cardNo=6217000030001234567&bankAccount=%E9%A9%AC%E4%BA%91&money=0.01&amount=0.01&bankMark=CCB&bankName=%E4%B8%AD%E5%9B%BD%E5%BB%BA%E8%AE%BE%E9%93%B6%E8%A1%8C
参数：
appId=09999988   // 应用ID -默认
actionType=toCard  // 转账类型 toCard-到银行卡
sourceId=bill  // 未知
cardNo=6217000030001234567  // 银行卡号
bankAccount=%E9%A9%AC%E4%BA%91  // 银行账户
money=0.01  // 转账金额
amount=0.01  // 转账额度
bankMark=CCB  // 银行代号 -可选
bankName=%E4%B8%AD%E5%9B%BD%E5%BB%BA%E8%AE%BE%E9%93%B6%E8%A1%8C  // 银行名称

接口：
    转账到银行卡：
        支付宝 转账接口：需要urlencode  from urllib.parse import quote
        https://www.alipay.com/?appId=09999988&actionType=toCard&sourceId=bill&cardNo=银行卡号&bankAccount=银行账户名&money=转账金额&amount=备注&bankMark=银行英文简写&bankName=银行中文名称

    隐藏卡号：
        cardid，cardno，bankname，bankshortname，cardname
        cardid=是一个银行卡的一个ID，估计是zfb自己定义的吧
        cardno=隐藏的卡号
        bankname=银行名称
        bankshortname=银行简称
        cardname=真实姓名
        https://www.alipay.com/?appId=09999988&actionType=toCard&sourceId=bill&cardNo=cardno&bankAccount=cardname&money=1.00&amount=1.00&bankMark=bankshortname&bankName=bankname&cardIndex=cardid&cardNoHidden=true&cardChannel=HISTORY_CARD&orderSource=from

"""
import os
import uuid
import json
import string
import requests
from urllib.parse import quote  # url编码
from fake_useragent import UserAgent

from image_process import Picture


class Spider:
    def __init__(self):
        # self.headers = {'user-agent': str(UserAgent().random)}
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'}

    def get_url(self, lang_url):
        """
        长链接转换短链接 百度短链
        0：正常返回短网址
        -1：短网址生成失败
        -2：长网址不合法
        -3：长网址存在安全隐患
        -4：内部错误
        -5：短网址服务目前不支持该域名
        -6：有效期设置错误
        -7：长网址在安全检测中
        -1xx：Token验证失败
        :param lang_url:
        :return:
        """
        # url 中文转码  string.printable 跳过ascii码
        lang_url = quote(lang_url, string.printable)
        print(lang_url)

        host = 'https://dwz.cn'
        path = '/admin/v2/create'
        url = host + path
        method = 'POST'
        content_type = 'application/json'
        # 设置Token
        token = '9a3dc2e0010d0168da6b82565f756d16'
        # 设置待创建的长网址
        bodys = {'Url': lang_url, 'TermOfValidity': '1-year'}
        # 配置headers
        headers = {'Content-Type': content_type, 'Token': token}
        count = 1
        while True:
            # 发起请求
            response = requests.post(url=url, data=json.dumps(bodys), headers=headers, verify=False)
            # 读取响应
            response = json.loads(response.text)
            if count > 3:
                print('程序运行错误,请联系开发者!')
                os._exit(0)
            if response['Code']:
                print('错误代码：{} 重试'.format(response['Code']))
                count += 1
                continue

            return response['ShortUrl']

    def _get_url(self, lang_url):
        lang_url = quote(lang_url)
        print(lang_url)
        response = requests.get(f'http://mrw.so/api.php?format=json&url={lang_url}&key=5d6dfeb6d3c38135d0e2b157@6284f3680b4f4c41f1de39fbe26f7635')
        response = json.loads(response.text)
        print(response['url'])
        return response['url']

    def code_generate(self, short_link):
        """
        聚合数据 短链接生成二维码
        https://www.juhe.cn/box/index/id/296 错误码参照表
        二维码生成
        :return:
        """
        # 转码
        short_link = quote(short_link, string.digits)
        url = 'http://apis.juhe.cn/qrcode/api?text={}&el=&bgcolor=&fgcolor=&logo=&w=&m=&lw=&type=2&key=b142a4a659dfa5237bf54a78baf8382f'.format(short_link)
        # print(url)
        response = requests.get(url, headers=self.headers, verify=False, timeout=10)
        with open('image/code.png', 'wb') as f:
            f.write(response.content)
            print('支付宝转账码生成成功!')
    
    def read_txt(self):
        """
        读取界面输入数据文件
        :return: 
        """
        # 获取当前目录
        path = os.getcwd()
        # 返回指定目录下所有文件
        files = os.listdir(path)
        # 筛选指定文件
        files = [i for i in files if 'config.txt' in i]
        if not files:
            print('读取配置文件错误,请正确填写数据!')
            os._exit(0)

        with open(files[0], 'r', encoding='UTF-8') as f:
            content = f.read().split(',')
            content = [i for i in content if i]
            content = content + ['ABC', '中国农业银行'] if len(content) < 5 else content
            return content

    def upload(self, uid, name, Countdown, url):
        """向服务器上传数据"""
        _url = f'http://www.dongdongmeiche.cn/upload/'
        data = {'uid': uid, 'name': name, 'time': Countdown, 'url': url}
        response = requests.post(_url, data=data)
        try:
            content = response.json()
            code = content['errorcode']
            if code != 10001:
                print(content['context'])
                os._exit(0)
            print(content['context'])
        except:
            print('连接服务器错误!')

    def Generate(self, data):
        """生成记录"""
        with open('image/生成记录.txt', 'a+', encoding='utf-8') as f:
            f.write(data)
            f.write('\n')

    def run(self):
        # 隐藏卡号url
        # cardID 隐藏卡号 获取方法  https://zhuanlan.zhihu.com/p/65495172
        # content = ['621569***3079', 'BOC', '吕俊臻', '兴业银行 ', '2005091991097662286']
        # _url = f'https://www.alipay.com/?appId=09999988&actionType=toCard&sourceId=bill&cardNo={content[0]}&' \
        #        f'bankAccount={content[2]}&money=&amount=&bankMark={content[1]}&bankName={content[3]}&cardIndex={content[4]}&cardNoHidden=true&cardChannel=HISTORY_CARD&orderSource=from'
        # print(_url)
        # 普通转账url
        content = self.read_txt()
        # 新接口
        _url = f'https://ds.alipay.com/?from=mobilecodec&scheme=alipays%3A%2F%2Fplatformapi%2Fstartapp%3FappId%3D20000200' \
               f'%26actionType%3DtoCard%26sourceId=bill%26cardNo={content[1]}%26bankAccount={content[0]}%0A%26money=' \
               f'%26amount=%26bankMark={content[3]}%26bankName={content[4]}%26cardNoHidden=true%26cardChannel=HISTORY_CARD%26orderSource=from'

        # 旧接口
        # _url = 'https://www.alipay.com/?appId=09999988&actionType=toCard&sourceId=bill&cardNo={}&bankAccount={}&' \
        #        'money=&amount=&bankMark={}&bankName={}&orderSource='.format(content[1], content[0], content[3], content[4])
        print(_url)

        # 防风控制作
        # _url = quote(_url, string.printable)
        # uid = ''.join(str(uuid.uuid4()).split('-'))
        # self.upload(uid, content[2], str(15), str(_url))
        # _url = f'http://www.dongdongmeiche.cn/alipay/{uid}'
        # print(_url)

        # 百度长链接转换短链接
        short_link = self.get_url(_url)
        # short_link = 'http://mrw.so/4BH9yz '
        print(f'百度短链：{short_link}')

        # 缩短网址 http://mrw.so/api.html
        # short_link = self._get_url(_url)

        # 短链接生成二维码
        self.code_generate(short_link)

        # 保存生成记录
        data = f'{content[2]},{short_link},{_url}'
        self.Generate(data)

        # 二维码合成图片
        image_process = Picture()
        image_process.text = content[2]
        image_process.run()


if __name__ == '__main__':
    spider = Spider()
    spider.run()

