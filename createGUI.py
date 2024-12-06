import json
import os
import sys
from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QInputDialog,
    QFileDialog, QMessageBox, QTableWidgetItem, QTableWidget, QDialog
)

from ACsearch import book
from examGUI import Exam
from makeSchedule import generate
from resetList import reset


class TaskStatusDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('任务状态')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # 创建表格以显示任务列表
        self.task_table = QTableWidget(self)
        self.task_table.setColumnCount(4)
        self.task_table.setHorizontalHeaderLabels(['任务数', '任务内容', '状态', '完成时间'])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 禁止编辑
        layout.addWidget(self.task_table)

        # 继续学习按钮
        self.continue_btn = QPushButton('继续学习', self)
        self.continue_btn.clicked.connect(self.on_continue)
        layout.addWidget(self.continue_btn)

        # 退出学习按钮
        self.exit_btn = QPushButton('退出学习', self)
        self.exit_btn.clicked.connect(self.on_exit)
        layout.addWidget(self.exit_btn)

        self.setLayout(layout)

        self.load_tasks()

    def load_tasks(self):
        if not os.path.exists('schedule.json'):
            QMessageBox.information(self, "提示", "暂未制定学习计划")
            self.reject()
            return

        with open('schedule.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.today_tasks = []
        self.current_day_info = None

        for day_info in data:
            for task in day_info['task']:
                if task['finish'] == '0':
                    self.current_day_info = day_info
                    break
            if self.current_day_info:
                break

        if not self.current_day_info:
            QMessageBox.information(self, "提示", "所有任务都已完成！")
            self.accept()
            return

        QMessageBox.information(self, "提示", f"今天是第{self.current_day_info['day']}天学习，当天的任务列表如下：")
        row_count = 0
        self.task_table.setRowCount(0)
        for task in self.current_day_info['task']:
            self.today_tasks.append(task)
            self.task_table.insertRow(row_count)
            self.task_table.setItem(row_count, 0, QTableWidgetItem(str(self.current_day_info['day'])))
            self.task_table.setItem(row_count, 1, QTableWidgetItem(f"{task['type']}_{task['num']}"))
            finish_temp = "已完成" if task['finish'] != '0' else "待完成"
            self.task_table.setItem(row_count, 2, QTableWidgetItem(finish_temp))
            self.task_table.setItem(row_count, 3, QTableWidgetItem(task.get('finish', '')))
            row_count += 1

    def on_continue(self):
        selected_row = self.task_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "警告", "请选择一个任务开始")
            return
        task = self.today_tasks[selected_row]
        file_path = f"{task['type']}/day_{task['num']}.json"
        if not os.path.exists(file_path):
            QMessageBox.information(self, "警告", "该目录不存在")
            return
        if os.path.getsize(file_path) == 0:
            QMessageBox.information(self, "警告", "该目录为空")
            return
        Exam('list', task['num'], self.on_examine_finished)

    def on_exit(self):
        # 弹出确认退出的消息框
        reply = QMessageBox.question(self, "确认退出", "确定要退出学习吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.reject()  # 退出当前对话框

    def on_examine_finished(self, exam_completed):
        selected_row = self.task_table.currentRow()
        task = self.today_tasks[selected_row]
        if exam_completed:
            task['finish'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.task_table.setItem(selected_row, 2, QTableWidgetItem("已完成"))
            self.task_table.setItem(selected_row, 3, QTableWidgetItem(task['finish']))
            QMessageBox.information(self, "完成",
                                    f'您在{task["finish"]}时刻完成了{task["type"]}_{task["num"]}的学习任务')

            with open('schedule.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            for day_info in data:
                if day_info['day'] == self.current_day_info['day']:
                    for t in day_info['task']:
                        if t['type'] == task['type'] and t['num'] == task['num']:
                            t['finish'] = task['finish']
                            break
            with open('schedule.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            all_completed = all(t['finish'] != '0' for t in self.today_tasks)
            if all_completed:
                QMessageBox.information(self, "提示", "今天的所有任务都已完成！")
                self.accept()
            else:
                choice = QMessageBox.question(self, '确认继续', '是否继续学习？',
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                              QMessageBox.StandardButton.No)
                if choice == QMessageBox.StandardButton.Yes:
                    self.load_tasks()
                else:
                    self.accept()
        else:
            QMessageBox.information(self, "退出", "您选择了退出测试")


class LearnApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('学习助手')
        self.setGeometry(100, 100, 400, 300)
        main_layout = QVBoxLayout()
        title_label = QLabel("欢迎使用词汇考察工具", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(16)
        title_label.setFont(font)
        main_layout.addWidget(title_label)
        button_layout = QHBoxLayout()
        buttons = [
            ('按进度继续学习', self.on_continue),
            ('自定义练习', self.on_custom),
            ('导入词书', self.on_import),
            ('制定学习计划', self.on_plan),
            ('重置单词列表', self.on_reset),
            ('退出学习', self.on_exit)
        ]
        for text, callback in buttons:
            btn = QPushButton(text, self)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def on_continue(self):
        dialog = TaskStatusDialog()
        dialog.exec()

    def on_examine_finished(self, exam_completed):
        if exam_completed:
            times = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            QMessageBox.information(self, "完成",
                                    f'您在{times}时刻完成了{self.exam_types}_{self.progresses}的自学任务')
        else:
            QMessageBox.information(self, "退出", "您选择了退出测试")

    def on_custom(self):
        self.exam_types, ok = QInputDialog.getItem(
            self, "选择复习类型", "请输入要复习的类型：", ["词表", "错词本", "熟知词"], 0, False)
        if self.exam_types == "词表":
            self.exam_types = 'list'
        elif self.exam_types == "错词本":
            self.exam_types = 'wrong'
        elif self.exam_types == "熟知词":
            self.exam_types = 'known'
        if ok and self.exam_types:
            self.progresses, ok = QInputDialog.getInt(self, "输入进度", "请输入要复习的进度：", min=1)
            if ok and self.progresses:
                file_path = f"{self.exam_types}/day_{self.progresses}.json"
                if not os.path.exists(file_path):
                    QMessageBox.information(self, "警告", "该目录不存在")
                    return
                if os.path.getsize(file_path) == 0:
                    QMessageBox.information(self, "警告", "该目录为空")
                    return
                Exam(self.exam_types, self.progresses, self.on_examine_finished)

    def on_import(self):
        # 提示用户导入词书会覆盖原有进度
        reply = QMessageBox.question(self, "警告", "注意，导入词书会覆盖原有学习进度，是否继续？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return  # 如果用户选择“否”，则直接返回，不执行后续操作

        # 用户选择“是”继续导入词书
        name, _ = QFileDialog.getOpenFileName(self, '选择词书文件', '', '所有文件 (*)')
        content = []
        if name:
            # 获取词书的文件名
            content = book(name)

        # 显示词书内容或错误提示
        if content:
            QMessageBox.information(self, content[0], content[1])
        else:
            QMessageBox.warning(self, "错误", "无法导入词书，内容为空或格式不正确。")

    def on_plan(self):
        # 提示用户导入词书会覆盖原有进度
        reply = QMessageBox.question(self, "警告", "注意，重新制定学习计划会覆盖原有学习进度，是否继续？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return  # 如果用户选择“否”，则直接返回，不执行后续操作

        # 获取用户输入的学习数量
        numbers, ok1 = QInputDialog.getText(self, "输入学习数量", "请输入间隔几天复习，用英文逗号隔开")
        if not ok1:
            return  # 如果用户取消输入，则直接返回
        # 将输入的数字字符串转换为整数列表
        numbers = [int(i) for i in numbers.split(',')]
        if ok1:
            review = ['list'] * len(numbers)
            content = generate(numbers, review)  # 假设 generate 是你定义的函数
            QMessageBox.information(self, content[0], content[1])

    def on_reset(self):
        progress, ok = QInputDialog.getInt(self, "输入进度", "请输入要重置的进度：", min=1)

        if ok and progress:
            reply = QMessageBox.question(self, "确认重置", "您确定要重置进度吗？",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
            content = reset(progress)  # 假设 reset 函数会处理重置进度的逻辑
            QMessageBox.information(self, content[0], content[1])

    def on_exit(self):
        reply = QMessageBox.question(self, '确认退出', '你确定要退出吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "提示", "感谢使用，再见")
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    learn_app = LearnApp()
    learn_app.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
