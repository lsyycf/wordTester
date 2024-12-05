import random
import json

from PyQt6.QtCore import Qt

from getExam import get_random_word, merge_json
from resetList import load_dictionary, get_all_list
from PyQt6.QtWidgets import (
    QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QMessageBox, QTableWidgetItem, QTableWidget, QDialog, QAbstractItemView
)


class WordQuestionGUI(QDialog):
    def __init__(self, random_word, random_meaning, question_num, update_counts_callback, set_break_loop):
        super().__init__()
        self.random_word = random_word
        self.random_meaning = random_meaning
        self.question_num = question_num
        self.update_counts_callback = update_counts_callback
        self.set_break_loop = set_break_loop
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"问题 {self.question_num}")
        self.setGeometry(100, 100, 400, 200)

        # 设置布局
        layout = QVBoxLayout()

        # 问题标签
        self.question_label = QLabel(f"{self.question_num}. 请写出 '{self.random_meaning}' 的英文单词：")
        layout.addWidget(self.question_label)

        # 输入框
        self.answer_input = QLineEdit(self)
        self.answer_input.setPlaceholderText("输入答案")
        layout.addWidget(self.answer_input)

        # 提交按钮
        self.check_button = QPushButton("提交答案", self)
        self.check_button.clicked.connect(self.check_answer)
        layout.addWidget(self.check_button)

        # 标记熟知按钮
        self.known_button = QPushButton("熟知词", self)
        self.known_button.clicked.connect(self.mark_known)
        layout.addWidget(self.known_button)

        # 退出按钮
        self.exit_button = QPushButton("退出测试", self)
        self.exit_button.clicked.connect(self.exit_test)
        layout.addWidget(self.exit_button)

        # 设置布局
        self.setLayout(layout)

    def check_answer(self):
        user_answer = self.answer_input.text().strip()
        if user_answer.lower() == self.random_word["word"].lower():
            result = "正确"
            QMessageBox.information(self, "结果", "正确")
        elif user_answer == '!':
            result = "熟知"
            QMessageBox.information(self, "结果", "已加入熟知词")
        else:
            result = "错误"
            QMessageBox.warning(self, "结果", f"错误，正确答案是：{self.random_word['word']}")

        self.update_counts_callback(1, result, self.random_word["index"])
        self.accept()  # 关闭对话框

    def mark_known(self):
        result = "熟知"
        QMessageBox.information(self, "结果", "已加入熟知词")
        self.update_counts_callback(1, result, self.random_word["index"])
        self.accept()  # 关闭对话框

    def exit_test(self):
        """退出测试并关闭窗口"""
        exit_reply = QMessageBox.question(self, '退出测试', '确定要退出测试吗？',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if exit_reply == QMessageBox.StandardButton.Yes:
            self.set_break_loop()  # 调用回调函数来中断测试
            self.reject()  # 关闭对话框


class MultipleChoiceGUI(QDialog):
    def __init__(self, random_word, options, correct_answer, question_num, update_counts_callback, set_break_loop):
        super().__init__()
        self.random_word = random_word
        self.options = options
        self.correct_answer = correct_answer
        self.question_num = question_num
        self.update_counts_callback = update_counts_callback
        self.set_break_loop = set_break_loop
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"问题 {self.question_num}")
        self.setGeometry(100, 100, 400, 300)

        # 创建垂直布局
        layout = QVBoxLayout()

        # 显示问题标签
        self.question_label = QLabel(f"{self.question_num}. {self.random_word['word']} 的意思是以下哪一个选项：")
        layout.addWidget(self.question_label)

        # 添加选项按钮
        self.option_buttons = []
        for i, option in enumerate(self.options):
            button = QPushButton(f"{chr(ord('A') + i)}. {option}", self)
            button.clicked.connect(lambda checked, index=i: self.on_option_click(index))
            layout.addWidget(button)
            self.option_buttons.append(button)

        # 添加退出按钮
        exit_button = QPushButton("退出测试", self)
        exit_button.clicked.connect(self.exit_test)
        layout.addWidget(exit_button)

        self.setLayout(layout)

    def on_option_click(self, index):
        selected_answer = chr(ord('A') + index)
        if selected_answer.lower() == self.correct_answer.lower():
            result = "正确"
            QMessageBox.information(self, "结果", "正确")
        elif selected_answer == '!':
            result = "熟知"
            QMessageBox.information(self, "结果", "已加入熟知词")
        else:
            result = "错误"
            QMessageBox.warning(self, "结果", f"错误，正确答案是：{self.correct_answer}")
        self.update_counts_callback(2, result, self.random_word["index"])
        self.accept()  # 关闭对话框

    def exit_test(self):
        """退出测试并关闭窗口"""
        exit_reply = QMessageBox.question(self, '退出测试', '确定要退出测试吗？',
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if exit_reply == QMessageBox.StandardButton.Yes:
            self.set_break_loop()
            self.reject()  # 关闭对话框


class ExamStartGUI(QDialog):
    def __init__(self, word_list, set_break_loop):
        super().__init__()
        self.word_list = word_list
        self.set_break_loop = set_break_loop
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("开始学习")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()
        self.label = QLabel("以下是本次学习的单词信息：", self)
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["单词", "音标", "释义", "错误次数"])
        self.table_widget.setRowCount(len(self.word_list))

        for row, word in enumerate(self.word_list):
            self.table_widget.setItem(row, 0, QTableWidgetItem(word["word"]))
            self.table_widget.setItem(row, 1, QTableWidgetItem(word["phonetic"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(word["meanings"].replace("\n", "")))
            self.table_widget.setItem(row, 3, QTableWidgetItem(str(word["wrong"])))
            for col in range(4):
                item = self.table_widget.item(row, col)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # 禁用编辑

        self.test__button = QPushButton("开始测试", self)
        self.test__button.clicked.connect(self.test_words)
        self.exit_button = QPushButton("退出测试", self)
        self.exit_button.clicked.connect(self.exit_test)

        layout.addWidget(self.label)
        layout.addWidget(self.table_widget)
        layout.addWidget(self.test__button)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def test_words(self):
        reply = QMessageBox.question(self, '开始测试', '确定要开始测试吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.accept()

    def exit_test(self):
        reply = QMessageBox.question(self, '退出学习', '确定要退出学习吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.set_break_loop()
            self.reject()


class ExamCompletionGUI(QDialog):
    def __init__(self, wrong_index_list, word_list, set_break_loop, reset_exam):
        super().__init__()
        self.wrong_index_list = wrong_index_list
        self.word_list = word_list
        self.set_break_loop = set_break_loop
        self.reset_exam = reset_exam
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("测试完成")
        self.setGeometry(100, 100, 600, 400)

        # 布局
        layout = QVBoxLayout()

        if not self.wrong_index_list:
            # 如果没有错题，显示恭喜信息和完成测试按钮
            self.label = QLabel("恭喜你，全部答对啦！", self)
            self.complete_button = QPushButton("完成测试", self)
            self.complete_button.clicked.connect(self.complete_test)
            layout.addWidget(self.label)
            layout.addWidget(self.complete_button)
        else:
            # 如果有错题，显示错题表格
            self.label = QLabel("以下是本次答错的单词信息：", self)
            self.table_widget = QTableWidget(self)
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(["单词", "音标", "释义"])

            # 填充错题表格
            self.table_widget.setRowCount(len(self.wrong_index_list))
            for row, index in enumerate(self.wrong_index_list):
                word = self.word_list[index]
                self.table_widget.setItem(row, 0, QTableWidgetItem(word["word"]))
                self.table_widget.setItem(row, 1, QTableWidgetItem(word["phonetic"]))
                self.table_widget.setItem(row, 2, QTableWidgetItem(word["meanings"].replace("\n", "")))
                for col in range(3):
                    item = self.table_widget.item(row, col)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self.test_wrong_button = QPushButton("测试错题", self)
            self.test_wrong_button.clicked.connect(self.test_wrong_words)
            self.exit_button = QPushButton("退出测试", self)
            self.exit_button.clicked.connect(self.exit_test)

            layout.addWidget(self.label)
            layout.addWidget(self.table_widget)
            layout.addWidget(self.test_wrong_button)
            layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def test_wrong_words(self):
        self.reset_exam(self.wrong_index_list)
        self.accept()  # 关闭对话框并返回

    def exit_test(self):
        reply = QMessageBox.question(self, '退出测试', '确定要退出测试吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.set_break_loop()
            self.reject()  # 关闭对话框并返回拒绝（退出）

    def complete_test(self):
        self.set_break_loop()
        self.accept()  # 正常完成测试，关闭对话框


class Exam:
    def __init__(self, exam_type, day, on_finished):
        self.exam_type = exam_type
        self.day = day
        self.file_path = f"{exam_type}/day_{day}.json"
        self.word_list = []
        self.all_list = []
        self.known_index_list = []
        self.wrong_index_list = []
        self.used_index_list1 = []
        self.used_index_list2 = []
        self.question_type_1_count = 0
        self.question_type_2_count = 0
        self.question_count = 0
        self.break_loop = 0
        self.on_finished = on_finished
        self.init_exam()

    def init_exam(self):
        self.word_list = load_dictionary(self.file_path)
        self.all_list = get_all_list(self.day)
        self.question_type_1_count = len(self.word_list)
        self.question_type_2_count = self.question_type_1_count
        self.question_count = self.question_type_1_count * 2
        self.start_exam()

    def set_break_loop(self):
        self.break_loop = 1

    def start_exam(self):
        start = ExamStartGUI(self.word_list, self.set_break_loop)
        start.exec()
        if self.break_loop == 1:
            self.on_finished(False)
            return
        flag = 0
        while True:
            while self.question_count > 0:
                question_type = random.choice([1, 2])
                if (question_type == 1 and self.question_type_1_count > 0) or (
                        question_type == 2 and self.question_type_2_count == 0):
                    self.generate_question_1()
                elif (question_type == 2 and self.question_type_2_count > 0) or (
                        question_type == 1 and self.question_type_1_count == 0):
                    self.generate_question_2()
                if self.break_loop == 1:
                    if flag == 0:
                        self.on_finished(False)
                    else:
                        self.on_finished(True)
                    return
            self.handle_exam_results()
            flag = 1
            if self.break_loop == 1:
                self.on_finished(True)
                return

    def generate_question_1(self):
        random_word = get_random_word(self.word_list, self.used_index_list1, self.known_index_list)
        random_meaning = random_word["meanings"].replace("\n", "")
        question_num = len(self.used_index_list1) + len(self.used_index_list2) + 1
        window = WordQuestionGUI(random_word, random_meaning, question_num, self.update_counts, self.set_break_loop)
        window.exec()

    def generate_question_2(self):
        random_word = get_random_word(self.word_list, self.used_index_list2, self.known_index_list)
        correct_meaning = random_word["meanings"].replace("\n", "")
        options = [correct_meaning]
        list_temp = [word for word in self.all_list if word["index"] != random_word["index"]]
        random_list = random.sample(list_temp, 3)
        options += [word["meanings"].replace("\n", "") for word in random_list]
        random.shuffle(options)
        correct_index = options.index(correct_meaning)
        correct_answer = chr(ord('A') + correct_index)
        question_num = len(self.used_index_list1) + len(self.used_index_list2) + 1
        window = MultipleChoiceGUI(random_word, options, correct_answer, question_num,
                                   self.update_counts, self.set_break_loop)
        window.exec()

    def handle_exam_results(self):
        if self.known_index_list and self.exam_type != 'known':
            self.word_list = [word for word in self.word_list if word["index"] not in self.known_index_list]
            merge_json("known", self.day, self.known_index_list, self.all_list)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.word_list, ensure_ascii=False, indent=2))
        self.wrong_index_list = sorted(list(set(self.wrong_index_list)))
        self.word_list = [word for word in self.word_list if word["index"] in self.wrong_index_list]
        path_temp = "list" if self.exam_type == "wrong" else "wrong"
        merge_json(path_temp, self.day, self.wrong_index_list, self.all_list)
        window = ExamCompletionGUI(self.wrong_index_list, self.all_list, self.set_break_loop, self.reset_exam)
        window.exec()

    def update_counts(self, question_type, result, index):
        if question_type == 1:
            self.question_type_1_count -= 1
            self.used_index_list1.append(index)
        else:
            self.question_type_2_count -= 1
            self.used_index_list2.append(index)
        self.question_count -= 1
        self.update_word_info(index, result)
        if result == "错误":
            self.wrong_index_list.append(index)
        elif result == "熟知" and self.exam_type != 'known':
            self.known_index_list.append(index)

    def update_word_info(self, index, result):
        for word in self.word_list:
            if word["index"] == index:
                if result == "错误":
                    word['wrong'] += 1
                break
        for word in self.all_list:
            if word["index"] == index:
                if result == "错误":
                    word['wrong'] += 1
                break

    def reset_exam(self, wrong_index_list):
        self.question_type_1_count = len(wrong_index_list)
        self.question_type_2_count = self.question_type_1_count
        self.question_count = self.question_type_1_count * 2
        self.used_index_list1 = []
        self.used_index_list2 = []
        self.wrong_index_list = []
