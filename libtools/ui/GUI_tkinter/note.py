from . import WidgetBase

class Notebook(WidgetBase):
    def __init__(self, master, parent, command=None, close=None, **options):
        super().__init__(master)
        self.parent=parent
        if close is None:
            from tkinter.ttk import Notebook
            self.widget=Notebook(self.master, **options)
        else:
            from .widgets import CustomNotebook
            self.widget=CustomNotebook(self.master, **options)
        self.widget.enable_traversal()
        if not command is None:
            self.widget.bind("<<NotebookTabClosed>>",lambda null: command)
        self.value=None
        self.widget.bind("<<NotebookTabChanged>>", self.callback)
        self.widget.pack(fill="both", expand=True)
    def add_tab(self, label=""):
        child=self.parent.Frame()
        #child.pack()
        self.widget.add(child=child.root, text=label)
        return child
    def callback(self, event):
        self.value=self.widget.tab(self.widget.index("current"), "text")#select()