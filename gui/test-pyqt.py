from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit

def on_click():
    label.setText(f"Hello, {text_input.text()}!")

app = QApplication([])

# 创建窗口
window = QWidget()
window.setWindowTitle("PyQt GUI 示例")

# 创建布局
layout = QVBoxLayout()

# 创建标签
label = QLabel("请输入你的名字:")
layout.addWidget(label)

# 创建输入框
text_input = QLineEdit()
layout.addWidget(text_input)

# 创建按钮
button = QPushButton("提交")
button.clicked.connect(on_click)
layout.addWidget(button)

# 设置窗口的布局并显示
window.setLayout(layout)
window.show()

app.exec_()
