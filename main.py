from re import sub
from threading import Thread
from time import sleep

import yaml
from pyperclip import copy, paste
from win32gui import GetClassName, GetForegroundWindow, GetWindowText
from wx import App, EVT_CLOSE, EVT_MENU, Frame, Icon, Menu, NewIdRef
from wx.adv import TaskBarIcon


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, frame: Frame):
        super(MyTaskBarIcon, self).__init__()
        self.frame = frame
        self.ICON_WORK = "working.png"
        self.ICON_STOP = "stop.png"
        self.ID_ABOUT = NewIdRef()
        self.ID_EXIT = NewIdRef()
        self.ID_RUN = NewIdRef()
        self.ID_STOP = NewIdRef()
        self.TITLE = "clipboard_manager"
        self.recent_value = ""
        self.stop_flag = False
        self.t1 = Thread(target=self.clipboard_manager, args=())
        self.SetIcon(Icon(self.ICON_WORK), self.TITLE)
        self.Bind(EVT_MENU, self.on_exit, id=self.ID_EXIT)
        self.Bind(EVT_MENU, self.on_run, id=self.ID_RUN)
        self.Bind(EVT_MENU, self.on_stop, id=self.ID_STOP)

        with open("./target.yaml", "r", encoding="utf-8") as f:
            self.target = yaml.load(f.read(), Loader=yaml.FullLoader)
        self.t1.start()

    def on_exit(self, event):
        if self.t1.is_alive():
            self.stop_flag = True
        self.frame.Close()

    def on_run(self, event):
        self.stop_flag = False
        self.SetIcon(Icon(self.ICON_WORK), self.TITLE)
        if self.t1.is_alive():
            pass
        else:
            self.t1 = Thread(target=self.clipboard_manager, args=())
            self.t1.start()

    def on_stop(self, event):
        self.stop_flag = True
        self.SetIcon(Icon(self.ICON_STOP), self.TITLE)

    def CreatePopupMenu(self):
        menu = Menu()
        for mentAttr in self.get_menu_attrs():
            menu.Append(mentAttr[1], mentAttr[0])
        return menu

    def get_menu_attrs(self):
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
                    current_window = GetForegroundWindow()
                    cw_title = GetWindowText(current_window)
                    cw_classname = GetClassName(current_window)
                    if any(t_classname in cw_classname for t_classname in self.target["classname"]) or any(
                            t_title in cw_title for t_title in self.target["title"]):
                        tmp_value = sub("( +)|((\r\n)+)", " ", paste())  # 读取剪切板复制的内容并删掉换行符
                        # changed = out = re.sub(r"\s{2,}", " ", recent_value)  # 将文本的换行符去掉，变成一个空格
                        copy(tmp_value)  # 将修改后的文本写入系统剪切板中
                        print("\n Value changed: %s" % str(tmp_value))  # 输出已经去除换行符的文本
                    recent_value = tmp_value
                sleep(0.2)
            except KeyboardInterrupt:  # 如果有ctrl+c，那么就退出这个程序。  （不过好像并没有用。无伤大雅）
                break

            if self.stop_flag:
                print("receive stop flag")
                break


class MyFrame(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.myapp = MyTaskBarIcon(self)  # 显示系统托盘图标
        self.Bind(EVT_CLOSE, self.on_close)

    def on_close(self, event):
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