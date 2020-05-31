# coding=utf-8
# 作者    ： Administrator
# 文件    ：TrieData.py
# IED    ：PyCharm
# 创建时间 ：2020/5/30 16:20
import os, sys, datetime, logging, requests, csv
from lxml.etree import HTML
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


class TrieData:
    def __init__(self):
        self.headers = {"User-Agent": UserAgent().random}
        self.session = requests.session()
        # 必须要请求一次主页获取session值,不然会无线跳转报错
        self.session.get(url='https://www.tuhu.cn/', headers=self.headers)

    @retry(stop_max_attempt_number=30)
    def _parse_url(self, url):
        """url请求"""
        while True:
            try:
                # allow_redirects关闭页面跳转
                response = requests.get(url, headers=self.headers, allow_redirects=False, timeout=300)
            except Exception as e:
                log_init().info(e)
                continue
            return response

    def is_null(self, an_str):
        """判断是否为空列表"""
        if an_str:
            return an_str
        else:
            return '-'

    def get_product_url(self):
        """获取轮胎详情页URL"""
        for i in range(1, 189):
            tires_url = f'https://item.tuhu.cn/Tires/{i}/f0.html'
            log_init().info(f'第：{i}页数据获取中...')
            response = self._parse_url(tires_url)
            tires_html = HTML(response.text).xpath('//*[@id="Products"]/table/tbody/tr')
            if not tires_html:
                continue

            for tire in tires_html:
                product_url = tire.xpath('td[2]/a/@href')[0]
                yield product_url
            log_init().info(f'第：{i}页数据获取完成!')

    def get_trie_data(self, product_url):
        """获取轮胎详情数据"""
        log_init().info(f'{product_url}数据请求中...')
        response = self._parse_url(product_url)
        html = HTML(response.text)

        # 轮胎名称
        title = html.xpath('//*[@id="product_detail"]/div[2]/h1/text()')
        title = [i.strip() for i in title if i.strip()][0]

        properties = html.xpath('//*[@id="product_detail"]/div[2]/div[1]/ul/li')

        # 解析轮胎参数
        reltus = {}
        for propertie in properties:
            TireBrand = propertie.xpath('.//text()')
            reltus[TireBrand[0].replace('：', '')] = TireBrand[1]

        TireBrand = self.is_null(reltus.get('轮胎品牌'))  # 轮胎品牌
        Productspec = self.is_null(reltus.get('产品规格'))  # 产品规格
        Speedlevel = self.is_null(reltus.get('速度级别'))  # 速度级别
        LoadIndex = self.is_null(reltus.get('载重指数'))  # 载重指数
        ProductOrigin = self.is_null(reltus.get('产品产地'))  # 产品产地
        Tyrecategory = self.is_null(reltus.get('轮胎类别'))  # 轮胎类别
        Tirepattern = self.is_null(reltus.get('轮胎花纹'))  # 轮胎花纹
        price = html.xpath('//*[@id="product_detail"]/div[2]/div[2]/div[2]/strong/text()')[0]  # 价格

        data = [[title, TireBrand, Productspec, Speedlevel, LoadIndex, ProductOrigin, Tyrecategory, Tirepattern, price,
                 product_url]]

        log_init().info(f'{product_url}数据获取成功!')
        self.csv_save(data)

    def csv_save(self, data):
        """保存数据"""
        with open("轮胎数据.csv", "a+", encoding='utf-8', newline="") as f:
            k = csv.writer(f, delimiter=',')
            with open("轮胎数据.csv", "r", encoding='utf-8', newline="") as f1:
                reader = csv.reader(f1)
                if not [row for row in reader]:
                    k.writerow(['轮胎名称', '轮胎品牌', '产品规格', '速度级别', '载重指数', '产品产地', '轮胎类别', '轮胎花纹', '价格',
                                'URL'])
                    k.writerows(data)
                else:
                    k.writerows(data)

    @run_time
    def run(self):
        # 多线程启动
        # pool = Pool(1)
        for product_url in self.get_product_url():
            # 启动线程
            self.get_trie_data(product_url)
        #     pool.apply_async(self.get_trie_data, (product_url,))
        #
        # pool.close()
        # pool.join()


if __name__ == '__main__':
    spider = TrieData()
    spider.run()
    # spider.get_trie_data('https://item.tuhu.cn/Products/TR-HK-VENTUS-K117/52.html')