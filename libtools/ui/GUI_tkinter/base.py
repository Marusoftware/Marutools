from . import WidgetBase

class Label(WidgetBase):
    def __init__(self, master, **options):
        super().__init__(master=master)
        from tkinter.ttk import Label
        self.widget=Label(self.master, **options)
