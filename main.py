from re import sub
import time
from threading import Thread
from pyperclip import copy, paste
from wx import Frame, NewIdRef, Icon, EVT_MENU, Menu, EVT_CLOSE, App
from wx.adv import TaskBarIcon


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, frame: Frame):
        super(MyTaskBarIcon, self).__init__()
        self.frame = frame
        self.ICON = "logo.ico"
        self.ID_ABOUT = NewIdRef()
        self.ID_EXIT = NewIdRef()
        self.ID_RUN = NewIdRef()
        self.ID_STOP = NewIdRef()
        self.TITLE = "clipboard_manager"
        self.recent_value = ""
        self.stop_flag = False
        self.t1 = Thread(target=self.clipboard_manager, args=())
        self.SetIcon(Icon(self.ICON), self.TITLE)
        self.Bind(EVT_MENU, self.onExit, id=self.ID_EXIT)
        self.Bind(EVT_MENU, self.onRun, id=self.ID_RUN)
        self.Bind(EVT_MENU, self.onSTOP, id=self.ID_STOP)
        self.t1.start()

    def onExit(self, event):
        if self.t1.is_alive():
            self.stop_flag = True
        self.frame.Close()

    def onRun(self, event):
        self.stop_flag = False
        if self.t1.is_alive():
            pass
        else:
            self.t1 = Thread(target=self.clipboard_manager, args=())
            self.t1.start()

    def onSTOP(self, event):
        self.stop_flag = True

    def CreatePopupMenu(self):
        menu = Menu()
        for mentAttr in self.getMenuAttrs():
            menu.Append(mentAttr[1], mentAttr[0])
        return menu

    def getMenuAttrs(self):
        return [
            ('运行', self.ID_RUN),
            ('停止', self.ID_STOP),
            ('退出', self.ID_EXIT)]

    def clipboard_manager(self):
        recent_value = ""
        while True:
            tmp_value = paste()  # 读取剪切板复制的内容
            try:
                if tmp_value != recent_value:  # 如果检测到剪切板内容有改动，那么就进入文本的修改
                    tmp_value = sub("( +)|((\r\n)+)", " ", paste())  # 读取剪切板复制的内容并删掉换行符
                    recent_value = tmp_value
                    # changed = out = re.sub(r"\s{2,}", " ", recent_value)  # 将文本的换行符去掉，变成一个空格
                    copy(recent_value)  # 将修改后的文本写入系统剪切板中
                    print("\n Value changed: %s" % str(recent_value))  # 输出已经去除换行符的文本
                time.sleep(0.1)
            except KeyboardInterrupt:  # 如果有ctrl+c，那么就退出这个程序。  （不过好像并没有用。无伤大雅）
                break

            if self.stop_flag:
                print("recieve stop flag")
                break


class MyFrame(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.myapp = MyTaskBarIcon(self)  # 显示系统托盘图标
        self.Bind(EVT_CLOSE, self.onClose)

    def onClose(self, evt):
        self.myapp.RemoveIcon()
        self.myapp.Destroy()
        self.Destroy()


class MyApp(App):
    def OnInit(self):
        MyFrame()
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
