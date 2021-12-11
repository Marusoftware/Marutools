import os
import pickle
import tkinter
from tkinter import ttk
import array
import numpy

class edit():
    def get_info(argv):
        if argv == "enable":
            return 1
        if argv == "addon_var":
            return 0
        elif argv == "template_var":
            return "b0.0.3"
        elif argv == "__built_in__":
            return 0
        elif argv == "type":
            return ".pickle"
        elif argv == "type_ex":
            return "pickle file"
        else:
            return 0
    def file_new(open_pas):
        pass

    def file_open(open_path, ofps, master):
        master.open_path = open_path
        if os.path.exists(master.open_path):
            master.doc = pickle.load(open(master.open_path,"rb"))
        if type(master.doc) == dict:
            master.mode = "dict"
        elif type(master.doc) == int:
            master.mode = "int"
        elif type(master.doc) == list or array.array or numpy.array:
            master.mode = "list"
        elif type(master.doc) == tuple:
            master.mode = "tuple"
        else:
            master.mode = "str"
            master.t.insert("end",)
        return [open_path]

    def file_save(master):
        if os.path.exists(master.open_path):
            os.remove(master.open_path)
        pickle.dump(master.t.get('1.0', 'end -1c'),open(master.open_path,"wb"))
        
    def file_main(master):
        def dic(master):
            master.dic = tkinter.Tk(className="Maruediter")
            master.dic.title("Maruediter")
            master.dic.bt1 = ttk.Button(master.dic, text="ADD")
            master.dic.bt2 = ttk.Button(master.dic, text="DEL")
            master.dic.bt3 = ttk.Button(master.dic, text="EDIT")
            master.dic.lb1 = tkinter.Listbox(master.dic)
            master.dic.lb2 = tkinter.Listbox(master.dic)
            master.dic.bt1.grid(column=2,row=0)
            master.dic.bt2.grid(column=2,row=1)
            master.dic.bt3.grid(column=2,row=2)
            master.dic.lb1.grid(column=0,row=0,sticky='ns',rowspan=3)
            master.dic.lb2.grid(column=1,row=0,sticky='ns',rowspan=3)
        master.t = tkinter.Text(master)
        master.f = ttk.Frame(master)
        master.f.bt1 = ttk.Button(master.f, text="dictionary",command=lambda: dic(master))
        master.f.pack()
        master.f.bt1.pack()
        master.t.pack()
        
    def file_exit(master):
        pass
