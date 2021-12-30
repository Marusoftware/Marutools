from . import WidgetBase

class Dialog(WidgetBase):
    def askfile(self, multi=False, save=False, **options):
        from .filedialog import askopenfilename, askopenfilenames, asksaveasfilename
        if save:
            return asksaveasfilename(**options)
        else:
            if multi:
                return askopenfilenames(**options)
            else:
                return askopenfilename(**options)
    def askdir(self, **options):
        from .filedialog import askdirectory
        return askdirectory(**options)
    def error(self, **options):
        from tkinter.messagebox import showerror
        return showerror(**options)
    def info(self, **options):
        from tkinter.messagebox import showinfo
        return showinfo(**options)
    def warn(self, **options):
        from tkinter.messagebox import showwarning
        return showwarning(**options)
    def question(self, type, title, message, **options):
        from tkinter.messagebox import askokcancel, askretrycancel, askyesno, askyesnocancel
        if type=="okcancel":
            return askokcancel(title=title, message=message, **options)
        elif type=="retrycancel":
            return askretrycancel(title=title, message=message, **options)
        elif type=="yesno":
            return askyesno(title=title, message=message, **options)
        elif type=="yesnocancel":
            return askyesnocancel(title=title, message=message, **options)
        elif type=="text":
            from tkinter.simpledialog import askstring
            return askstring(title=title, prompt=message, **options)