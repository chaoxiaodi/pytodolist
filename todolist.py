import os
import sys
import uuid
import json
import datetime
import win32con
import win32api
import webbrowser
from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem
from pytodolist import Ui_PyTodoMain
from jobeverycommon import Ui_jobEveryCommon

BASE_PATH = os.getcwd()
JOB_PATH = os.path.join(BASE_PATH, 'job')
JOB_COMMON = os.path.join(JOB_PATH, 'common.todo')
JOB_DAY = os.path.join(JOB_PATH, 'day.todo')
JOB_WEEK = os.path.join(JOB_PATH, 'week.todo')
JOB_MONTH = os.path.join(JOB_PATH, 'month.todo')
ICO_PATH = os.path.join(BASE_PATH, 'todolist128.ico')
COMM_TITLE = ['每日任务', '每周任务', '每月任务']
COMB_DAY = list(map(lambda i: str(i) + ':00', list(range(1, 24))))
COMB_WEEK = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
COMB_MONTH = list(map(lambda i: str(i) + '号', list(range(1, 32))))


class PytodoMain(QMainWindow, Ui_PyTodoMain):
    def __init__(self, parent=None):
        super(PytodoMain, self).__init__(parent)
        self.setupUi(self)


class CommonWindow(QMainWindow, Ui_jobEveryCommon):
    def __init__(self, parent=None):
        super(CommonWindow, self).__init__(parent)
        self.setupUi(self)


