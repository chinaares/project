import sys
from configparser import ConfigParser

from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox, QTextEdit, QFormLayout


class repoer(QWidget):
    def __init__(self):
        super(repoer, self).__init__()
        self.resize(400, 500)
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
        self.name.setPlaceholderText("请输入500字学习心得总结:")

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