import os
import pickle
import tkinter
from tkinter import ttk
from . import chardet

class edit():
    def get_info(argv):
        if argv == "enable":
            return 1
        elif argv == "addon_var":
            return 0
        elif argv == "template_var":
            return "b0.0.3"
        elif argv == "__built_in__":
            return 1
        elif argv == "type":
            return ".txt"
        elif argv == "type_ex":
            return "text file"
        else:
            return 0
    def file_new(open_pas):
        pass

    def file_open(open_path, ofps, master):
        master.open_path = open_path
        return [open_path]

    def file_save(master, save_other="0"):
        if save_other == "0":
            if os.path.exists(master.open_path):
                os.remove(master.open_path)
            o = open(master.open_path,"w")
            o.write(master.t.get('1.0', 'end -1c'))
            o.close()
        else:
            if os.path.exists(save_other):
                os.remove(save_other)
            o = open(save_other,"w")
            o.write(master.t.get('1.0', 'end -1c'))
            o.close()
        
        
    def file_main(master):
        master.t = tkinter.Text(master)
        master.t.pack(fill="both",expand=True)
        if os.path.exists(master.open_path):
            
            master.t.insert("end",open(master.open_path,"r",encoding=chardet.detect(open(master.open_path,"rb").read())["encoding"]).read())
        
    def file_exit(master):
        pass