class PytodoList(PytodoMain, CommonWindow ):

    def __init__(self):
        self.originaltodolist = []
        self.formattodolist = []
        self.main_tree_checked = ''
        self.common_tree_checked = ''
        self.winmain = self.window_init_set(PytodoMain)
        self.wincommon = self.window_init_set(CommonWindow)
        self.timer3 = QTimer()
        self.timer_refresh_todo = QTimer()
        self.init_env()
        self.init_window()
        self.conn_event()

    def init_env(self):
        if not os.path.exists(JOB_PATH):
            os.mkdir(JOB_PATH)
        if not os.path.exists(JOB_COMMON):
            f = open(JOB_COMMON, 'a+', encoding='utf8')
            f.close()
        if not os.path.exists(JOB_DAY):
            f = open(JOB_DAY, 'a+', encoding='utf8')
            f.close()
        if not os.path.exists(JOB_WEEK):
            f = open(JOB_WEEK, 'a+', encoding='utf8')
            f.close()
        if not os.path.exists(JOB_MONTH):
            f = open(JOB_MONTH, 'a+', encoding='utf8')
            f.close()
        if not os.path.exists(self.get_history_filename()):
            f = open(self.get_history_filename(), 'a+', encoding='utf8')
            f.close()
        win32api.SetFileAttributes(JOB_PATH, win32con.FILE_ATTRIBUTE_HIDDEN)
        self.refresh_todolist()
        self.timer_refresh_todo.start(600000)

    def init_window(self):
        self.set_time(0)
        # 设置左侧样式
        self.winmain.left_widget.setStyleSheet('''background:gray;
        border-top-left-radius:10px;
        border-bottom-left-radius:10px;''')
        # 设置右侧样式
        self.winmain.right_widget.setStyleSheet('''
        color:#232C51;
        background:white;
        border-top:1px solid darkGray;
        border-bottom:1px solid darkGray;
        border-left:1px solid darkGray;
        border-right:1px solid darkGray;
        border-top-right-radius:10px;
        border-bottom-right-radius:10px;
        ''')
        # 左上角按钮效果
        self.winmain.btn_close.setStyleSheet(
            '''QPushButton{background:#F76677;border-radius:7px;}QPushButton:hover{background:red;}''')
        self.winmain.btn_about.setStyleSheet(
            '''QPushButton{background:#F7D674;border-radius:7px;}QPushButton:hover{background:yellow;}''')
        self.winmain.btn_mini.setStyleSheet(
            '''QPushButton{background:#6DDF6D;border-radius:7px;}QPushButton:hover{background:green;}''')
        self.wincommon.btn_close.setStyleSheet(
            '''QPushButton{background:#F76677;border-radius:7px;}QPushButton:hover{background:red;}''')
        self.wincommon.btn_mini.setStyleSheet(
            '''QPushButton{background:#6DDF6D;border-radius:7px;}QPushButton:hover{background:green;}''')

        self.winmain.btn_jjzy.setChecked(True)  # 设置紧急重要选中状态
        self.winmain.show()

    def window_init_set(self, window):
        self.win_name = window()
        self.win_name.setWindowFlags(Qt.FramelessWindowHint)  # 窗口类型为：无边框
        self.win_name.setFixedSize(self.win_name.width(), self.win_name.height())  # 禁止调整窗口大小
        icon = QIcon()
        icon.addPixmap(QPixmap(ICO_PATH), QIcon.Normal, QIcon.Off)
        self.win_name.setWindowIcon(icon)
        # self.win_name.setWindowOpacity(0.8) # 设置窗口透明度
        # self.win_name.setAttribute(Qt.WA_TranslucentBackground) # 设置背景透明度
        return self.win_name

    def set_time(self, add=None):
        '''设置时间'''
        NOW = QDateTime.currentDateTime()
        after = NOW.addDays(add)
        if add is None:
            self.winmain.choose_time.setDateTime(NOW)
        else:
            self.winmain.choose_time.setDateTime(after)

    def conn_event(self):
        '''按钮事件关联'''
        self.winmain.btn_close.clicked.connect(self.winmain.close)
        self.winmain.btn_about.clicked.connect(lambda: self.open_about())
        self.winmain.btn_mini.clicked.connect(lambda: self.window_change_mini(self.winmain))
        self.winmain.btn_time_tomorrow.clicked.connect(lambda: self.set_time(1))
        self.winmain.btn_time_7.clicked.connect(lambda: self.set_time(7))
        self.winmain.btn_time_14.clicked.connect(lambda: self.set_time(14))
        self.winmain.btn_time_30.clicked.connect(lambda: self.set_time(30))
        self.winmain.btn_add_todo.clicked.connect(lambda: self.btn_add_clicked())
        self.winmain.btn_day.clicked.connect(lambda: self.common_window_open(COMM_TITLE[0], COMB_DAY))
        self.winmain.btn_week.clicked.connect(lambda: self.common_window_open(COMM_TITLE[1], COMB_WEEK))
        self.winmain.btn_month.clicked.connect(lambda: self.common_window_open(COMM_TITLE[2], COMB_MONTH))
        self.winmain.btn_done.clicked.connect(lambda: self.btn_done_clicked())
        self.winmain.tree_lists.itemClicked.connect(lambda: self.main_tree_item_clicked())

        self.wincommon.btn_close.clicked.connect(self.wincommon.close)
        self.wincommon.btn_mini.clicked.connect(lambda: self.window_change_mini(self.wincommon))
        self.wincommon.btn_add.clicked.connect(lambda: self.common_job_add())
        self.wincommon.btn_minus.clicked.connect(lambda: self.common_job_remove())
        self.wincommon.tree_jobs.itemClicked.connect(lambda: self.common_tree_item_clicked())

        self.timer3.timeout.connect(lambda: self.tips_show_hide())
        self.timer_refresh_todo.timeout.connect(lambda: self.refresh_todolist())
        # self.btn_close.clicked.connect(self.close())

    def convert_tag(self):
        if self.winmain.btn_jjzy.isChecked():
            return 0
        if self.winmain.btn_jjbzy.isChecked():
            return 1
        if self.winmain.btn_zybjj.isChecked():
            return 2
        if self.winmain.btn_bzybjj.isChecked():
            return 3

    def get_uuid(self):
        return ''.join(str(uuid.uuid4()).split('-'))

    def tips_show_hide(self):
        if self.winmain.lbl_tips.isVisible():
            self.winmain.lbl_tips.setVisible(False)
        else:
            self.winmain.lbl_tips.setVisible(True)

    def set_tip_text(self, text=None):
        if text is None:
            self.winmain.lbl_tips.setText('^_^ 今 日 事 今 日 毕 ^_^')
            self.timer3.stop()
        else:
            self.winmain.lbl_tips.setText(text)
            self.timer3.start(1000)
            self.winmain.lbl_tips.setStyleSheet('''color:red;''')

    def window_change_mini(self, window):
        '''最小化'''
        window.setWindowState(Qt.WindowMinimized)

    def get_lines_form_file(self, filename):
        '''
        :param filename: 文件名
        :return: 返回文件内容
        '''
        with open(filename, 'r', encoding='utf8') as jd:
            all_lines = jd.readlines()
        return all_lines

    def write_to_file(self, filename, text, cover=False):
        '''
        :param filename: 文件
        :param text: 写入的内容
        :param cover: 是否清空重写
        :return:
        '''
        if cover:
            with open(filename, 'w') as jf:
                jf.write(text)
        else:
            with open(filename, 'a+', encoding='utf8') as jf:
                jf.write(text)
                jf.write('\n')

    def remove_file_item(self, filename, uuid):
        all_lines = self.get_lines_form_file(filename)
        i = 0
        while i < len(all_lines):
            if uuid in all_lines[i]:
                all_lines.pop(i)
            i += 1
        self.write_to_file(filename, '', True)
        for jobitem in all_lines:
            job_json = json.loads(jobitem)
            self.write_to_file(filename, json.dumps(job_json, ensure_ascii=False))

    def get_history_filename(self):
        YM = QDateTime.currentDateTime().toString('yyyyMM')
        job_history_fname = 'todo_history_' + YM + '.todo'
        JOB_HISTRORY = os.path.join(JOB_PATH, job_history_fname)
        return JOB_HISTRORY

    def main_tree_item_clicked(self):
        self.main_tree_checked = self.winmain.tree_lists.currentItem().toolTip(0)

    def common_tree_item_clicked(self):
        self.common_tree_checked = self.wincommon.tree_jobs.currentItem().toolTip(0)

    def convert_window_attr_filename(self):
        if self.wincommon.lbl_title.text() == '每日任务':
            return 1, JOB_DAY
        if self.wincommon.lbl_title.text() == '每周任务':
            return 2, JOB_WEEK
        if self.wincommon.lbl_title.text() == '每月任务':
            return 3, JOB_MONTH

    def common_window_open(self, title, combdata):
        self.wincommon.time_comb.clear()
        self.wincommon.lbl_title.setText(title)
        self.wincommon.time_comb.addItems(combdata)
        attr, filename = self.convert_window_attr_filename()
        self.common_refresh_tree(filename)
        self.wincommon.show()
        self.wincommon.activateWindow()

    def common_job_add(self):
        attr, filename = self.convert_window_attr_filename()
        if self.wincommon.job_text.toPlainText().strip() == '':
            self.set_tip_text('提示：待办不能为空！')
        else:
            if len(self.wincommon.job_text.toPlainText().strip()) > 64:
                self.set_tip_text('提示：待办不能超过64个字符')
            else:
                todo_item = {
                    'time': self.wincommon.time_comb.currentText(),
                    'tag': 0,
                    'jobattr': attr,  # 0普通任务 1每日任务 2每周任务 3每月任务
                    'job': self.wincommon.job_text.toPlainText().strip(),
                    'doneflag': False,
                    'donetime': '',
                    'uuid': self.get_uuid()
                }
                self.write_to_file(filename, json.dumps(todo_item, ensure_ascii=False))
                self.set_tip_text()
                self.wincommon.job_text.clear()
                self.common_refresh_tree(filename)

    def common_refresh_tree(self, filename):
        self.wincommon.tree_jobs.clear()
        self.wincommon.tree_jobs.setColumnCount(1)
        self.wincommon.tree_jobs.setColumnWidth(0, 400)
        self.wincommon.tree_jobs.setHeaderLabels(['(提醒时间_待办工作)'])
        # 添加四个一级节点
        day_todo = self.get_lines_form_file(filename)
        for jobitem in day_todo:
            job_json = json.loads(jobitem)
            job_uuid = job_json['uuid']
            job_text = job_json['time'] + '_' + job_json['job']
            root = QTreeWidgetItem(self.wincommon.tree_jobs)
            root.setText(0, job_text)
            root.setToolTip(0, job_uuid)

    def common_job_remove(self):
        attr, filename = self.convert_window_attr_filename()
        if self.wincommon.tree_jobs == '':
            self.set_tip_text('请选择正确的待办事项')
        else:
            self.remove_file_item(filename, self.common_tree_checked)
            self.common_refresh_tree(filename)
            self.set_tip_text()
            self.common_tree_checked = ''

    def btn_add_clicked(self):
        if self.winmain.text_todo.toPlainText().strip() == '':
            self.set_tip_text('提示：待办不能为空！')
        else:
            if len(self.winmain.text_todo.toPlainText().strip()) > 64:
                self.set_tip_text('提示：待办不能超过64个字符')
            else:
                self.set_tip_text()
                job_item = self.format_text()
                self.write_to_file(JOB_COMMON, job_item)
                self.refresh_todolist()
                self.winmain.text_todo.clear()

    def btn_done_clicked(self):
        if self.main_tree_checked == '' or self.winmain.tree_lists.currentItem().parent().text(0) == '今日完成':
            self.set_tip_text('请选择正确的待办事项')
        else:
            choose_job = self.winmain.tree_lists.currentItem().text(0)
            if choose_job in ['紧急重要', '紧急不重要', '重要不紧急', '不紧急不重要', '今日完成']:
                self.set_tip_text('请选择正确的待办事项')
            else:
                self.change_done_status(self.main_tree_checked)
                self.set_tip_text()
                self.main_tree_checked = ''

    def get_today_done(self):
        TODAY = QDateTime.currentDateTime().toString('yyyy-MM-dd')
        JOB_HISTORY = self.get_history_filename()
        today_all_lines = self.get_lines_form_file(JOB_HISTORY)
        today_done_list = []
        for jobitem in today_all_lines:
            if TODAY in jobitem:
                today_done_list.append(json.loads(jobitem))
        return today_done_list

    def check_job_status(self, uuid):
        TODAY = QDateTime.currentDateTime().toString('yyyy-MM-dd')
        todo_lines = self.get_lines_form_file(self.get_history_filename())
        for jobitem in todo_lines:
            job_json = json.loads(jobitem)
            if job_json['uuid'] == uuid and TODAY in job_json['donetime']:
                return False

        todo_lines = self.get_lines_form_file(JOB_COMMON)
        for jobitem in todo_lines:
            job_json = json.loads(jobitem)
            if job_json['uuid'] == uuid:
                return False

        return True

    def get_day_todo(self):
        todo_lines = self.get_lines_form_file(JOB_DAY)
        for jobitem in todo_lines:
            job_json = json.loads(jobitem)
            job_uuid = job_json['uuid']
            if self.check_job_status(job_uuid):
                self.write_to_file(JOB_COMMON, json.dumps(job_json, ensure_ascii=False))

    def get_week_todo(self):
        week_list = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        week_index = datetime.datetime.now().weekday()
        week = week_list[week_index]
        todo_lines = self.get_lines_form_file(JOB_WEEK)
        for jobitem in todo_lines:
            job_json = json.loads(jobitem)
            job_uuid = job_json['uuid']
            job_time = job_json['time']
            if job_time != week:
                continue
            if self.check_job_status(job_uuid):
                self.write_to_file(JOB_COMMON, json.dumps(job_json, ensure_ascii=False))

    def get_month_todo(self):
        today = QDateTime.currentDateTime().toString('d号')
        todo_lines = self.get_lines_form_file(JOB_MONTH)
        for jobitem in todo_lines:
            job_json = json.loads(jobitem)
            job_uuid = job_json['uuid']
            job_time = job_json['time']
            if job_time != today:
                continue
            if self.check_job_status(job_uuid):
                self.write_to_file(JOB_COMMON, json.dumps(job_json, ensure_ascii=False))

    def refresh_todolist(self):
        tmp_list = []
        self.get_day_todo()
        self.get_week_todo()
        self.get_month_todo()
        todo_lines = self.get_lines_form_file(JOB_COMMON)
        for line in todo_lines:
            tmp_list.append(json.loads(line))
        # 根据tag排序，再根据 time排序
        todo_lists = sorted(tmp_list, key=lambda e:(e.__getitem__('tag'), e.__getitem__('time')))
        todo_lists.extend(self.get_today_done())
        self.show_in_tree(todo_lists)

    def show_in_tree(self, lists):
        self.winmain.tree_lists.clear()
        self.winmain.tree_lists.setColumnCount(1)
        self.winmain.tree_lists.setColumnWidth(0, 800)
        self.winmain.tree_lists.setHeaderLabels(['待办事项(期望完成时间_待办工作)'])
        # 添加四个一级节点
        root0 = QTreeWidgetItem(self.winmain.tree_lists)
        root0.setText(0,'紧急重要')
        root1 = QTreeWidgetItem(self.winmain.tree_lists)
        root1.setText(0, '紧急不重要')
        root2 = QTreeWidgetItem(self.winmain.tree_lists)
        root2.setText(0, '重要不紧急')
        root3 = QTreeWidgetItem(self.winmain.tree_lists)
        root3.setText(0, '不紧急不重要')
        root4 = QTreeWidgetItem(self.winmain.tree_lists)
        root4.setText(0, '今日完成')

        if not lists:
            self.set_tip_text('真棒，今天没有待完成任务')

        for jobitem in lists:
            job_text = jobitem['time'] + '_' + jobitem['job']
            job_uuid = jobitem['uuid']
            if jobitem['doneflag']:
                tree_child = QTreeWidgetItem(root4)
                tree_child.setText(0, job_text)
                tree_child.setToolTip(0, job_uuid)
                # tree_child.setDisabled(True)
                continue
            if jobitem['tag'] == 0:
                tree_child = QTreeWidgetItem(root0)
                tree_child.setText(0, job_text)
                tree_child.setToolTip(0, job_uuid)
                continue
            if jobitem['tag'] == 1:
                tree_child = QTreeWidgetItem(root1)
                tree_child.setText(0, job_text)
                tree_child.setToolTip(0, job_uuid)
                continue
            if jobitem['tag'] == 2:
                tree_child = QTreeWidgetItem(root2)
                tree_child.setText(0, job_text)
                tree_child.setToolTip(0, job_uuid)
                continue
            if jobitem['tag'] == 3:
                tree_child = QTreeWidgetItem(root3)
                tree_child.setText(0, job_text)
                tree_child.setToolTip(0, job_uuid)
                continue

        self.winmain.tree_lists.addTopLevelItem(root0)
        self.winmain.tree_lists.expandAll()

    def format_text(self):
            todo_item = {
                'time': self.winmain.choose_time.dateTime().toString('yyyy-MM-dd HH:mm'),
                'tag': self.convert_tag(),
                'jobattr': 0,  # 0普通任务 1每日任务 2每周任务 3每月任务
                'job': self.winmain.text_todo.toPlainText().strip(),
                'doneflag': False,
                'donetime': '',
                'uuid': self.get_uuid()
            }
            return json.dumps(todo_item, ensure_ascii=False)

    def write_to_history(self, text):
        JOB_HISTRORY = self.get_history_filename()
        self.write_to_file(JOB_HISTRORY, text)

    def change_done_status(self, uuid):
        todo_lines = self.get_lines_form_file(JOB_COMMON)
        NOW = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        i = 0
        while i < len(todo_lines):
            # print(todo_lines[i])
            job_json = json.loads(todo_lines[i])
            job_new_status = json.loads(todo_lines[i])
            if uuid == job_json['uuid']:
                job_new_status['doneflag'] = True
                job_new_status['donetime'] = NOW
                self.write_to_history(json.dumps(job_new_status, ensure_ascii=False))
            i += 1
        self.remove_file_item(JOB_COMMON, uuid)
        self.refresh_todolist()

    def open_about(self):
        '''打开软件介绍'''
        url = 'https://www.github.com/chaoxiaodi/pytodolist'
        webbrowser.open(url, new=0, autoraise=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = PytodoList()
    sys.exit(app.exec())
