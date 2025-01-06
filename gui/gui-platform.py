import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, \
    QFrame
from PyQt6.QtGui import QColor

# 导入各个模块的界面类
# 账号管理模块，用于管理用户账号和状态
from account_management import AccountManagementUI
# 作品查看模块，用于展示用户的作品列表和相关信息
from work_viewing import WorkViewingUI
# 作品发布模块，用于选择目录并发布作品
from work_publishing import WorkPublishingUI


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # 调用父类 QMainWindow 的初始化方法
        self.setWindowTitle("Modular Application")  # 设置主窗口标题
        self.setFixedSize(1080, 720)  # 设置窗口大小：宽度 1080，高度 720

        # 创建主窗口小部件并设置布局
        main_widget = QWidget()  # 创建一个 QWidget 作为主窗口的中央部件
        self.setCentralWidget(main_widget)  # 设置主窗口的中央部件
        layout = QVBoxLayout()  # 创建一个垂直布局
        main_widget.setLayout(layout)  # 将布局应用到主窗口的中央部件

        # 创建水平布局来放置按钮
        button_layout = QHBoxLayout()  # 创建一个水平布局
        layout.addLayout(button_layout)  # 将按钮布局添加到主布局的顶部

        # 创建切换模块的按钮
        self.account_button = QPushButton("账号管理")  # 创建一个按钮，显示“账号管理”
        self.work_view_button = QPushButton("作品管理")  # 创建一个按钮，显示“作品管理”
        self.work_publish_button = QPushButton("一键发布")  # 创建一个按钮，显示“一键发布”

        # 将按钮添加到水平布局中
        button_layout.addWidget(self.account_button)
        button_layout.addWidget(self.work_view_button)
        button_layout.addWidget(self.work_publish_button)

        # 添加一条横向分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)  # 设置为横向线
        separator.setFrameShadow(QFrame.Shadow.Sunken)  # 设置阴影效果
        layout.addWidget(separator)  # 将分隔线添加到主布局

        # 创建堆叠小部件，用于切换显示不同的模块页面
        self.stacked_widget = QStackedWidget()  # 创建 QStackedWidget 实例
        layout.addWidget(self.stacked_widget)  # 将堆叠小部件添加到主布局中

        # 创建各个模块的界面实例，并添加到堆叠小部件中
        self.account_ui = AccountManagementUI()  # 创建账号管理模块界面实例
        self.work_view_ui = WorkViewingUI()  # 创建作品查看模块界面实例
        self.work_publish_ui = WorkPublishingUI()  # 创建作品发布模块界面实例

        self.stacked_widget.addWidget(self.account_ui)  # 将账号管理模块界面添加到堆叠小部件
        self.stacked_widget.addWidget(self.work_view_ui)  # 将作品查看模块界面添加到堆叠小部件
        self.stacked_widget.addWidget(self.work_publish_ui)  # 将作品发布模块界面添加到堆叠小部件

        # 设置 UI 样式
        self.set_ui_styles()

        # 默认显示账号管理模块
        self.show_account_management()

        # 连接按钮的点击信号到对应的槽函数
        self.account_button.clicked.connect(self.show_account_management)  # 点击按钮切换到账号管理模块
        self.work_view_button.clicked.connect(self.show_work_viewing)  # 点击按钮切换到作品查看模块
        self.work_publish_button.clicked.connect(self.show_work_publishing)  # 点击按钮切换到作品发布模块

    def set_ui_styles(self):
        """
        设置整个 UI 的样式，包括背景色、按钮样式等
        """
        # 设置窗口背景色为淡紫色
        palette = self.palette()
        palette.setColor(self.palette().ColorRole.Window, QColor(230, 180, 255))  # 淡紫色
        self.setPalette(palette)

        # 设置按钮的样式
        button_style = """
        QPushButton {
            background-color: #b19cd9;  # 淡紫色背景
            color: white;
            border-radius: 15px;  # 更圆的按钮角
            padding: 15px 30px;  # 增加按钮的内边距
            font-size: 18px;  # 增大文字
            font-weight: bold;
            min-width: 200px;  # 设置按钮的最小宽度
        }
        QPushButton:hover {
            background-color: #9b7cd4;  # 悬停时的颜色
        }
        QPushButton:pressed {
            background-color: #8e66b0;  # 按下时的颜色
        }
        """
        self.account_button.setStyleSheet(button_style)
        self.work_view_button.setStyleSheet(button_style)
        self.work_publish_button.setStyleSheet(button_style)

        # 设置选中的按钮样式
        selected_button_style = """
        QPushButton:checked {
            background-color: #a8a8a8;  # 选中的按钮背景色为灰色
            color: black;  # 文字颜色变为黑色
            font-size: 20px;  # 选中时文字放大
            font-weight: bold;
        }
        """
        self.account_button.setStyleSheet(button_style + selected_button_style)
        self.work_view_button.setStyleSheet(button_style + selected_button_style)
        self.work_publish_button.setStyleSheet(button_style + selected_button_style)

        # 设置当前按钮选中的样式
        current_button_style = """
        QPushButton.current {
            background-color: #4f85d1;  # 当前选中按钮背景色为蓝色
            color: white;  # 文字颜色为白色
            font-size: 20px;  # 选中时文字放大
            font-weight: bold;
        }
        """
        self.account_button.setStyleSheet(button_style + current_button_style)
        self.work_view_button.setStyleSheet(button_style + current_button_style)
        self.work_publish_button.setStyleSheet(button_style + current_button_style)

    def show_account_management(self):
        """
        切换到账号管理模块
        """
        self.stacked_widget.setCurrentWidget(self.account_ui)  # 设置堆叠小部件的当前页面为账号管理模块
        self.set_button_checked(self.account_button)

    def show_work_viewing(self):
        """
        切换到作品查看模块
        """
        self.stacked_widget.setCurrentWidget(self.work_view_ui)  # 设置堆叠小部件的当前页面为作品查看模块
        self.set_button_checked(self.work_view_button)

    def show_work_publishing(self):
        """
        切换到作品发布模块
        """
        self.stacked_widget.setCurrentWidget(self.work_publish_ui)  # 设置堆叠小部件的当前页面为作品发布模块
        self.set_button_checked(self.work_publish_button)

    def set_button_checked(self, button):
        """
        设置按钮的选中状态，其他按钮恢复未选中状态
        """
        self.account_button.setChecked(False)
        self.work_view_button.setChecked(False)
        self.work_publish_button.setChecked(False)

        # 重置所有按钮的背景色
        self.account_button.setStyleSheet(self.account_button.styleSheet().replace("background-color: #4f85d1;", ""))
        self.work_view_button.setStyleSheet(
            self.work_view_button.styleSheet().replace("background-color: #4f85d1;", ""))
        self.work_publish_button.setStyleSheet(
            self.work_publish_button.styleSheet().replace("background-color: #4f85d1;", ""))

        # 设置选中的按钮为选中状态
        button.setChecked(True)
        button.setStyleSheet(button.styleSheet() + "background-color: #4f85d1;")  # 设置选中按钮为蓝色


if __name__ == "__main__":
    # 创建应用程序实例
    app = QApplication(sys.argv)  # 初始化 QApplication，传入命令行参数
    main_window = MainWindow()  # 创建主窗口实例
    main_window.show()  # 显示主窗口
    sys.exit(app.exec())  # 运行应用程序的主循环，并在结束时退出
