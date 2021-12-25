import os, traceback
from libtools.exception import UIError

class TKINTER():
    def __init__(self, setup_info, logger):
        self.setup_info=setup_info
        self.logger=logger
        try:
            import tkinter
        except:
            self.setup_info["GUI"]=False
            raise UIError("GUI is not supported")
        if self.setup_info["GUI_tkdnd"]:
            os.environ['TKDND_LIBRARY'] = os.path.join(self.setup_info["share_os"],"tkdnd")
        try:
            from .tkdnd import Tk
        except Exception as e:
            self.logger.exception(e)
            from tkinter import Tk
            self.setup_info["GUI_tkdnd"] = False
        else:
            self.setup_info["GUI_tkdnd"] = True
        self.root=Tk(className=setup_info["appname"])
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
    def setStyle(self, name):
        self.root.style.theme_use(name)
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
        from PIL import Image, ImageTk
