__all__=["GUI","TUI","WEB"]

def GUI(library="auto"):
    from .GUI_tkinter import TKINTER
    return TKINTER()

def TUI():
    pass

def WEB():
    pass