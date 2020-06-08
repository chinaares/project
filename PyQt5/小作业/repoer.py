import sys
from configparser import ConfigParser

from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox, QTextEdit, QFormLayout


class repoer(QWidget):
    def __init__(self):
        super(repoer, self).__init__()
        self.resize(400, 650)
        username = self.red_ini()
        self.setWindowTitle(username)
        # 标题
        self.title = QLabel("   个人1寸照片显示")
        # 设置标题框尺寸
        self.title.setFixedSize(200, 20)
        self.title1 = QLabel("学号：196210312 姓名：刘宝荫")
        self.title1.setFixedSize(200, 20)

        # 初始化课程报告文本框
        self.nameLabel = QLabel("课程总结报告:")
        self.nameLabel.setFixedSize(200, 40)
        self.name = QTextEdit(self)  # 文本输入框

        # 加载图片
        self.img = QLabel()

        self.h_layout = QVBoxLayout()  # 初始化水平布局(局部布局)
        self.v_layout = QFormLayout()  # 初始化垂直布局(局部布局)
        self.v_layout.setFormAlignment(Qt.AlignHCenter)

        self.name_init()
        self.layout_init()
        self.img_init()

    def name_init(self):
        text = "学习报告:\n1.课程内容总结，首先，我们学到了对于程序的定义，理解了什么是程序？什么是程序设计的含义，然后通过编程应用python对一些简单的编程语言进行学习。" \
               "在课程中，我们学习了python的基本数据类型，与python的input（）函数，和赋值运算符，逻辑运算符等基础函数的应用，并尝试编写了简易计算器的程序，" \
               "与猜数字程序。在界面可视化的学习中，我们学会了利用窗体和按钮的建立与布局，制作了可视化的简易计算器与猜数字的小程序。在课程中，我们学会利用python建立可视化的界面，并实现部分简单功能的运行。\n" \
               "2，课程学习心得六月初，对python的学习已三月有余，于计算机的运行程序，得以窥其一二，" \
               "虽是管中窥豹知之甚少，但在课程的学习中亦是获益良多。于课上，得以理解程序语言的条理与逻辑性，这是我们艺术类专业所不具备的，这个过程即是利用感性思维去尝试理解理性秩序的过程。" \
               "人的生活亦是如此，介乎于感性与理性间，思其秩序，辩其优劣，文理之别自是如此。故而“理“赋予文明进步，而”文”赋予文明以色彩。进而纳其逻辑为己用，亦为乐事。\n" \
               "3，自己的专业如何与python结合视觉传达设计专业可以通过对python的简单了解，在其后设计UI交互的界面时，可更好地与编程人员进行沟通，以提高工作效率。"
        # self.name.setPlaceholderText("请输入500字学习心得总结:")
        self.name.setText(text)
        # self.name.setText(text1)

    def img_init(self):
        self.img.setFixedSize(150, 200)
        self.img.move(100, 80)
        self.img.setStyleSheet("QLabel{background:white;}"
                              "QLabel{color:rgb(300,300,300,120);font-size:10px;font-weight:bold;font-family:宋体;}"
                              )

        jpg = QtGui.QPixmap('touxiang.jpg').scaled(self.img.width(), self.img.height())
        self.img.setPixmap(jpg)

    def layout_init(self):
        """页面布局"""
        self.v_layout.addWidget(self.title)
        self.v_layout.addWidget(self.title1)
        self.v_layout.addWidget(self.img)

        self.h_layout.addLayout(self.v_layout)
        self.h_layout.addWidget(self.nameLabel)
        self.h_layout.addWidget(self.name)

        self.setLayout(self.h_layout)
        
    def red_ini(self):
        """读取、修改 ini配置文件"""
        file = 'config.ini'  # 文件路径
        cp = ConfigParser()  # 实例化
        cp.read(file, encoding='utf-8')  # 读取文件
        res = cp.get('Status', 'username')
        return res


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = repoer()
    window.show()
    sys.exit(app.exec_())