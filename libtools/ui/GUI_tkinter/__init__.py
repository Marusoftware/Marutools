import os
from libtools.exception import UIError
from libtools.ui.GUI_tkinter.menu import Menu as _Menu

class TKINTER():
    def __init__(self, config, logger):
        self.logger=logger
        self.config=config
        self.conf=config.conf
        self.appinfo=config.appinfo
        self.backend="tkinter"
        try:
            import tkinter
        except:
            self.appinfo["GUI"]=False
            raise UIError("GUI is not supported")
        os.environ['TKDND_LIBRARY'] = os.path.join(self.appinfo["share_os"],"tkdnd")
        try:
            from .tkdnd import Tk
        except Exception as e:
            self.logger.exception(e)
            from tkinter import Tk
            self.dnd = False
        else:
            self.dnd = True
        self.root=Tk(className=self.appinfo["appname"])
        #ttkthemes
        try:
            from ttkthemes import ThemedStyle as Style
        except:
            from tkinter.ttk import Style
        try:
            self.root.style = Style()
        except:
            from tkinter.ttk import Style as oStyle
            self.root.style = oStyle()
        self.root.report_callback_exception=self.tkerror
        self.changeTitle(self.appinfo["appname"])
        if "theme" in self.conf:
            self.changeStyle(self.conf["theme"])
        self.aqua=(self.appinfo["os"] == "Darwin" and self.root.tk.call('tk', 'windowingsystem') == "aqua")
    def changeTitle(self, title):
        self.root.title(title)
    def changeStyle(self, name):
        self.root.style.theme_use(name)
        self.logger.info("Theme:"+self.conf["theme"])
    def changeIcon(self, icon_path):
        from PIL import Image, ImageTk
        icon=ImageTk.PhotoImage(Image.open(icon_path))
        self.root.iconphoto(True, icon)
    def tkerror(self, exception, value, t):
        import tkinter
        sorry = tkinter.Toplevel()
        sorry.title("Marueditor - Error")
        tkinter.Label(sorry,text="We're sorry.\n\nError is happen.").pack()
        t = tkinter.Text(sorry)
        t.pack()
        t.insert("end","Error report=========\n")
        t.insert("end",str(exception)+"\n")
        t.insert("end",str(value)+"\n")
        t.insert("end",str(t)+"\n")
        tkinter.Button(sorry, text="EXIT", command=sorry.destroy).pack()
        #sorry.protocol("WM_DELETE_WINDOW",sorry.destroy)
    def main(self):
        try:
            from tkinter.scrolledtext import ScrolledText
        except:
            from .scrolledtext import ScrolledText
        from .widgets import CustomNotebook
        import tkinter.simpledialog as sdg
        import tkinter.ttk as ttk
        import tkinter.messagebox as tkmsg
        from . import filedialog
    def setcallback(self, name, callback):
        if name=="close":
            self.root.protocol("WM_DELETE_WINDOW", callback)
            if self.aqua:
                self.root.createcommand('tk::mac::Quit', callback)
        elif name=="macos_help" and self.aqua:
            self.root.createcommand('tk::mac::ShowHelp', callback)
        elif name=="macos_settings" and self.aqua:
            self.root.createcommand('tk::mac::ShowPreferences')
    def Menu(self, **options):
        return _Menu(self.root, **options)