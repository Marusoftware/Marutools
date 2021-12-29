from tkinter import Menu as _Menu
from tkinter.ttk import Menubutton, OptionMenu
import platform

import libtools

class Menu():
    def __init__(self, master, type, aqua=False, **options):
        self.type=type
        self.master=master
        self.aqua=aqua
        if type=="bar":
            self.children={}
            self.master.config(menu=self.menu)
            self.menu=_Menu(master=master, **options)
        elif type=="bar_child":
            self.menu=_Menu(master=master, **options)
            self.master.add_cascade(menu=self.menu)
        elif type=="popup":
            pass
        elif type=="button":
            pass
        elif type == "menu":
            self.menu=Menubutton(master=master, **options)
        elif type == "menubutton":
            self.menu=OptionMenu(master=master, **options)
    def add_category(self, label, name=None, **options):
        if name is None:
            name=label
        if self.type == "bar":
            if name=="apple":
                if self.aqua:
                    pass
            elif name=="system":
                if platform.system()=="Windows":
                    pass
            self.children[name]=Menu(self.menu, "bar_child", name=name, **options)
        elif self.type == "bar_child":
            self.children[name]=Menu(self.menu, "bar_child", name=name, **options)
        return self.children[name]
    def add_item(self, type, accelerator=None, command=None, child=None, bind=True, **options):
        if self.type == "bar":
            if child is None:
                menu=self.menu
            else:
                menu=self.children[child]
        elif self.type == "bar_child":
            menu=self.menu
        if not command is None:
            options["command"]=command
        if not accelerator is None and not command is None:
            options["accelerator"]="+".join(accelerator)
            if bind:
                event=""
                for i in accelerator:
                    if len(i) == 1:
                        event+=("KeyPress-"+i)
                    else:
                        event=(i+event)
                self.master.bind(f"<{event}>", command)
        if type=="button":
            menu.add_command(**options)
        elif type=="checkbutton":
            menu.add_checkbutton(**options)
        elif type=="radiobutton":
            menu.add_radiobutton(**options)
        elif type=="separator":
            menu.add_separator(**options)