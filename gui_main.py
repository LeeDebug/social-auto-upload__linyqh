import asyncio
import configparser
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDateTime, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QComboBox, QPushButton, QLabel,
                             QFileDialog, QTextEdit, QMessageBox, QRadioButton,
                             QDateTimeEdit, QButtonGroup, QCheckBox, QGroupBox,
                             QFrame, QInputDialog)
from xhs import XhsClient

# 项目相关导入
from conf import BASE_DIR
from uploader.bilibili_uploader.main import (BilibiliUploader)
# 各平台上传器导入
from uploader.douyin_uploader.main import douyin_setup, DouYinVideo
from uploader.ks_uploader.main import ks_setup, KSVideo
from uploader.tencent_uploader.main import weixin_setup
from uploader.tk_uploader.main_chrome import tiktok_setup
from uploader.xhs_uploader.main import sign_local
from utils.base_social_media import get_supported_social_media, get_platform_key
from utils.files_times import get_title_and_hashtags


class UploadWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def __init__(self,
                 platform,
                 account_name,
                 video_file,
                 publish_time=0,
                 title=None,
                 tags=None,
                 is_scheduled=False):
        super().__init__()
        self.platform = platform
        self.account_name = account_name
        self.video_file = video_file
        self.publish_time = publish_time
        self.title = title
        self.tags = tags
        self.is_scheduled = is_scheduled

    def run(self):
        try:
            self.progress.emit(f"\n=== 开始上传视频到{self.platform} ===")

            # 构建cookie文件路径
            if self.platform == "xhs":
                # 小红书使用特殊的配置文件
                account_file = Path(BASE_DIR) / "cookies" / "xhs_accounts.ini"
            else:
                # 其他平台都使用固定的account.json
                account_file = Path(
                    BASE_DIR
                ) / "cookies" / f"{self.platform}_uploader" / "account.json"

            self.progress.emit(f"使用配置文件：{account_file.relative_to(BASE_DIR)}")

            if not account_file.exists():
                raise Exception(f"账号配置文件不存在：{account_file}")

            self.progress.emit("账号配置文件检查完成")

            # 获取视频信息
            if self.title is None or self.tags is None:
                self.progress.emit("\n=== 读取视频信息 ===")
                self.progress.emit(f"视频文件：{self.video_file}")
                self.title, self.tags = get_title_and_hashtags(self.video_file)
                self.progress.emit(f"标题：{self.title}")
                self.progress.emit(f"标签：{', '.join(self.tags)}")

            # 根据平台选择不同的上传方法
            if self.platform == "xhs":
                # 小红书上传处理...
                pass
            elif self.platform == "bilibili":
                # B站上传处理...
                pass
            elif self.platform == "kuaishou":
                self.progress.emit("\n=== 初始化快手上传 ===")
                try:
                    # 创建快手视频对象
                    video = KSVideo(
                        title=self.title,
                        file_path=self.video_file,
                        tags=self.tags,
                        publish_date=datetime.fromtimestamp(self.publish_time)
                        if self.publish_time else datetime.now(),
                        account_file=str(account_file))

                    # 执行上传并等待完成
                    await_result = asyncio.run(video.main())

                    # 检查上传结果
                    if await_result:
                        self.progress.emit("✅ 视频上传成功！")
                        self.finished.emit(True, "视频上传成功！")
                    else:
                        raise Exception("上传失败，请检查日志")

                except playwright._impl._errors.TargetClosedError:
                    # 特殊处理浏览器关闭错误
                    self.progress.emit("⚠️ 浏览器被关闭，但视频可能已上传成功")
                    self.progress.emit("请登录快手创作者平台检查视频是否上传成功")
                    self.finished.emit(True, "视频可能已上传成功，请手动检查")

                except Exception as e:
                    raise Exception(f"快手上传失败：{str(e)}")

            elif self.platform == "douyin":
                self.progress.emit("\n=== 初始化抖音上传 ===")
                # 创建抖音视频对象
                video = DouYinVideo(
                    title=self.title,
                    file_path=self.video_file,
                    tags=self.tags,
                    publish_date=datetime.fromtimestamp(self.publish_time)
                    if self.publish_time else datetime.now(),
                    account_file=str(account_file))
                # 执行上传
                await_result = asyncio.run(video.main())
                if await_result:
                    self.progress.emit("视频上传成功！")
                    self.finished.emit(True, "视频上传成功！")
                else:
                    raise Exception("上传失败")

            # ... 其他平台的处理 ...

        except Exception as e:
            self.progress.emit(f"\n=== 上传失败 ===")
            self.progress.emit(f"错误信息：{str(e)}")
            self.finished.emit(False, f"上传失败：{str(e)}")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("自媒体多平台视频上传工具")
        # 增加窗口默认大小
        self.setMinimumSize(1000, 900)  # 增加最小尺寸
        self.resize(1100, 1200)  # 设置默认尺寸

        # 优化界面样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 15px;
                color: #333333;
                font-weight: 500;
            }
            QPushButton {
                background-color: #2d8cf0;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 15px;
                min-width: 120px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2b85e4;
            }
            QPushButton:pressed {
                background-color: #2472c8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #dcdee2;
                border-radius: 5px;
                min-width: 250px;
                font-size: 15px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #2d8cf0;
            }
            QTextEdit {
                border: 1px solid #dcdee2;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #2d8cf0;
            }
            QRadioButton {
                font-size: 15px;
                spacing: 10px;
            }
            QCheckBox {
                font-size: 15px;
                spacing: 10px;
            }
            QDateTimeEdit {
                padding: 8px 12px;
                border: 1px solid #dcdee2;
                border-radius: 5px;
                min-width: 250px;
                font-size: 15px;
                background-color: white;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #dcdee2;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                color: #2d8cf0;
            }
        """)
        self.initUI()

        # 创建一个定时器，在窗口显示后执行检查
        self.init_timer = QTimer(self)
        self.init_timer.setSingleShot(True)  # 只执行一次
        self.init_timer.timeout.connect(self.delayed_init)

    def initUI(self):
        # 主布局增加边距
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)  # 增加组件间距
        layout.setContentsMargins(25, 25, 25, 25)  # 增加边距

        # 创建分组框
        platform_group = QGroupBox("平台设置")
        video_group = QGroupBox("视频信息")
        publish_group = QGroupBox("发布设置")
        log_group = QGroupBox("日志信息")

        # 创建日志文本框 - 移到最前面
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(300)  # 增加日志框高度
        log_layout.addWidget(self.log_text)

        # 平台设置布局
        platform_layout = QVBoxLayout(platform_group)
        platform_layout.setSpacing(10)

        # 平台选择
        platform_row = QHBoxLayout()
        platform_label = QLabel("选择平台：")
        platform_label.setFixedWidth(80)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(get_supported_social_media())
        platform_row.addWidget(platform_label)
        platform_row.addWidget(self.platform_combo)
        platform_layout.addLayout(platform_row)

        # 账号输入
        account_row = QHBoxLayout()
        account_label = QLabel("账号名称：")
        account_label.setFixedWidth(80)
        self.account_input = QComboBox()
        self.account_input.setEditable(True)
        account_row.addWidget(account_label)
        account_row.addWidget(self.account_input)
        platform_layout.addLayout(account_row)

        # 直接连接到新的处理函数，不需要先断开
        self.platform_combo.currentTextChanged.connect(
            self.on_platform_changed)

        # 延迟加载第一次的账号列表
        QTimer.singleShot(100,
                          lambda: self.update_account_list(show_loading=True))

        # 添加获取 Cookies 按钮
        cookies_row = QHBoxLayout()
        get_cookies_btn = QPushButton("获取 Cookies (仅小红书)")
        get_cookies_btn.clicked.connect(self.get_cookies)

        # 根据平台启用/禁用按钮并更新提示文本
        def update_cookies_btn(platform):
            platform_key = get_platform_key(platform)  # 转换平台名称
            is_xhs = platform_key == "xhs"  # 使用平台键值判断
            get_cookies_btn.setEnabled(is_xhs)
            if platform_key == "bilibili":
                get_cookies_btn.setToolTip(
                    "B站请使用 biliup.exe 登录获取 cookies，\n"
                    "获取到的 account.json 文件请放到 cookies 目录下")
            else:
                get_cookies_btn.setToolTip(
                    "其他平台请使用对应的登录工具获取 cookies"
                    if not is_xhs else "点击获取小红书平台的 cookies")
            # 设置不同状态下的样式
            if not is_xhs:
                get_cookies_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #cccccc;
                        color: #666666;
                    }
                    QPushButton:hover {
                        background-color: #cccccc;
                    }
                """)
            else:
                get_cookies_btn.setStyleSheet("")  # 恢复默认样式

        # 连接平台选择变化事件
        self.platform_combo.currentTextChanged.connect(update_cookies_btn)
        # 初始状态设置
        update_cookies_btn(self.platform_combo.currentText())

        cookies_row.addWidget(get_cookies_btn)
        platform_layout.addLayout(cookies_row)

        # 视频信息布局
        video_layout = QVBoxLayout(video_group)
        video_layout.setSpacing(10)

        # 视频选择
        video_row = QHBoxLayout()
        self.video_path_label = QLabel("未选择视频")
        select_video_btn = QPushButton("选择视频")
        select_video_btn.clicked.connect(self.select_video)
        video_row.addWidget(self.video_path_label)
        video_row.addWidget(select_video_btn)
        video_layout.addLayout(video_row)

        # 标题和标签输入
        title_row = QHBoxLayout()
        title_label = QLabel("视频标题：")
        title_label.setFixedWidth(80)
        self.title_input = QTextEdit()
        self.title_input.setMaximumHeight(50)
        title_row.addWidget(title_label)
        title_row.addWidget(self.title_input)
        video_layout.addLayout(title_row)

        tags_row = QHBoxLayout()
        tags_label = QLabel("视频标签：")
        tags_label.setFixedWidth(80)
        self.tags_input = QTextEdit()
        self.tags_input.setMaximumHeight(50)
        self.tags_input.setPlaceholderText("多个标签用空格分隔，例如：标签1 标签2 标签3")
        tags_row.addWidget(tags_label)
        tags_row.addWidget(self.tags_input)
        video_layout.addLayout(tags_row)

        # 自动读取选项
        self.auto_read_check = QCheckBox("自动读取视频描述文件")
        self.auto_read_check.setChecked(True)
        self.auto_read_check.stateChanged.connect(self.on_auto_read_changed)
        video_layout.addWidget(self.auto_read_check)

        # 发布设置布局
        publish_layout = QVBoxLayout(publish_group)
        publish_layout.setSpacing(10)

        # 发布类型选择
        publish_row = QHBoxLayout()
        publish_label = QLabel("发布类型：")
        publish_label.setFixedWidth(80)

        # 创建一个子布局来包含单选按钮和时间选择器
        publish_options = QHBoxLayout()
        publish_options.setSpacing(20)

        # 单选按钮组
        radio_group = QHBoxLayout()
        self.publish_type_group = QButtonGroup()
        self.immediate_radio = QRadioButton("立即发布")
        self.scheduled_radio = QRadioButton("定时发布")
        self.immediate_radio.setChecked(True)
        self.publish_type_group.addButton(self.immediate_radio)
        self.publish_type_group.addButton(self.scheduled_radio)
        radio_group.addWidget(self.immediate_radio)
        radio_group.addWidget(self.scheduled_radio)

        # 时间选择器
        time_group = QHBoxLayout()
        time_label = QLabel("发布时间：")
        time_label.setFixedWidth(80)
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight
                                | Qt.AlignmentFlag.AlignVCenter)

        # 创建时间选择器
        self.datetime_edit = QDateTimeEdit()
        # 设置最小时间为当前时间
        self.datetime_edit.setMinimumDateTime(QDateTime.currentDateTime())
        # 设置默认时间为当前时间后1小时
        self.datetime_edit.setDateTime(
            QDateTime.currentDateTime().addSecs(3600))
        # 使用更友好的日期时间格式
        self.datetime_edit.setDisplayFormat("yyyy年MM月dd日 HH:mm")
        # 允许弹出日历选择
        self.datetime_edit.setCalendarPopup(True)
        # 设置时间段为5分钟
        self.datetime_edit.setTimeSpec(Qt.TimeSpec.LocalTime)
        # 设置最小宽度
        self.datetime_edit.setMinimumWidth(200)
        # 默认禁用
        self.datetime_edit.setEnabled(False)

        # 在时间变更时进行验证和调整
        def adjust_minutes(time):
            """将分钟调整为5的倍数"""
            minutes = time.time().minute()
            adjusted = ((minutes + 4) // 5) * 5  # 向上取整到最近的5分钟
            if adjusted != minutes:
                new_time = time.addSecs((adjusted - minutes) * 60)
                self.datetime_edit.setDateTime(new_time)

        # 连接时间变更信号
        self.datetime_edit.dateTimeChanged.connect(adjust_minutes)

        time_group.addWidget(time_label)
        time_group.addWidget(self.datetime_edit)
        time_group.addStretch()

        # 添加信号连接
        self.immediate_radio.toggled.connect(self.on_publish_type_changed)
        self.scheduled_radio.toggled.connect(self.on_publish_type_changed)
        self.datetime_edit.dateTimeChanged.connect(self.on_datetime_changed)

        # 添加到发布选项布局
        publish_options.addLayout(radio_group)
        publish_options.addLayout(time_group)
        publish_options.addStretch()

        publish_row.addWidget(publish_label)
        publish_row.addLayout(publish_options)
        publish_layout.addLayout(publish_row)

        # 操作按钮
        button_row = QHBoxLayout()
        login_btn = QPushButton("登录账号")
        upload_btn = QPushButton("上传视频")
        login_btn.clicked.connect(self.login)
        upload_btn.clicked.connect(self.upload)
        button_row.addWidget(login_btn)
        button_row.addWidget(upload_btn)
        button_row.addStretch()
        publish_layout.addLayout(button_row)

        # 添加所有分组到主布局
        layout.addWidget(platform_group)
        layout.addWidget(video_group)
        layout.addWidget(publish_group)
        layout.addWidget(log_group)

        # 添加广告信息
        ad_frame = QFrame()
        ad_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1890ff, stop:1 #36cfc9);
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
            }
        """)
        ad_layout = QVBoxLayout(ad_frame)
        ad_layout.setSpacing(5)  # 减小间距
        ad_layout.setContentsMargins(10, 5, 10, 5)  # 减小内边距

        # 广告内容 - 使用单行显示
        ad_text = QLabel(
            "🌟 专业版功能：✨ 支持多平台上传 · 🚀 批量上传 · 📊 智能分发 · 💎 私域引流 · 📱 商务合作请联系微信：<b>JUNLIN9403</b>"
        )
        ad_text.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                line-height: 1.2;
            }
        """)

        # 添加到布局
        ad_layout.addWidget(ad_text)
        layout.addWidget(ad_frame)

    def select_video(self):
        """手动选择单个视频文件"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.avi *.mov *.wmv *.flv);;所有文件 (*)")

        if file_name:
            # 单个文件上传模式
            self.video_queue = None
            self.current_video_index = None
            self.video_path_label.setText(file_name)
            self.log_text.append("\n=== 已选择单个视频文件 ===")
            self.log_text.append(f"视频文件：{file_name}")

            if self.auto_read_check.isChecked():
                self.load_video_info()

    def login(self):
        platform = self.platform_combo.currentText()
        account = self.account_input.currentText()

        if not account or account == "请先登录账号":
            QMessageBox.warning(self, "警告", "请输入账号名称")
            return

        try:
            if platform == "xhs":
                # 小红书使用特殊的配置文件
                config_file = Path(
                    BASE_DIR) / "uploader" / "xhs_uploader" / "accounts.ini"
                config_file.parent.mkdir(parents=True, exist_ok=True)
                self.log_text.append("请手动编辑 accounts.ini 文件配置小红书账号")

            elif platform == "bilibili":
                # B站使用特殊的cookie获取方式
                cookie_dir = Path(BASE_DIR) / "uploader" / "bilibili_uploader"
                cookie_dir.mkdir(parents=True, exist_ok=True)
                self.log_text.append("请使用以下步骤获取B站cookie：")
                self.log_text.append("1. 打开命令行")
                self.log_text.append(f"2. 进入目录：{cookie_dir}")
                self.log_text.append(
                    "3. 运行命令：biliup.exe -u account.json login")
                self.log_text.append("4. 按照提示在浏览器中登录B站账号")

            elif platform == "douyin":
                # 抖音的cookie文件
                cookie_file = Path(
                    BASE_DIR) / "cookies" / "douyin_account.json"
                cookie_file.parent.mkdir(parents=True, exist_ok=True)
                asyncio.run(douyin_setup(str(cookie_file), handle=True))

            else:
                # 其他平台使用通用的cookie文件命名方式
                cookie_file = Path(
                    BASE_DIR) / "cookies" / f"{platform}_{account}.json"
                cookie_file.parent.mkdir(parents=True, exist_ok=True)

                if platform == "kuaishou":
                    asyncio.run(ks_setup(str(cookie_file), handle=True))
                elif platform == "tiktok":
                    asyncio.run(tiktok_setup(str(cookie_file), handle=True))
                elif platform == "tencent":
                    asyncio.run(weixin_setup(str(cookie_file), handle=True))

            self.log_text.append(f"正在登录 {platform} 平台，账号：{account}")

            # 登录成功后更新账号列表
            self.update_account_list()
            # 选择新登录的账号
            index = self.account_input.findText(account)
            if index >= 0:
                self.account_input.setCurrentIndex(index)

        except Exception as e:
            self.log_text.append(f"登录失败：{str(e)}")
            QMessageBox.warning(self, "登录失败", str(e))

    def on_publish_type_changed(self):
        is_scheduled = self.scheduled_radio.isChecked()
        self.datetime_edit.setEnabled(is_scheduled)

        if is_scheduled:
            current_time = QDateTime.currentDateTime()
            self.datetime_edit.setMinimumDateTime(current_time)
            if self.datetime_edit.dateTime() <= current_time:
                self.datetime_edit.setDateTime(current_time.addSecs(3600))
            self.log_text.append("已切换到定时发布模式")
            self.log_text.append("提示：请选择发布时间，需至少比当前时间晚5分钟")
            self.log_text.append(
                f"默认设置为：{self.datetime_edit.dateTime().toString('yyyy年MM月dd日 HH:mm')}"
            )
        else:
            self.log_text.append("已切换到立即发布模式")

    def append_log(self, message):
        """添加带时间戳的日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum())

    def upload(self):
        try:
            platform = self.platform_combo.currentText()
            platform_key = get_platform_key(platform)
            account = self.account_input.currentText()

            # 构建cookie文件路径
            if platform_key == "xhs":
                # 小红书使用特殊的配置文件
                account_file = Path(BASE_DIR) / "cookies" / "xhs_accounts.ini"
                # 检查配置文件
                if not account_file.exists():
                    raise Exception(f"账号配置文件不存在：{account_file}")

                # 验证配置文件格式
                try:
                    config = configparser.RawConfigParser()
                    config.read(account_file, encoding='utf-8')
                    # 检查是否有任何账号配置
                    if len(config.sections()) == 0:
                        raise Exception("配置文件中没有找到任何账号配置")
                    # 使用当前选择的账号名称
                    if not config.has_section(account):
                        raise Exception(f"配置文件中未找到账号 [{account}] 的配置")
                    if not config.has_option(account, 'cookies'):
                        raise Exception(f"账号 [{account}] 缺少 cookies 配置")
                except Exception as e:
                    raise Exception(f"配置文件格式错误：{str(e)}")
            else:
                # 其他平台都使用固定的account.json
                account_file = Path(
                    BASE_DIR
                ) / "cookies" / f"{platform_key}_uploader" / "account.json"
                # 如果不存在，则查找旧的位置
                if not account_file.exists() and platform_key == "bilibili":
                    account_file = Path(
                        BASE_DIR
                    ) / "uploader" / "bilibili_uploader" / "account.json"
                if not account_file.exists():
                    raise Exception(f"账号配置文件不存在：{account_file}")

            # 获取当前视频信息并上传
            video_path = self.video_path_label.text()
            title = self.title_input.toPlainText().strip()
            if not title:
                raise Exception("请输入视频标题")

            tags = self.tags_input.toPlainText().strip().split()
            if not tags:
                raise Exception("请输入至少一个标签")

            # 获取发布时间
            if self.immediate_radio.isChecked():
                publish_time = 0
            else:
                # 定时发布
                scheduled_time = self.datetime_edit.dateTime()
                current_time = QDateTime.currentDateTime()
                if scheduled_time <= current_time:
                    raise Exception("定时发布时间必须大于当前时间")
                publish_time = scheduled_time.toSecsSinceEpoch()

            # 创建上传工作线程
            self.upload_worker = UploadWorker(
                platform=platform_key,
                account_name=account,
                video_file=video_path,
                publish_time=publish_time,
                title=title,
                tags=tags,
                is_scheduled=self.scheduled_radio.isChecked())
            self.upload_worker.finished.connect(self.on_upload_finished)
            self.upload_worker.progress.connect(self.log_text.append)
            self.upload_worker.start()

        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))
            self.log_text.append(f"❌ 错误：{str(e)}")

    def on_upload_finished(self, success, message):
        """上传完成后的处理"""
        if success:
            QMessageBox.information(self, "成功", message)
            # 如果是批量上传模式且还有下一个视频
            if self.video_queue and self.current_video_index < len(
                    self.video_queue) - 1:
                self.current_video_index += 1
                next_video = str(self.video_queue[self.current_video_index])
                self.video_path_label.setText(next_video)
                self.log_text.append(
                    f"\n准备上传第 {self.current_video_index + 1}/{len(self.video_queue)} 个视频：{next_video}"
                )

                # 读取下一个视频的信息
                if self.auto_read_check.isChecked():
                    self.load_video_info()

                # 自动开始上传下一个视频
                self.upload_video()
            elif self.video_queue:
                self.log_text.append("\n=== 所有视频上传完成 ===")
        else:
            QMessageBox.warning(self, "失败", message)
        self.log_text.append(message)

    def on_auto_read_changed(self, state):
        # 启用/禁用标题和标签输入
        self.title_input.setEnabled(not state)
        self.tags_input.setEnabled(not state)
        if state and self.video_path_label.text() != "未选择视频":
            self.load_video_info()

    def load_video_info(self, show_error=True):
        """加载视频信息"""
        try:
            video_path = self.video_path_label.text()
            if video_path and video_path != "未选择视频":
                title, tags = get_title_and_hashtags(video_path,
                                                     show_error=show_error)
                if title and tags:
                    self.title_input.setPlainText(title)
                    self.tags_input.setPlainText(' '.join(tags))
                elif show_error:
                    QMessageBox.warning(self, "警告", "未找到视频描述文件，请手动输入标题和标签")
        except Exception as e:
            if show_error:
                QMessageBox.warning(self, "警告", str(e))

    def on_datetime_changed(self, qdate):
        """处理时间选择器的时间变更"""
        if self.scheduled_radio.isChecked():
            current_time = QDateTime.currentDateTime()
            if qdate <= current_time:
                self.datetime_edit.setDateTime(current_time.addSecs(3600))
                self.log_text.append("提示：发布时间必须大于当前时间")
            else:
                time_diff = qdate.toSecsSinceEpoch(
                ) - current_time.toSecsSinceEpoch()
                if time_diff < 300:  # 小于5分钟
                    self.datetime_edit.setDateTime(current_time.addSecs(300))
                    self.log_text.append("提示：发布时间必须至少比当前时间晚5分钟")
                else:
                    self.log_text.append(
                        f"发布时间已更新为：{qdate.toString('yyyy年MM月dd日 HH:mm')}")

    def get_account_list(self, platform):
        """获取平台的账号列表"""
        platform_key = get_platform_key(platform)

        self.log_text.append(f"\n=== 正在获取{platform}账号列表 ===")

        # 检查账号配置文件
        if platform_key == "xhs":
            account_file = Path(BASE_DIR) / "cookies" / "xhs_accounts.ini"
        else:
            account_file = Path(
                BASE_DIR
            ) / "cookies" / f"{platform_key}_uploader" / "account.json"

        # 如果账号文件不存在
        if not account_file.exists():
            self.log_text.append("未找到任何账号，请先登录")
            return ["请先登录账号"]

        # 读取账号信息
        try:
            if platform_key == "xhs":
                config = configparser.RawConfigParser()
                config.read(account_file, encoding='utf-8')
                accounts = config.sections()
            else:
                accounts = [platform]  # 其他平台只显示平台名

            if accounts:
                self.log_text.append(f"找到 {len(accounts)} 个账号")
                return accounts
            else:
                self.log_text.append("未找到任何账号，请先登录")
                return ["请先登录账号"]

        except Exception as e:
            self.log_text.append(f"读取账号信息失败：{str(e)}")
            return ["请先登录账号"]

    def update_account_list(self, show_loading=False):
        """更新账号列表"""
        if show_loading:
            self.account_input.clear()
            self.account_input.addItem("正在加载账号列表...")
            self.account_input.setEnabled(False)
            # 延迟执行实际的账号验证
            QTimer.singleShot(100, self._do_update_account_list)
        else:
            self._do_update_account_list()

    def _do_update_account_list(self):
        """实际执行账号列表更新"""
        try:
            platform = self.platform_combo.currentText()
            platform_key = get_platform_key(platform)
            accounts = self.get_account_list(platform)

            self.account_input.clear()
            self.account_input.addItems(accounts)
            self.account_input.setEnabled(True)

            # 如果没有找到有效账号，且不是小红书和B站，提示是否登录
            if accounts == ["请先登录账号"
                            ] and platform_key not in ["xhs", "bilibili"]:
                reply = QMessageBox.question(
                    self, "登录提示", f"未检测到{platform}平台的账号信息，是否现在登录？",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.on_login_clicked()  # 调用登录功能

        except Exception as e:
            self.log_text.append(f"更新账号列表失败：{str(e)}")
            self.account_input.clear()
            self.account_input.addItem("请先登录账号")
            self.account_input.setEnabled(True)

    def get_cookies(self):
        """获取并保存 cookies"""
        try:
            platform = self.platform_combo.currentText()
            platform_key = get_platform_key(platform)

            if platform_key == "xhs":
                try:
                    # 获取当前选择的账号名称，不再使用默认名称
                    account_name = self.account_input.currentText()
                    if account_name == "请先登录账号":
                        # 让用户输入账号名称
                        name_dialog = QInputDialog()
                        name_dialog.setWindowTitle("输入账号名称")
                        name_dialog.setLabelText("请输入小红书账号名称：")
                        name_dialog.setTextValue("")

                        if name_dialog.exec():
                            account_name = name_dialog.textValue().strip()
                            if not account_name:
                                raise Exception("账号名称不能为空")
                        else:
                            raise Exception("未输入账号名称")

                    # 打开小红书登录页面
                    import webbrowser
                    webbrowser.open(
                        'https://creator.xiaohongshu.com/creator/home')

                    # 提示用户操作
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText("""请按以下步骤操作：

1. 在打开的浏览器中登录小红书
2. 登录成功后按 F12 打开开发者工具
3. 切换到 Network 标签页
4. 刷新页面
5. 在 Network 中找到任意请求
6. 在请求头中找到 Cookie 字段
7. 复制整个 Cookie 值
8. 点击确定后将复制的 Cookie 粘贴到弹出的输入框中""")
                    msg.setWindowTitle("小红书登录")
                    msg.exec()

                    # 弹出输入框让用户粘贴cookie
                    cookie_input = QInputDialog()
                    cookie_input.setWindowTitle("输入Cookie")
                    cookie_input.setLabelText("请粘贴复制的Cookie值：")
                    cookie_input.setTextValue("")
                    cookie_input.resize(600, 200)

                    if cookie_input.exec():
                        cookie_str = cookie_input.textValue()
                        if not cookie_str:
                            raise Exception("Cookie不能为空")

                        # 保存cookie到配置文件
                        config_file = Path(
                            BASE_DIR) / "cookies" / "xhs_accounts.ini"
                        config = configparser.ConfigParser()

                        # 读取现有配置
                        if config_file.exists():
                            config.read(config_file, encoding='utf-8')

                        # 更新或添加新账号
                        config[account_name] = {'cookies': cookie_str}

                        # 保存配置
                        config_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(config_file, 'w', encoding='utf-8') as f:
                            config.write(f)

                        self.log_text.append(f"\n已保存账号 [{account_name}] 的配置")

                        # 验证新cookie
                        try:
                            xhs_client = XhsClient(cookie_str, sign=sign_local)
                            user_info = xhs_client.get_self_info()

                            # 打印原始返回数据用于调试
                            self.log_text.append("\n=== API 返回数据 ===")
                            self.log_text.append(str(user_info))

                            # 检查API返回状态 - 修改这部分逻辑
                            if not isinstance(user_info, dict):
                                raise Exception(f"API返回格式错误: {user_info}")

                            # 检查是否包含必要的信息
                            if 'basic_info' not in user_info:
                                raise Exception("API返回数据缺少用户信息")

                            # 解析并显示用户信息
                            self.log_text.append("\n=== 用户信息 ===")

                            # 基本信息
                            basic_info = user_info.get('basic_info', {})
                            if not basic_info:
                                raise Exception("未获取到用户基本信息")

                            self.log_text.append("\n【基本信息】")
                            self.log_text.append(
                                f"用户名：{basic_info.get('nickname', '未知')}")
                            self.log_text.append(
                                f"用户ID：{basic_info.get('red_id', '未知')}")
                            self.log_text.append(
                                f"简介：{basic_info.get('desc', '暂无')}")
                            self.log_text.append(
                                f"性别：{'女' if basic_info.get('gender') == 2 else '男' if basic_info.get('gender') == 1 else '未知'}"
                            )
                            self.log_text.append(
                                f"地区：{basic_info.get('ip_location', '未知')}")

                            # 互动数据
                            self.log_text.append("\n【互动数据】")
                            interactions = user_info.get('interactions', [])
                            for interaction in interactions:
                                name = interaction.get('name')
                                count = interaction.get('count')
                                if name and count:
                                    self.log_text.append(f"{name}：{count}")

                            # 用户标签
                            self.log_text.append("\n【用户标签】")
                            tags = user_info.get('tags', [])
                            for tag in tags:
                                tag_type = tag.get('tagType', '')
                                tag_name = tag.get('name', '')
                                if tag_name:
                                    self.log_text.append(
                                        f"{tag_type}：{tag_name}")

                            self.log_text.append("\n=== Cookie 验证成功 ===")

                        except Exception as e:
                            self.log_text.append(f"\n=== Cookie 验证失败 ===")
                            self.log_text.append(f"错误信息: {str(e)}")
                            raise Exception(f"Cookie验证失败: {str(e)}")
                    else:
                        raise Exception("用户取消输入")

                except Exception as e:
                    self.log_text.append(f"获取 cookie 过程出错: {str(e)}")
                    raise Exception(f"小红书登录失败: {str(e)}")

            # 更新账号列表
            self.update_account_list()

        except Exception as e:
            self.log_text.append(f"获取 cookies 失败：{str(e)}")
            QMessageBox.warning(self, "获取失败", str(e))

    def check_bilibili_cookie_expired(self):
        """检查B站cookie是否失效"""
        try:
            # 优先检查统一目录下的cookie
            cookie_file = Path(BASE_DIR) / "cookies" / "account.json"

            # 如果统一目录下没有，则检查原始位置
            if not cookie_file.exists():
                cookie_file = Path(
                    BASE_DIR
                ) / "uploader" / "bilibili_uploader" / "account.json"

            if not cookie_file.exists():
                self.log_text.append(f"未找到B站cookie文件：{cookie_file}")
                return True

            self.log_text.append(f"找到B站cookie文件：{cookie_file}")

            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
                self.log_text.append("成功读取cookie文件")

                # 打印cookie数据结构（可选）
                self.log_text.append(
                    f"Cookie数据结构：{json.dumps(cookie_data, indent=2)}")

            # 创建上传器实例测试cookie
            uploader = BilibiliUploader(cookie_data=cookie_data)
            user_info = uploader.get_user_info()  # 尝试获取用户信息
            self.log_text.append(f"成功获取用户信息：{user_info}")
            return False

        except Exception as e:
            self.log_text.append(f"检查B站cookie失败：{str(e)}")
            return True

    def get_xhs_cookie(self):
        """获取小红书cookie"""
        config_file = Path(BASE_DIR) / "cookies" / "xhs_accounts.ini"
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        account_name = self.account_input.currentText()
        return config[account_name]['cookies']  # 使用当前选择的账号名称

    def upload_video(self):
        """上传视频"""
        try:
            platform = self.platform_combo.currentText()
            platform_key = get_platform_key(platform)
            account = self.account_input.currentText()

            # 如果没有手动选择视频，则使用videos目录下的所有视频
            if self.video_path_label.text() == "未选择视频":
                videos_dir = Path(BASE_DIR) / "videos"
                if not videos_dir.exists():
                    raise Exception("未找到 videos 目录")

                video_files = sorted(list(videos_dir.glob("*.mp4")))
                if not video_files:
                    raise Exception("videos 目录下未找到视频文件")

                self.log_text.append("\n=== 准备批量上传 ===")
                self.log_text.append(f"找到 {len(video_files)} 个视频文件：")
                for video in video_files:
                    self.log_text.append(f"- {video.name}")

                # 存储视频队列
                self.video_queue = video_files
                self.current_video_index = 0
                video_path = str(self.video_queue[self.current_video_index])
                self.video_path_label.setText(video_path)
                self.log_text.append(
                    f"\n开始处理第 1/{len(video_files)} 个视频：{video_path}")

                # 读取第一个视频的信息
                if self.auto_read_check.isChecked():
                    self.load_video_info()

            # 获取当前视频信息并上传
            video_path = self.video_path_label.text()
            title = self.title_input.toPlainText().strip()
            if not title:
                raise Exception("请输入视频标题")

            tags = self.tags_input.toPlainText().strip().split()
            if not tags:
                raise Exception("请输入至少一个标签")

            # 获取发布时间
            if self.immediate_radio.isChecked():
                publish_time = 0
            else:
                # 定时发布
                scheduled_time = self.datetime_edit.dateTime()
                current_time = QDateTime.currentDateTime()
                if scheduled_time <= current_time:
                    raise Exception("定时发布时间必须大于当前时间")
                publish_time = scheduled_time.toSecsSinceEpoch()

            # 创建上传工作线程
            self.upload_worker = UploadWorker(
                platform=platform_key,
                account_name=account,
                video_file=video_path,
                publish_time=publish_time,
                title=title,
                tags=tags,
                is_scheduled=self.scheduled_radio.isChecked())
            self.upload_worker.finished.connect(self.on_upload_finished)
            self.upload_worker.progress.connect(self.log_text.append)
            self.upload_worker.start()

        except Exception as e:
            QMessageBox.warning(self, "错误", str(e))
            self.log_text.append(f"❌ 错误：{str(e)}")

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 延迟100毫秒执行初始化检查
        self.init_timer.start(100)

    def delayed_init(self):
        """延迟执行的初始化检查"""
        # 检查视频目录
        self.check_videos_directory()
        # 更新账号列表
        self.update_account_list(show_loading=True)

    def check_videos_directory(self):
        """检查视频目录"""
        videos_dir = Path(BASE_DIR) / "videos"
        if videos_dir.exists():
            video_files = sorted(list(videos_dir.glob("*.mp4")))
            if video_files:
                self.log_text.append("\n=== 检查视频目录 ===")
                self.log_text.append(f"找到 {len(video_files)} 个视频文件：")
                for video in video_files:
                    self.log_text.append(f"- {video.name}")

                # 存储视频队列
                self.video_queue = video_files
                self.current_video_index = 0
                video_path = str(self.video_queue[self.current_video_index])
                self.video_path_label.setText(video_path)
                self.log_text.append(
                    f"\n准备上传第 1/{len(video_files)} 个视频：{video_path}")

                # 延迟100毫秒后尝试读取视频信息
                if self.auto_read_check.isChecked():
                    QTimer.singleShot(
                        100, lambda: self.load_video_info(show_error=True))

    def on_platform_changed(self, platform):
        """平台变更时的处理"""
        # 显示加载提示
        self.account_input.clear()
        self.account_input.addItem("正在加载账号列表...")
        self.account_input.setEnabled(False)

        # 延迟执行账号验证
        QTimer.singleShot(100,
                          lambda: self.update_account_list(show_loading=True))

    def on_login_clicked(self):
        """处理登录按钮点击事件"""
        try:
            platform = self.platform_combo.currentText()
            platform_key = get_platform_key(platform)
            account = self.account_input.currentText()

            self.log_text.append(f"\n=== 开始{platform}登录 ===")
            self.log_text.append(f"正在登录 {platform} 平台，账号：{account}")

            if platform_key == "xhs":
                QMessageBox.information(self, "提示",
                                        "请使用 get_cookies 按钮获取小红书 cookie")
                return
            elif platform_key == "bilibili":
                QMessageBox.information(self, "提示",
                                        "请使用 biliup.exe 获取B站 cookie")
                return
            else:
                # 其他平台使用统一的登录处理
                try:
                    script_path = Path(
                        BASE_DIR) / f"get_{platform_key}_cookie.py"
                    if not script_path.exists():
                        raise Exception(f"未找到登录脚本：{script_path}")

                    self.log_text.append(f"正在执行登录脚本：{script_path.name}")

                    # 使用 Python 执行脚本，实时显示输出
                    process = subprocess.Popen(
                        [sys.executable, str(script_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True)

                    # 读取并显示输出
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            self.log_text.append(output.strip())

                    # 获取返回码和错误信息
                    return_code = process.poll()
                    if return_code != 0:
                        error = process.stderr.read()
                        raise Exception(f"登录脚本执行失败：{error}")

                    self.log_text.append("登录完成，cookie已保存")
                    # 登录完成后更新账号列表
                    self.update_account_list()

                except Exception as e:
                    raise Exception(f"{platform}登录失败：{str(e)}")

        except Exception as e:
            QMessageBox.warning(self, "登录失败", str(e))
            self.log_text.append(f"❌ 登录失败：{str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
