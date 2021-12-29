import platform
import tkinter.filedialog as _fd1
try:
    import tkfilebrowser as _fd2
except:
    mode=0
else:
    mode=1

#default setting
if platform.system() == "Linux":
    mode = 1
else:
    mode = 0

#tools
#def load_fd2():
    
def chg_mode():
    global mode
    if mode:
        mode = 0
    else:
        mode = 1

#dialogs
def askdirectory(fd=None, **argv):
    if fd == None: fd = mode
    if fd:
        return _fd2.askopendirname(**argv)
    else:
        return _fd1.askdirectory(**argv)

def askopenfilename(fd=None, **argv):
    if fd == None: fd = mode
    if platform.system() == "Darwin":
        #load_fd2()
        return _fd2.askopenfilename(**argv)
    if fd:
        return _fd2.askopenfilename(**argv)
    else:
        return _fd1.askopenfilename(**argv)
def askopenfilenames(fd=None, **argv):
    if fd == None: fd = mode
    if platform.system() == "Darwin":
        #load_fd2()
        return _fd2.askopenfilenames(**argv)
    if fd:
        return _fd2.askopenfilenames(**argv)
    else:
        return _fd1.askopenfilenames(**argv)
def asksaveasfilename(fd=None, **argv):
    if fd == None: fd = mode
    if fd:
        return _fd2.asksaveasfilename(**argv)
    else:
        return _fd1.asksaveasfilename(**argv)
        