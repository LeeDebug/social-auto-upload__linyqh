import configparser
import sys
import asyncio
import time
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
    QComboBox, QTextEdit, QWidget
)
from xhs import XhsClient
from conf import BASE_DIR
from utils.files_times import generate_schedule_time_any_day, get_title_and_hashtags
from uploader.xhs_uploader.main import sign_local, beauty_print

class XhsUploaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小红书视频上传工具")
        self.setGeometry(200, 200, 800, 600)

        self.log_output = QTextEdit()  # 初始化日志输出窗口
        self.log_output.setReadOnly(True)

        self.log("初始化主窗口...")

        # 主界面布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.log("初始化界面组件...")
        # 组件初始化
        self.init_ui()

    def init_ui(self):
        self.log("创建账户配置文件选择下拉框...")
        # 选择账户配置文件（这里使用accounts.ini，与原代码对应）
        self.layout.addWidget(QLabel("选择账户配置文件 (accounts.ini):"))
        self.account_combo = QComboBox()
        self.populate_account_files()
        self.layout.addWidget(self.account_combo)

        self.log("创建视频文件夹选择下拉框...")
        # 选择视频文件夹
        self.layout.addWidget(QLabel("选择视频文件夹:"))
        self.folder_combo = QComboBox()
        self.populate_video_folders()
        self.layout.addWidget(self.folder_combo)

        self.log("创建发送模式选择下拉框...")
        # 定时发送或立即发送选择
        self.layout.addWidget(QLabel("发送方式:"))
        self.send_mode_combo = QComboBox()
        self.send_mode_combo.addItems(["定时发送", "立即发送"])
        self.send_mode_combo.currentIndexChanged.connect(self.toggle_schedule_options)
        self.layout.addWidget(self.send_mode_combo)

        self.log("创建定时发送参数配置输入框...")
        # 定时发送参数配置
        self.schedule_options_layout = QVBoxLayout()
        self.layout.addLayout(self.schedule_options_layout)

        self.schedule_options_layout.addWidget(QLabel("每日发送次数 (daily_times):"))
        self.daily_times_input = QLineEdit("1")
        self.schedule_options_layout.addWidget(self.daily_times_input)

        self.schedule_options_layout.addWidget(QLabel("开始日期 (start_date):"))
        self.start_date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.schedule_options_layout.addWidget(self.start_date_input)

        self.schedule_options_layout.addWidget(QLabel("提前天数 (days_ahead):"))
        self.days_ahead_input = QLineEdit("0")
        self.schedule_options_layout.addWidget(self.days_ahead_input)

        self.log("初始化定时发送参数配置为隐藏状态...")
        # 隐藏定时发送参数配置
        self.toggle_schedule_options()

        self.log("创建开始上传按钮...")
        # 开始上传按钮
        self.upload_button = QPushButton("开始上传")
        self.upload_button.clicked.connect(self.start_upload)
        self.layout.addWidget(self.upload_button)

        self.log("创建日志输出窗口...")
        # 输出日志窗口
        self.layout.addWidget(QLabel("日志输出:"))
        self.layout.addWidget(self.log_output)

    def populate_account_files(self):
        self.log("加载账户配置文件...")
        """填充账户配置文件下拉框"""
        account_dir = Path(BASE_DIR) / "cookies" / "xhs_uploader"
        account_files = list(account_dir.glob("*.ini"))
        file_names = [file.name for file in account_files]
        self.account_combo.addItems(file_names)
        self.log(f"找到以下账户配置文件: {', '.join(file_names)}")

        # 查找是否存在accounts.ini并设置默认选中
        for index, file_name in enumerate(file_names):
            if file_name == "accounts.ini":
                self.account_combo.setCurrentIndex(index)
                break

    def populate_video_folders(self):
        self.log("加载视频文件夹...")
        """填充视频文件夹下拉框"""
        video_dir = Path(BASE_DIR) / "videos" / "backups"
        folders = [folder.name for folder in video_dir.iterdir() if folder.is_dir()]
        self.folder_combo.addItems(folders)
        self.log(f"找到以下视频文件夹: {'; '.join(folders)}")

        today_str = datetime.now().strftime("%Y-%m-%d")
        for index, folder_name in enumerate(folders):
            if folder_name == today_str:
                self.folder_combo.setCurrentIndex(index)
                break

    def toggle_schedule_options(self):
        self.log("切换发送模式...")
        """根据发送模式显示或隐藏定时发送选项"""
        is_scheduled = self.send_mode_combo.currentText() == "定时发送"
        self.log(f"当前发送模式: {'定时发送' if is_scheduled else '立即发送'}")
        for i in range(self.schedule_options_layout.count()):
            widget = self.schedule_options_layout.itemAt(i).widget()
            widget.setVisible(is_scheduled)

    def log(self, message):
        """日志输出"""
        self.log_output.append(message + "\n")
        print(message)

    def start_upload(self):
        self.log("开始上传逻辑...")
        try:
            self.log("获取账户配置文件...")
            # 获取账户配置文件
            account_file = Path(self.account_combo.currentText())
            if not account_file.exists():
                self.log(f"账户配置文件不存在: {account_file}")
                return

            self.log("获取视频文件夹...")
            # 获取视频文件夹
            folder_path = Path(BASE_DIR) / "videos" / "backups" / self.folder_combo.currentText()
            files = list(folder_path.glob("*.mp4"))
            if not files:
                self.log("视频文件夹中没有找到.mp4 文件")
                return
            file_num = len(files)
            self.log(f"找到以下视频文件: {[file.name for file in files]}")

            # 读取账户配置文件中的cookies信息
            config = configparser.RawConfigParser()
            config.read(account_file)
            cookies = config['account1']['cookies']

            # 创建XhsClient实例
            xhs_client = XhsClient(cookies, sign=sign_local, timeout=60)

            # 验证cookie有效性
            self.log("验证cookie有效性...")
            try:
                xhs_client.get_video_first_frame_image_id("3214")
            except:
                self.log("cookie 失效")
                return

            # 判断发送模式
            self.log("判断发送模式...")
            is_scheduled = self.send_mode_combo.currentText() == "定时发送"
            if is_scheduled:
                self.log("生成定时发送的时间戳...")
                daily_times = list(map(int, self.daily_times_input.text().split(',')))
                start_date = self.start_date_input.text()
                days_ahead = int(self.days_ahead_input.text())
                publish_datetimes = generate_schedule_time_any_day(file_num, days_ahead, daily_times, start_date,
                                                                    timestamps=True)
                self.log(f"生成的时间戳: {publish_datetimes}")
            else:
                self.log("立即发送模式，无需生成时间戳...")
                publish_datetimes = [0] * file_num

            for index, file in enumerate(files):
                self.log(f"处理视频文件: {file.name}")
                title, tags = get_title_and_hashtags(str(file))
                tags_str = ' '.join(['#' + tag for tag in tags])
                hash_tags = []
                topics = []

                self.log(f"视频文件名：{file}")
                self.log(f"标题：{title}")
                self.log(f"Hashtag：{tags}")

                # 获取话题相关信息
                for i in tags[:3]:
                    topic_official = xhs_client.get_suggest_topic(i)
                    if topic_official:
                        topic_official[0]['type'] = 'topic'
                        topic_one = topic_official[0]
                        hash_tag_name = topic_one['name']
                        hash_tags.append(hash_tag_name)
                        topics.append(topic_one)
                self.log("topics: ", topics)

                hash_tags_str = ' ' + ' '.join(['#' + tag + '[话题]#' for tag in hash_tags])

                note = xhs_client.create_video_note(title=title[:20], video_path=str(file),
                                                    desc=title + tags_str + hash_tags_str,
                                                    topics=topics,
                                                    is_private=False,
                                                    post_time=publish_datetimes[index].strftime("%Y-%m-%d %H:%M:%S"))
                beauty_print(note)
                self.log(f"成功上传视频: {file.name}")
                time.sleep(30)  # 避免风控，强制休眠30s

        except Exception as e:
            self.log(f"发生错误: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = XhsUploaderGUI()
    gui.show()
    sys.exit(app.exec())