# coding=utf-8
# 作者    ： Administrator
# 文件    ：验证码识别.py
# IED    ：PyCharm
# 创建时间 ：2019/8/10 18:33
"""
使用tesserocr识别字母数字验证码
环境配置教程：https://www.cnblogs.com/guishenyouhuo/p/10121864.html
cv2库安装：pip install opencv-python
"""
import cv2
# import tesserocr
import pytesseract
from PIL import Image

"""
图片处理流程：
1.PIL 将图片转换为灰度图
2.PIL 将灰度图转换为黑白图 或者 将灰度图二值化 根据实际情况二选一,一般直接转为黑白图即可
3.CV2 降噪处理 ,必须先进行图片灰值化
4.tesserocr 识别验证码
"""


class Code:
    def pretreatment(self):
        """PIL 灰值化 二值化 处理"""
        # 打开一张图片
        img = Image.open('code/phone.png')
        # 1.转为灰度图 模式L为灰色图像，它的每个像素用8个bit表示，0表示黑，255表示白，其他数字表示不同的灰度
        img_gray = img.convert('L')
        # img_gray.save('b.png')
        # 2.转为黑白图片 必须先转为灰度图 才可转为黑白图
        img_black_white = img_gray.point(lambda x: 0 if x > 200 else 255)
        img_black_white.save('a.png')

        # 2.设定二值化阈值 自定义灰度界限，大于这个值为黑色，小于这个值为白色
        # threshold = 100
        # table = []
        # # 0 代表黑色 1 代表白色
        # for i in range(256):
        #     if i < threshold:
        #         table.append(0)
        #     else:
        #         table.append(1)
        # 图片二值化 必须把图片灰值化处理后才可二值化
        # photo = img_gray.point(table, '1')
        # photo.save("a.png")


        """cv2 灰值化 二值化 处理"""
        # 打开一张图片
        img_cv = cv2.imread('a.png')
        # 灰值化
        im = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        # 二值化
        # cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)
        return im

    # 3.CV2降噪处理 img参数必须为灰值化之后的数据
    def interference_point(self, img):
        h, w = img.shape[:2]
        # 遍历像素点进行处理
        for y in range(0, w):
            for x in range(0, h):
                # 去掉边框上的点
                if y == 0 or y == w - 1 or x == 0 or x == h - 1:
                    img[x, y] = 255
                    continue
                count = 0
                if img[x, y - 1] == 255:
                    count += 1
                if img[x, y + 1] == 255:
                    count += 1
                if img[x - 1, y] == 255:
                    count += 1
                if img[x + 1, y] == 255:
                    count += 1
                if count > 2:
                    img[x, y] = 255
        # 保存图片
        cv2.imwrite('b.png', img)

    def run(self):
        im = self.pretreatment()
        self.interference_point(im)
        # 4. tesserocr识别验证码
        img = Image.open('b.png')
        code = pytesseract.image_to_string(img)
        print('验证码：{}'.format(code))
        if len(code) > 4:
            code = code.replace(' ', '')
            print(code[:4])
            return code[:4]
        print(code)
        return code


if __name__ == '__main__':
    code = Code()
    code.run()
