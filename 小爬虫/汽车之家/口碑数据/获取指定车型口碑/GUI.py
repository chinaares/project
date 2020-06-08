# -*- coding: UTF-8 -*-
# @Time    : 2019/6/20 8:51
# @Author  : project
# @File    : GUI.py
# @Software: PyCharm

import re
import os
import sys
import logging
import subprocess
from configparser import ConfigParser

from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QThread, pyqtSignal, QFile, QTextStream
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextBrowser, \
    QHBoxLayout, QVBoxLayout, QGridLayout, QTextEdit, QCheckBox, QMessageBox, QHeaderView, QTableWidget, \
    QTableWidgetItem

import res


# 项目路径
PATH = os.getcwd()


class CrawlWindow(QWidget):
    def __init__(self):
        super(CrawlWindow, self).__init__()
        self.resize(600, 700)
        self.setWindowTitle('汽车之家口碑数据')
        self.setWindowIcon(QIcon(':reson/maoyan.ico'))

        # 初始化输出文本框
        self.log_browser = QTextBrowser(self)
        # 初始化车型ID文本框 多行文本框
        self.price = QTextEdit(self)
        # 初始化查询本地数据按钮
        self.save_combobox = QPushButton(self)
        # 初始化更新数据库按钮
        self.update_database = QPushButton(self)
        # 初始化启动按钮
        self.start_btn = QPushButton(self)
        # 初始化表格控件
        self.table = QTableWidget(self)
        # 初始化暂停按钮
        self.stop = QPushButton(self)
        # 初始化写入车型ID复选框
        self.model_id = QCheckBox('写入车型ID', self)
        # 初始化IP代理复选框
        self.checkbox = QCheckBox('启用代理', self)
        # 初始化多线程复选框
        self.start_thread = QCheckBox('启用多线程', self)

        # 界面布局 全局控件（注意参数self），用于承载全局布局
        wwg = QWidget(self)
        self.w_layout = QHBoxLayout(wwg)  # 初始化全局布局为水平模式(全局布局)
        self.h_layout = QHBoxLayout()  # 初始化水平布局(局部布局)
        self.v_layout = QVBoxLayout()  # 初始化垂直布局(局部布局)
        self.g_layout = QGridLayout()  # 初始化网格布局(局部布局)
        # self.f_layout = QFormLayout()  # 初始化表单布局(局部布局)

        # 初始化音频播放
        self.btn_sound = QSound(':reson/btn.wav', self)
        self.finish_sound = QSound(':reson/finish.wav', self)

        # 实例化线程
        self.worker = MyThread()

        # 实例化控件默认配置
        self.movie_init()  # 关键词
        self.combobox_init()  # 查询本地数据按钮
        self.update_database_init()  # 更新数据库按钮
        self.start_btn_init()  # 启动按钮
        self.table_init()  # 表格控件
        self.stop_init()  # 暂停按钮
        self.layout_init()  # 页面布局
        self.set_log_init()  # 输出控件
        self.model_id_init()  # 写入车型ID复选框
        self.checkbox_init()  # IP代理复选框
        self.start_thread_init()  # 启用多线程代理复选框

        self.ini_init()  # 初始化配置文件参数
        self.count = True  # 是否清空输入框中的文本

    def ini_init(self):
        """config.ini 配置文件初始化"""
        self.log_browser.append('GUI界面启动中...')
        self.log_browser.append('GUI界面启动成功')
        self.log_browser.append('检查配置文件...')
        self.log_browser.append('初始化配置文件')
        self.red_ini('Status', 'proxy', '0')  # 设置IP代理为不可用
        self.red_ini('Status', 'thread', '0')  # 设置多线程关闭
        self.red_ini('Version', 'model', 'None')  # 设置车型ID为空
        self.log_browser.append('初始化配置文件成功')
        self.log_browser.append('<font color="green">系统启动成功</font>')

    def movie_init(self):
        """添加车系ID输入框 初始化配置"""
        # 文本框尺寸
        self.price.setFixedSize(220, 100)
        # 设置默认显示文本
        self.price.setPlainText("输入车系ID,多个ID以英文','隔开")
        # 输入内容时清空默认显示文本内容 selectionChanged:点击文本框时发射信号
        self.price.selectionChanged.connect(self.price_clear)

    def price_clear(self):
        """清空输入框中的默认显示文本"""
        if self.count:
            self.price.setPlainText('')
        self.count = False

    def combobox_init(self):
        """查询本地数据按钮 初始化配置"""
        self.save_combobox.setText('查询本地数据')
        self.save_combobox.setEnabled(True)
        # TODO 查询本地数据信号槽
        self.save_combobox.clicked.connect(self.combobox_btn_slot)

    def update_database_init(self):
        """更新数据库按钮 初始化配置"""
        self.update_database.setText('更新数据库')
        self.update_database.setEnabled(True)
        # TODO 启动爬虫
        self.update_database.clicked.connect(self.update_database_btn_slot)

    def start_btn_init(self):
        """启动按钮 初始化配置"""
        self.start_btn.setText('启动')
        self.start_btn.setEnabled(True)
        # self.start_btn.setFixedSize(300, 30)
        self.start_btn.clicked.connect(self.start_btn_slot)

    def table_init(self):
        """表格控件 配置"""
        self.table.setColumnCount(34)
        self.table.setHorizontalHeaderLabels(['用户ID', '用户姓名', '车系ID', '车型ID', '品牌名称', '车系名称', '购买车型', '购买地点(省)', '购买地点(市)',
                                                '购车经销商', '购买时间', '裸车购买价', '油耗(百公里)', '目前行驶', '满意内容', '不满意内容', '空间(评分)', '空间内容',
                                                '动力(评分)', '动力内容', '操控(评分)', '操控内容', '油耗(评分)', '油耗内容', '舒适性(评分)', '舒适性内容',
                                                '外观(评分)', '外观内容', '内饰(评分)', '内饰内容', '性价比(评分)', '性价比内容', '购车目的', 'eid'])
        # 设置水平方向表格为自适应的伸缩模式
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def stop_init(self):
        """暂停按钮 初始化配置"""
        self.stop.setText('停止')
        self.stop.setEnabled(False)
        self.stop.clicked.connect(self.stop_slot)

    def set_log_init(self):
        """输出控件 初始化配置"""
        self.log_browser.setFixedSize(600, 150)
        # 输出至输出文本框
        self.worker.log_signal.connect(self.set_log_slot)
        # 输出至表格控件
        self.worker.result_signal.connect(self.set_table_slot)
        # 调用清屏槽
        # self.worker.start_q.connect(self.set_start_slot)
        # 改变按钮状态
        self.worker.start_q.connect(self.set_enabled_slot)

    def model_id_init(self):
        """写入车型ID复选框 初始化配置"""
        self.model_id.stateChanged.connect(self.model_id_slot)

    def checkbox_init(self):
        """IP代理复选框 初始化配置"""
        # 复选框默认选中
        # self.checkbox.toggle()
        self.checkbox.stateChanged.connect(self.checkbox_slot)

    def start_thread_init(self):
        """开启多线程复选框 初始化配置"""
        self.start_thread.stateChanged.connect(self.start_thread_slot)

    def layout_init(self):
        """页面布局"""
        # 输出控件设置为垂直布局方式
        self.v_layout.addWidget(self.table)
        self.v_layout.addWidget(self.log_browser)

        # 局部布局 关键词输入控件、添加关键词按钮、启动按钮、暂停按钮 水平布局+网格布局方式
        self.h_layout.addWidget(self.price)  # 关键词输入控件设置为水平布局
        self.g_layout.addWidget(self.model_id, 0, 0)
        self.g_layout.addWidget(self.start_thread, 0, 1)
        self.g_layout.addWidget(self.checkbox, 0, 2)
        self.g_layout.addWidget(self.save_combobox, 1, 0)  # 添加关键词按钮设置为网格布局指定位置为第一行第一个位置
        self.g_layout.addWidget(self.update_database, 1, 1)  # 添加关键词按钮设置为网格布局指定位置为第一行第二个位置
        self.g_layout.addWidget(self.start_btn, 2, 0)  # 启动按钮设置为网格布局指定位置为第二行第一个位置
        self.g_layout.addWidget(self.stop, 2, 1)  # 暂停按钮设置为网格布局指定职位只第二行第二个位置
        self.h_layout.addLayout(self.g_layout)  # 将局部网格布局嵌套进局部水平布局(关键词输入控件、添加关键词按钮、启动按钮、暂停按钮 绑定在一起)
        self.v_layout.addLayout(self.h_layout)  # 将局部水平布局嵌套进局部垂直布局(将上一步整合的布局和输出控件平级,设置成垂直布局)

        # 将局部布局添加到全局布局中
        self.w_layout.addLayout(self.v_layout)
        # 将布局应用到窗口
        self.setLayout(self.w_layout)

    def program_btn(self, program_name):
        """程序启动"""
        # 判断添加关键词 按钮状态, True:可按，False:不可按。 isEnabled():返回控件状态
        if not self.model_id.isChecked():
            self.log_browser.append('<font color="red">请填写车型ID!!!</font>')
            return None
        self.btn_sound.play()
        self.log_browser.append('<font color="green">{}程序启动{}</font>'.format('*'*20, '*'*20))
        # 启动线程
        self.worker.name = program_name
        self.worker.start()
        # self.finish_sound.play()
        # 初始化各个按钮状态
        self.update_database.setEnabled(False)  # 更新数据库按钮
        self.price.setEnabled(False)  # 输入框
        self.save_combobox.setEnabled(False)  # 添加关键字按钮
        self.checkbox.setEnabled(False)  # IP代理复选框
        self.start_thread.setEnabled(False)  # 开启多线程复选框
        self.start_btn.setEnabled(False)  # 启动按钮
        self.stop.setEnabled(True)  # 暂停按钮

    def start_btn_slot(self):
        """启动按钮 信号槽"""
        program_name = r'DatabaseQuery.py'
        self.program_btn(program_name)


    def stop_slot(self):
        """暂停 信号槽"""
        # 改变程序状态
        self.worker.stop = True
        # 改变各按钮状态
        self.price.setEnabled(True)  # 输入框
        self.save_combobox.setEnabled(True)  # 添加关键字按钮
        self.checkbox.setEnabled(True)  # IP代理复选框
        self.start_thread.setEnabled(True)  # 开启多线程复选框
        self.start_btn.setEnabled(True)  # 启动按钮
        self.stop.setEnabled(False)  # 暂停按钮

    def model_id_slot(self):
        """车系ID输入控件 信号槽"""
        # 取消选中时的设置
        if not self.model_id.isChecked():
            # 改变输入框输入状态
            self.price.setEnabled(True)
            return
        words = self.get_words()
        if not words:
            return
        # GUI界面输入的车型ID写入文件
        words = words.replace('，', ',').replace('\n', '')
        val = self.red_ini('Version', 'model', words)
        self.log_browser.append(f'<font color="green">车型ID：[{val}]添加成功</font>')
        # 改变输入框输入状态
        self.price.setEnabled(False)

    def get_words(self):
        """提取输入框文本信息 信号槽"""
        words = self.price.toPlainText()
        if not words or "输入车系ID,多个ID以英文','隔开" in words:
            self.log_browser.append('<font color="red">请正确填写车型ID!!!</font>')
            return
        return words

    def combobox_btn_slot(self):
        """查询本地数据按钮 信号槽"""
        program_name = r'DatabaseQuery.py'
        self.program_btn(program_name)

    def update_database_btn_slot(self):
        """更新数据库按钮 信号槽"""
        program_name = r'model_koubei.py'
        self.program_btn(program_name)

    def checkbox_slot(self):
        """IP代理复选框 信号槽"""
        if self.checkbox.isChecked():
            self.red_ini('Status', 'proxy', '1')
            self.log_browser.append('<font color="green">开启IP代理</font>')
            return None
        self.red_ini('Status', 'proxy', '0')
        self.log_browser.append('<font color="red">关闭IP代理</font>')

    def start_thread_slot(self):
        """多线程复选框 信号槽"""
        if self.start_thread.isChecked():
            self.red_ini('Status', 'thread', '1')
            self.log_browser.append('<font color="green">开启多线程</font>')
            return None
        self.red_ini('Status', 'thread', '0')
        self.log_browser.append('<font color="red">关闭多线程</font>')

    def set_enabled_slot(self, status):
        """子程序结束改变按钮状态"""
        if not status:
            self.price.setEnabled(True)  # 输入框
            self.save_combobox.setEnabled(True)  # 添加关键字按钮
            self.checkbox.setEnabled(True)  # IP代理
            self.start_thread.setEnabled(True)  # 开启多线程复选框
            self.start_btn.setEnabled(True)  # 启动按钮
            self.update_database.setEnabled(True)
            self.stop.setEnabled(False)  # 暂停按钮

    def set_log_slot(self, log):
        """添加输出控件显示内容 信号槽"""
        self.log_browser.append(log)

    def set_table_slot(self, userId, eid, userName, model, specid, brandname, seriesname, specname, boughtprovincename, \
            boughtcityname, dealername, boughtdate, boughtPrice, actualOilConsumption, drivekilometer, \
            satisfaction_content, Dissatisfied_content, spaceScene, space_content, powerScene, \
            power_content, maneuverabilityScene, Control_content, oilScene, oilScene_content, \
            comfortablenessScene, Comfort_content, apperanceScene, Exterior_content, internalScene, \
            Interior_content, costefficientScene, Costeffective_content, purpose):
        """表格控件输出"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(userId))
        self.table.setItem(row, 1, QTableWidgetItem(userName))
        self.table.setItem(row, 2, QTableWidgetItem(model))
        self.table.setItem(row, 3, QTableWidgetItem(specid))
        self.table.setItem(row, 4, QTableWidgetItem(brandname))
        self.table.setItem(row, 5, QTableWidgetItem(seriesname))
        self.table.setItem(row, 6, QTableWidgetItem(specname))
        self.table.setItem(row, 7, QTableWidgetItem(boughtprovincename))
        self.table.setItem(row, 8, QTableWidgetItem(boughtcityname))
        self.table.setItem(row, 9, QTableWidgetItem(dealername))
        self.table.setItem(row, 10, QTableWidgetItem(boughtdate))
        self.table.setItem(row, 11, QTableWidgetItem(boughtPrice))
        self.table.setItem(row, 12, QTableWidgetItem(actualOilConsumption))
        self.table.setItem(row, 13, QTableWidgetItem(drivekilometer))
        self.table.setItem(row, 14, QTableWidgetItem(satisfaction_content))
        self.table.setItem(row, 15, QTableWidgetItem(Dissatisfied_content))
        self.table.setItem(row, 16, QTableWidgetItem(spaceScene))
        self.table.setItem(row, 17, QTableWidgetItem(space_content))
        self.table.setItem(row, 18, QTableWidgetItem(powerScene))
        self.table.setItem(row, 19, QTableWidgetItem(power_content))
        self.table.setItem(row, 20, QTableWidgetItem(maneuverabilityScene))
        self.table.setItem(row, 21, QTableWidgetItem(Control_content))
        self.table.setItem(row, 22, QTableWidgetItem(oilScene))
        self.table.setItem(row, 23, QTableWidgetItem(oilScene_content))
        self.table.setItem(row, 24, QTableWidgetItem(comfortablenessScene))
        self.table.setItem(row, 25, QTableWidgetItem(Comfort_content))
        self.table.setItem(row, 26, QTableWidgetItem(apperanceScene))
        self.table.setItem(row, 27, QTableWidgetItem(Exterior_content))
        self.table.setItem(row, 28, QTableWidgetItem(internalScene))
        self.table.setItem(row, 29, QTableWidgetItem(Interior_content))
        self.table.setItem(row, 30, QTableWidgetItem(costefficientScene))
        self.table.setItem(row, 31, QTableWidgetItem(Costeffective_content))
        self.table.setItem(row, 32, QTableWidgetItem(purpose))
        self.table.setItem(row, 33, QTableWidgetItem(eid))

    def set_start_slot(self):
        """输出框窗口清空 信号槽"""
        self.log_browser.clear()

    def red_ini(self, section, name, val):
        """读取、修改 ini配置文件"""
        file = PATH + '\config.ini'  # 文件路径
        cp = ConfigParser()  # 实例化
        cp.read(file, encoding='utf-8')  # 读取文件
        cp.set(section, name, val)  # 修改数据
        # 写入新数据
        with open(file, 'w', encoding='utf-8') as f:
            cp.write(f)

        # 读取修改后数据
        val = cp.get(section, name)
        return val

    def closeEvent(self, event):
        """程序退出确认弹窗"""
        reply = QMessageBox.question(self, '信息', '确认退出吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class MyThread(QThread):
    result_signal = pyqtSignal(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
                               str, str, str, str, str, str, str, str, str, str, str, str, str, str, str)
    log_signal = pyqtSignal(str)
    start_q = pyqtSignal(bool)
    stop = False  # 是否终止程序
    name = None

    def __init__(self):
        super(MyThread, self).__init__()

    def run(self):
        # 重写run方法
        # stdout PIPE 输出信息管道（把print信息重定向至管道）
        # stderr STDOUT 错误和日志信息管道
        # bufsize 缓冲设置默认值0 -- 表示不缓冲 1 -- 表示缓冲  NOTE: 如果遇到性能问题，建议将bufsize设置成 -1 或足够大的正数(如 4096）
        # r.poll()   检查子进程状态
        # r.kill()   终止子进程
        # r.send_signal() 向子进程发送信号
        # r.terminate()   终止子进程
        # r.returncode 子进程的退出状态
        # r.stdout.flush() 如果出现子进程假死 管道阻塞 手动刷新缓冲
        try:
            self.stop = False
            self.start_q.emit(True)
            r = subprocess.Popen(['python', self.name],  # 需要执行的文件路径
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 bufsize=0)

            while r.poll() is None:
                # 判断是否终止子程序(调用的程序)
                if self.stop:
                    r.terminate()  # win10终止子进程
                    self.log_signal.emit('<font color="red">*****程序已关闭*****</font>')
                    return
                line = str(r.stdout.readline(), encoding='UTF-8')  # TODO 打包时改为GBK
                line = line.strip()
                if line:
                    self.log_data(line)

            # 判断子进程状态
            if not r.returncode:
                self.log_signal.emit('<font color="green">Subprogram success</font>')
                self.log_signal.emit('<font color="green">程序执行完毕!</font>')
                self.start_q.emit(False)
            else:
                self.log_signal.emit('<font color="red">Subprogram failed</font>')
                self.log_signal.emit('<font color="red">程序执行错误!</font>')
                self.start_q.emit(False)
        except Exception as e:
            print(e)
            self.start_q.emit(False)
            # self.log_init().error(e)
            # self.log_init().exception(e)

    def log_data(self, line):
        # 筛选数据
        if 'content' in line:
            # print(len(eval(line.replace('content:', ''))))
            content = [str(i) for i in eval(line.replace('content:', ''))]
            ID, eid, userId, userName, model, specid, brandname, seriesname, specname, boughtprovincename, \
            boughtcityname, dealername, boughtdate, boughtPrice, actualOilConsumption, drivekilometer, \
            satisfaction_content, Dissatisfied_content, spaceScene, space_content, powerScene, \
            power_content, maneuverabilityScene, Control_content, oilScene, oilScene_content, \
            comfortablenessScene, Comfort_content, apperanceScene, Exterior_content, internalScene, \
            Interior_content, costefficientScene, Costeffective_content, purpose = content

            self.result_signal.emit(userId, eid, userName, model, specid, brandname, seriesname, specname, boughtprovincename, \
            boughtcityname, dealername, boughtdate, boughtPrice, actualOilConsumption, drivekilometer, \
            satisfaction_content, Dissatisfied_content, spaceScene, space_content, powerScene, \
            power_content, maneuverabilityScene, Control_content, oilScene, oilScene_content, \
            comfortablenessScene, Comfort_content, apperanceScene, Exterior_content, internalScene, \
            Interior_content, costefficientScene, Costeffective_content, purpose)
            return

        # 把管道输出内容传递给显示控件,在GUI界面中显示出来
        self.log_signal.emit(line)


def read_qss(style):
    file = QFile(style)
    file.open(QFile.ReadOnly)
    return QTextStream(file).readAll()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CrawlWindow()
    qss_style = read_qss(':reson/style.qss')
    window.setStyleSheet(qss_style)
    window.show()
    sys.exit(app.exec_())