import os  # 导入os模块，用于处理文件和目录操作
import json  # 导入json模块，用于处理JSON数据的读取和写入
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem  # 从PyQt6导入所需的UI组件
)

class WorkViewingUI(QWidget):  # 定义一个继承自QWidget的类WorkViewingUI
    def __init__(self):  # 初始化函数
        super().__init__()  # 调用父类的初始化函数
        self.init_ui()  # 调用初始化UI界面的方法

    def init_ui(self):  # 初始化UI界面的方法
        layout = QVBoxLayout()  # 创建一个垂直布局管理器
        self.setLayout(layout)  # 设置当前窗口的布局为垂直布局

        # 创建标题标签，显示"Work Viewing"
        self.title_label = QLabel("Work Viewing")
        layout.addWidget(self.title_label)  # 将标题标签添加到布局中

        # 创建表格，用于显示作品信息
        self.work_table = QTableWidget()  # 创建一个QTableWidget控件
        self.work_table.setColumnCount(3)  # 设置表格的列数为3
        self.work_table.setHorizontalHeaderLabels(["Name", "Status", "Published Date"])  # 设置表头标签
        layout.addWidget(self.work_table)  # 将表格控件添加到布局中

        # 调用加载作品数据的方法
        self.load_works()

    def load_works(self):  # 加载作品数据的方法
        works_path = os.path.join("works")  # 定义作品文件夹路径
        if not os.path.exists(works_path):  # 如果该路径不存在
            self.work_table.setRowCount(0)  # 设置表格行数为0，清空表格
            return  # 退出方法

        works = []  # 创建一个空列表，用于存储读取到的作品数据
        for file in os.listdir(works_path):  # 遍历目录中的所有文件
            if file.endswith(".json"):  # 如果文件是以.json结尾的
                with open(os.path.join(works_path, file), "r") as f:  # 打开文件进行读取
                    try:
                        work_data = json.load(f)  # 尝试将文件内容解析为JSON格式
                        works.append(work_data)  # 如果解析成功，将数据添加到works列表中
                    except json.JSONDecodeError:  # 如果解析失败，忽略该文件
                        pass

        self.work_table.setRowCount(len(works))  # 设置表格的行数为作品数量
        for row, work in enumerate(works):  # 遍历每个作品数据
            name = work.get("name", "Unknown")  # 获取作品名称，如果没有则默认值为"Unknown"
            status = work.get("status", "Unknown")  # 获取作品状态，如果没有则默认值为"Unknown"
            published_date = work.get("published_date", "Unknown")  # 获取作品发布日期，如果没有则默认值为"Unknown"

            # 将作品的名称、状态和发布日期分别显示在表格的对应单元格中
            self.work_table.setItem(row, 0, QTableWidgetItem(name))  # 设置第row行第0列的单元格为作品名称
            self.work_table.setItem(row, 1, QTableWidgetItem(status))  # 设置第row行第1列的单元格为作品状态
            self.work_table.setItem(row, 2, QTableWidgetItem(published_date))  # 设置第row行第2列的单元格为作品发布日期
