import os, traceback
from .exception import UIError

class TKINTER():
    def __init__(self, setup_info, endnd=False):
        try:
            import tkinter
        except:
            raise UIError("GUI is not supported")
        if endnd:
            os.environ['TKDND_LIBRARY'] = os.path.join(setup_info["share_os"],"tkdnd")
        try:
            from tkdnd import Tk
        except:
            from tkinter import Tk
            setup_info.update(gui_dnd = False)
            traceback.print_exc()
        else:
            setup_info.update(gui_dnd = True)
        #ttkthemes
        try:
            from ttkthemes import ThemedStyle as Style
        except:
            from tkinter.ttk import Style
        from custom_note import CustomNotebook
        import tkinter.simpledialog
        import tkinter.ttk as ttk
        import tkinter.messagebox as tkmsg
        import filedialog as filedialog
        from scrolledtext import ScrolledText
        from PIL import Image, ImageTk
        self.root=Tk()
    def main(self):
        pass
