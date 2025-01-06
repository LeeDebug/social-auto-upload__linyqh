import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
)

class AccountManagementUI(QWidget):
    def __init__(self):
        super().__init__()  # 初始化父类 QWidget
        self.init_ui()  # 调用初始化界面方法

    def init_ui(self):
        """
        初始化用户界面，设置布局和控件
        """
        layout = QVBoxLayout()  # 创建一个垂直布局
        self.setLayout(layout)  # 设置当前窗口的布局

        # 平台选择下拉框
        self.platform_label = QLabel("Select Platform:")  # 创建标签，提示用户选择平台
        self.platform_dropdown = QComboBox()  # 创建下拉框，用于选择平台
        self.platform_dropdown.addItems(["Select", "Xiaohongshu", "Douyin", "Video Account"])  # 添加平台选项
        self.platform_dropdown.currentTextChanged.connect(self.load_accounts)  # 当选项改变时，加载对应账号

        # 账号选择下拉框
        self.account_label = QLabel("Select Account:")  # 创建标签，提示用户选择账号
        self.account_dropdown = QComboBox()  # 创建下拉框，用于选择账号

        # 账号状态显示
        self.status_label = QLabel("Account Status:")  # 创建标签，显示账号状态
        self.status_display = QLabel("Not Logged In")  # 初始化状态显示为“未登录”

        # 将控件添加到布局中
        layout.addWidget(self.platform_label)  # 添加平台选择标签
        layout.addWidget(self.platform_dropdown)  # 添加平台选择下拉框
        layout.addWidget(self.account_label)  # 添加账号选择标签
        layout.addWidget(self.account_dropdown)  # 添加账号选择下拉框

        # 状态显示布局
        status_layout = QHBoxLayout()  # 创建一个水平布局
        status_layout.addWidget(self.status_label)  # 添加状态标签到水平布局
        status_layout.addWidget(self.status_display)  # 添加状态显示到水平布局
        layout.addLayout(status_layout)  # 将水平布局添加到主布局中

    def load_accounts(self, platform):
        """
        根据选定的平台加载对应的账号
        :param platform: 选定的平台名称
        """
        if platform == "Select":  # 如果选择的是默认选项
            self.account_dropdown.clear()  # 清空账号下拉框
            self.account_dropdown.addItem("No Accounts")  # 显示“无账号”
            self.status_display.setText("Not Logged In")  # 设置状态为“未登录”
            return

        # 构造 cookies 目录路径
        cookies_path = os.path.join("cookies", platform.lower())  # 根据平台名称生成目录路径
        if not os.path.exists(cookies_path):  # 如果目录不存在
            self.account_dropdown.clear()  # 清空账号下拉框
            self.account_dropdown.addItem("No Accounts")  # 显示“无账号”
            self.status_display.setText("Not Logged In")  # 设置状态为“未登录”
            return

        # 获取目录中的账号文件列表
        accounts = []  # 初始化账号列表
        for file in os.listdir(cookies_path):  # 遍历目录中的文件
            if file.endswith("account.json"):  # 筛选出以 account.json 结尾的文件
                accounts.append(file)  # 将文件名添加到账号列表中

        self.account_dropdown.clear()  # 清空账号下拉框
        if accounts:  # 如果有账号文件
            self.account_dropdown.addItems(accounts)  # 将账号文件名添加到下拉框
            self.account_dropdown.currentTextChanged.connect(self.update_status)  # 当账号选项改变时，更新状态
            self.update_status(accounts[0])  # 默认显示第一个账号的状态
        else:  # 如果没有账号文件
            self.account_dropdown.addItem("No Accounts")  # 显示“无账号”
            self.status_display.setText("Not Logged In")  # 设置状态为“未登录”

    def update_status(self, account_file):
        """
        根据选定的账号文件更新账号状态
        :param account_file: 选定的账号文件名
        """
        if not account_file or account_file == "No Accounts":  # 如果文件名为空或为“无账号”
            self.status_display.setText("Not Logged In")  # 设置状态为“未登录”
            return

        # 构造账号文件路径
        platform = self.platform_dropdown.currentText().lower()  # 获取当前选中的平台并转为小写
        account_path = os.path.join("cookies", platform, account_file)  # 拼接账号文件的完整路径
        try:
            with open(account_path, "r") as file:  # 打开账号文件
                account_data = json.load(file)  # 加载 JSON 数据
                status = account_data.get("status", "Unknown")  # 获取状态信息，默认为“未知”
                self.status_display.setText(status)  # 显示状态
        except Exception as e:  # 捕获异常
            self.status_display.setText("Error Loading Account")  # 显示加载错误
