__all__=["GUI", "TUI", "WEB", "UI"]

def UI(conf, logger):
    return GUI(conf, logger)

def GUI(conf, logger, library="auto"):
    from .GUI_tkinter import TKINTER
    return TKINTER()

def TUI():
    pass

def WEB():
    pass