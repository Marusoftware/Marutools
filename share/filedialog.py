import platform
import tkinter.filedialog as _fd1
if platform.system() == "Linux":
    import tkfilebrowser as _fd2
#from TkinterDnD2 import *
import tkinter
from tkinter import ttk
#import tkdnd

#default setting
if platform.system() == "Linux":
    mode = 1
else:
    mode = 0

#tools
def load_fd2():
    import tkfilebrowser as _fd2
def chg_mode():
    global mode
    if mode:
        mode = 0
    else:
        mode = 1

#dialogs
def askdirectory(**argv):
    print(argv)
    if mode:
        return _fd2.askopendirname(**argv)
    else:
        return _fd1.askdirectory(**argv)
def askopenfilename(**argv):
    print(argv)
    if mode:
        return _fd2.askopenfilename(**argv)
    else:
        return _fd1.askopenfilename(**argv)
def asksaveasfilename(**argv):
    print(argv)
    if mode:
        return _fd2.asksaveasfilename(**argv)
    else:
        return _fd1.asksaveasfilename(**argv)
