import wx
import os
import subprocess
import glob


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(500, 400))

        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # 创建控件：ListBox 显示 Python 文件列表
        self.file_listbox = wx.ListBox(self.panel, size=(300, 200))
        self.sizer.Add(self.file_listbox, flag=wx.EXPAND | wx.TOP, border=10)

        # 创建控件：TextCtrl 显示日志
        self.log_textctrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 150))
        self.sizer.Add(self.log_textctrl, flag=wx.EXPAND | wx.TOP, border=10)

        # 加载文件列表
        self.load_file_list()

        # 绑定事件：点击文件后执行
        self.file_listbox.Bind(wx.EVT_LISTBOX, self.on_file_select)

        # 设置布局
        self.panel.SetSizer(self.sizer)
        self.Show()

    def load_file_list(self):
        # 获取当前目录下 examples 文件夹中的所有 Python 文件
        examples_path = os.path.join(os.getcwd(), "examples")
        python_files = glob.glob(os.path.join(examples_path, "*.py"))

        # 将文件名添加到 ListBox 控件中
        self.file_listbox.SetItems([os.path.basename(f) for f in python_files])

    def on_file_select(self, event):
        # 获取选中的文件名
        selected_file = self.file_listbox.GetStringSelection()
        if selected_file:
            # 获取完整路径
            examples_path = os.path.join(os.getcwd(), "examples")
            file_path = os.path.join(examples_path, selected_file)

            # 清空日志文本框
            self.log_textctrl.Clear()

            # 执行选中的 Python 文件并捕获输出
            self.run_python_file(file_path)

    def run_python_file(self, file_path):
        # 运行 Python 文件并捕获输出
        try:
            # 使用 subprocess 运行文件，并捕获输出
            result = subprocess.run(
                ['python', file_path],
                capture_output=True,
                text=True,
                check=True
            )

            # 将执行日志显示到 TextCtrl 控件
            self.log_textctrl.AppendText(f"执行日志:\n{result.stdout}\n")
            if result.stderr:
                self.log_textctrl.AppendText(f"错误日志:\n{result.stderr}\n")
        except subprocess.CalledProcessError as e:
            # 处理错误，显示错误信息
            self.log_textctrl.AppendText(f"执行失败: {e}\n")
        except Exception as e:
            self.log_textctrl.AppendText(f"发生错误: {e}\n")


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "Python 文件执行器")
    app.MainLoop()
