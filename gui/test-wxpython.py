import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(300, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(panel, label="请输入你的名字:")
        vbox.Add(self.label, flag=wx.EXPAND | wx.TOP, border=10)

        self.text_input = wx.TextCtrl(panel)
        vbox.Add(self.text_input, flag=wx.EXPAND | wx.TOP, border=5)

        self.button = wx.Button(panel, label="提交")
        vbox.Add(self.button, flag=wx.EXPAND | wx.TOP, border=10)

        self.button.Bind(wx.EVT_BUTTON, self.on_click)

        panel.SetSizer(vbox)

    def on_click(self, event):
        name = self.text_input.GetValue()
        self.label.SetLabel(f"Hello, {name}!")

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "wxPython 示例")
    frame.Show()
    app.MainLoop()
