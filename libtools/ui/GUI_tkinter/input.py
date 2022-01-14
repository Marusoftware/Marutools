from . import WidgetBase
import os

class _Button(WidgetBase):
    def __init__(self, master, label, **options):
        super().__init__(master)
        from tkinter.ttk import Button
        if not "command" in options:
            from tkinter import IntVar
            self.var=IntVar(master=self.master, value=0)
            options["command"]=lambda: self.var.set(self.var.get()+1)
            self.widget=Button(self.master, text=label, **options)
        else:
            self.var=None
            self.widget=Button(self.master, text=label, **options)
    def wait(self):
        if self.var is None:
            return
        self.widget.wait_variable(self.var)
    def release(self):
        if self.var is None:
            return
        self.var.set(self.var.get()+1)
class _Form(WidgetBase):
    def __init__(self, master, parent, type="text", **options):
        from tkinter.ttk import Entry
        super().__init__(master, parent=parent)
        if type=="password":
            options.update(show="●")
        if type=="file":
            def on_press(event=None):
                if event is None:
                    file=self.parent.Dialog.askfile()
                    if not os.path.exists(file):
                        return
                else:
                    file=event.data
                self.widget.form.insert("end", file)
            self.widget=parent.Frame()
            self.widget.setup_dnd(on_press, "file")
            self.widget.form=Entry(self.widget.root, **options)
            self.widget.form.pack(fill="both", side="left", expand=True)
            from tkinter.ttk import Button
            self.widget.button=Button(self.widget.root, text="Select...", command=on_press)
            self.widget.button.pack(side="right")
        else:
            self.widget=Entry(self.master, **options)
class _List(WidgetBase):
    def __init__(self, master, **options):
        super().__init__(master)
        from tkinter.ttk import Treeview
        self.widget=Treeview(self.master, show="tree", **options)
        self.widget.bind("<<TreeviewSelect>>", self.callback)
        self.value=()
    def set_header(self, column, text):
        self.widget.heading("#"+str(column), text=text)
    def add_item(self, parent="", index=0, id=None, label="", values=None, **options):
        if not id is None:
            options.update(iid=id)
        if not values is None:
            options.update(values=values)
        self.widget.insert(parent=parent, index=index, text=label, **options)
    def callback(self, event):
        self.value=self.widget.selection()
    def set_selection(self, items):
        self.value=items
        self.widget.selection_set(items)
class Input(WidgetBase):
    def Button(self, **options):
        return _Button(self.master, **options)
    def List(self, **options):
        return _List(self.master, **options)
    def Form(self, **options):
        return _Form(self.master, self.parent, **options)