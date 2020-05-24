from bs4 import BeautifulSoup

"""
代理添加
设置本地代理 可用Fidder抓python请求包
"""
import requests

proxies = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888",
}
response = requests.get("https://www.baidu.com", verify=False, proxies=proxies)
print(response)


"""
西刺代理IP 抓取 + 效验
"""


def get_ip_list(ip_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0'}
    web_data = requests.get(ip_url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        try:
            tds = ip_info.find_all('td')
            # 获取HTTPS ip
            if tds[5].text == 'HTTPS':
                # 拼接IP:端口
                ip_list.append(tds[1].text + ':' + tds[2].text)
        except:
            continue
    # 效验IP 是否可用
    for ip in ip_list:
        try:
            # 拼接代理
            proxy_temp = {"https": "https://" + ip}
            test_url = 'https://wulumuqi.anjuke.com/community/'

            res = requests.get(test_url, headers=headers, proxies=proxy_temp, timeout=3)
            # 判断状态码
            if res.status_code == 200:
                return ip
        except Exception as e:
            ip_list.remove(ip)
            print(e)
            continue
