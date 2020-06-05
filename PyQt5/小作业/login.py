import sys
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox, QTextEdit, QFormLayout, \
    QPushButton, QHBoxLayout,QLineEdit, QGridLayout

from repoer import repoer


class login(QWidget):
    def __init__(self):
        super(login, self).__init__()
        self.resize(250, 200)
        self.setWindowTitle('登录')
        # 标题
        self.title = QLabel("      <<程序设计基础-----Python>>")
        self.title.setFixedSize(200, 20)

        # 初始化用户名文本框
        self.nameLabel = QLabel("用户名:")
        self.name = QLineEdit(self)
        # 初始化用户名文本框
        self.passwordLabel = QLabel("密  码:")
        self.password = QLineEdit(self)
        # 初始化注册按钮
        self.save_combobox = QPushButton(self)
        # 初始化登录按钮
        self.start_btn = QPushButton(self)
        # 初始化取消按钮
        self.cancel_btn = QPushButton(self)

        # 界面布局 全局控件（注意参数self），用于承载全局布局
        wwg = QWidget(self)
        self.w_layout = QHBoxLayout(wwg)  # 初始化全局布局为水平模式(全局布局)
        self.h_layout = QHBoxLayout()  # 初始化水平布局(局部布局)
        self.v_layout = QVBoxLayout()  # 初始化垂直布局(局部布局)
        self.g_layout = QGridLayout()  # 初始化网格布局(局部布局)

        # 实例化
        self.name_init()
        self.password_init()
        self.combobox_init()
        self.start_btn_init()
        self.cancel_init()
        self.layout_init()

    def name_init(self):
        """用户名 默认配置"""
        # 设置文本框尺寸
        self.name.setFixedSize(200, 20)
        # 设置默认文本
        self.name.setPlaceholderText("请输入用户名")

    def password_init(self):
        """用户名 默认配置"""
        # 设置文本框尺寸
        self.password.setFixedSize(200, 20)
        # 设置默认文本
        self.password.setPlaceholderText("请输入密码")

    def combobox_init(self):
        """注册 按钮配置"""
        self.save_combobox.setText('注册')
        self.save_combobox.setFixedSize(50, 30)
        self.save_combobox.clicked.connect(self.combobox_slot)

    def start_btn_init(self):
        """登录 按钮配置"""
        self.start_btn.setText('登录')
        self.start_btn.setFixedSize(50, 30)
        self.start_btn.clicked.connect(self.start_btn_slot)

    def cancel_init(self):
        """取消 按钮配置"""
        self.cancel_btn.setText('取消')
        self.cancel_btn.setFixedSize(50, 30)
        self.cancel_btn.clicked.connect(self.cancel_btn_slot)

    def layout_init(self):
        """页面布局"""
        self.v_layout.addWidget(self.title)

        self.g_layout.addWidget(self.nameLabel, 0, 0)
        self.g_layout.addWidget(self.name, 0, 1)
        self.g_layout.addWidget(self.passwordLabel, 1, 0)
        self.g_layout.addWidget(self.password, 1, 1)  # 添加关键词按钮设置为网格布局指定位置为第一行第一个位置
        self.h_layout.addWidget(self.save_combobox)  # 将局部网格布局嵌套进局部水平布局(关键词输入控件、添加关键词按钮、启动按钮、暂停按钮 绑定在一起)
        self.h_layout.addWidget(self.start_btn)  # 将局部网格布局嵌套进局部水平布局(关键词输入控件、添加关键词按钮、启动按钮、暂停按钮 绑定在一起)
        self.h_layout.addWidget(self.cancel_btn)  # 将局部网格布局嵌套进局部水平布局(关键词输入控件、添加关键词按钮、启动按钮、暂停按钮 绑定在一起)
        self.v_layout.addLayout(self.g_layout)  # 将局部水平布局嵌套进局部垂直布局(将上一步整合的布局和输出控件平级,设置成垂直布局)
        self.v_layout.addLayout(self.h_layout)  # 将局部水平布局嵌套进局部垂直布局(将上一步整合的布局和输出控件平级,设置成垂直布局)

        # 将局部布局添加到全局布局中
        self.w_layout.addLayout(self.v_layout)
        # 将布局应用到窗口
        self.setLayout(self.w_layout)

    def combobox_slot(self):
        """注册 信号槽"""
        username = self.name.text()
        password = self.password.text()
        print(username, password)
        with open('user.txt', 'r') as f:
            flight = [i.replace('\n', '') for i in f.readlines()]
            if str(username) in flight:
                self.do_btn('用户名已存在!')
                return

        with open('user.txt', 'a+') as f:
            f.write(f'{username},{password}')
            f.write('\n')
        self.do_btn('注册成功!')

    def start_btn_slot(self):
        """登录 信号槽"""
        username = self.name.text()
        password = self.password.text()
        print(username, password)
        for user in open('user.txt', 'r'):
            user = user.replace('\n', '').split(',')
            if username == user[0]:
                if password == user[1]:
                    print('登录成功')
                    self.red_ini(username)
                    self.repo()
                    return
                self.do_btn('密码错误!')
                return
        self.do_btn('用户不存在!')

    def cancel_btn_slot(self):
        """取消 信号槽"""
        self.name.clear()
        self.password.clear()

    def repo(self):
        rep.show()
        self.close()

    def do_btn(self, cont):
        """消息 弹窗"""
        QMessageBox.information(self,
                                "提示",
                                f"{cont}",
                                QMessageBox.Yes)
    
    def red_ini(self, username):
        """读取、修改 ini配置文件"""
        file = 'config.ini'  # 文件路径
        cp = ConfigParser()  # 实例化
        cp.read(file, encoding='utf-8')  # 读取文件
        cp.set('Status', 'username', username)  # 修改数据
        # 写入新数据
        with open(file, 'w', encoding='utf-8') as f:
            cp.write(f)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = login()
    window.show()
    rep = repoer()
    sys.exit(app.exec_())