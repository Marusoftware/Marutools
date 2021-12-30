from . import WidgetBase

class Input(WidgetBase):
    pass

class Button(WidgetBase):
    def __init__(self, master, label, **options):
        super().__init__(master)
        from tkinter import Button
        self.button=Button(self.master, text=label, **options)
        self.button.pack(expand=True, fill="both")
class List(WidgetBase):
    def __init__(self, master, label, **options):
        super().__init__(master)
        from tkinter.ttk import Treeview
        self.list=Treeview(self.master, **options)
        self.list.pack(expand=True, fill="both")
        self.category=[]
    def add_category(self):
        pass
    def add_item(self):
        pass