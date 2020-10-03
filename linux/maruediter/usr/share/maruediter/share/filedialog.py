import os
import tkinter.filedialog as _fd1
if os.name == "posix":
    import tkfilebrowser as _fd2
#from TkinterDnD2 import *
import tkinter
from tkinter import ttk
#import tkdnd

if os.name == "posix":
    mode = 1
else:
    mode = 0

def askdirectory(**argv):
    if mode:
        return _fd2.askopendirname(**argv)
    else:
        return _fd1.askdirectory(**argv)
def askopenfilename(**argv):
    if mode:
        return _fd2.askopenfilename(**argv)
    else:
        return _fd1.askopenfilename(**argv)
def asksaveasfilename(**argv):
    if mode:
        return _fd2.asksaveasfilename(**argv)
    else:
        return _fd1.asksaveasfilename(**argv)
