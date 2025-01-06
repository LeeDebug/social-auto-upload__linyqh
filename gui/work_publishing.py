import os  # 导入os模块，用于文件和目录操作
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QDateTimeEdit, QHBoxLayout  # 导入PyQt6中的UI组件
)
from PyQt6.QtCore import QDateTime  # 导入QDateTime类，用于日期和时间的处理

class WorkPublishingUI(QWidget):  # 定义一个继承自QWidget的类WorkPublishingUI
    def __init__(self):  # 初始化函数
        super().__init__()  # 调用父类的初始化函数
        self.init_ui()  # 调用初始化UI界面的函数

    def init_ui(self):  # 初始化UI界面的函数
        layout = QVBoxLayout()  # 创建一个垂直布局管理器
        self.setLayout(layout)  # 设置当前窗口的布局为垂直布局

        # 创建标题标签，显示"Work Publishing"
        self.title_label = QLabel("Work Publishing")
        layout.addWidget(self.title_label)  # 将标题标签添加到布局中

        # 创建一个按钮，用于选择目录
        self.select_dir_button = QPushButton("Select Directory")
        self.select_dir_button.clicked.connect(self.select_directory)  # 点击按钮时连接到select_directory方法
        layout.addWidget(self.select_dir_button)  # 将选择目录按钮添加到布局中

        # 创建一个表格，用于显示MP4文件信息
        self.work_table = QTableWidget()  # 创建QTableWidget表格控件
        self.work_table.setColumnCount(3)  # 设置表格的列数为3
        self.work_table.setHorizontalHeaderLabels(["File Name", "Path", "Publish Time"])  # 设置表头
        layout.addWidget(self.work_table)  # 将表格控件添加到布局中

    def select_directory(self):  # 选择目录的方法
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")  # 弹出选择目录对话框
        if directory:  # 如果选择了目录
            self.load_mp4_files(directory)  # 调用load_mp4_files方法加载目录中的MP4文件

    def load_mp4_files(self, directory):  # 加载MP4文件的方法
        mp4_files = []  # 创建一个空列表，用于存储MP4文件的路径
        for root, _, files in os.walk(directory):  # 遍历目录及其子目录中的文件
            for file in files:  # 遍历每个文件
                if file.endswith(".mp4"):  # 如果文件是MP4格式
                    mp4_files.append(os.path.join(root, file))  # 将文件的完整路径添加到mp4_files列表中

        # 设置表格的行数为MP4文件的数量
        self.work_table.setRowCount(len(mp4_files))
        for row, file_path in enumerate(mp4_files):  # 遍历每个MP4文件的路径
            file_name = os.path.basename(file_path)  # 获取文件名（去掉路径）

            # 在表格的第row行第0列设置文件名
            self.work_table.setItem(row, 0, QTableWidgetItem(file_name))

            # 在表格的第row行第1列设置文件的完整路径
            self.work_table.setItem(row, 1, QTableWidgetItem(file_path))

            # 在表格的第row行第2列设置一个QDateTimeEdit控件，允许用户选择发布日期
            date_time_edit = QDateTimeEdit()  # 创建QDateTimeEdit控件
            date_time_edit.setCalendarPopup(True)  # 设置控件支持弹出日历
            date_time_edit.setDateTime(QDateTime.currentDateTime())  # 设置当前日期和时间为默认值
            self.work_table.setCellWidget(row, 2, date_time_edit)  # 将QDateTimeEdit控件设置到表格的指定单元格
