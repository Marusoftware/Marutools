#!/usr/bin/python3
import filedialog
from tkinter import messagebox
from tkinter import ttk
import tkinter, random, string, pickle, os, sys, shutil

def randomstr(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
def file_open():
    return 0

class define():
    def GetRandomStr(num):
        import random
        import string
        dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
        return ''.join([random.choice(dat) for i in range(num)])

class edit():
    def get_info(argv):
        if argv == "enable":
            return 1
        if argv == "addon_var":
            return "pre0.0.1beta"
        elif argv == "template_var":
            return "b0.0.1"
        elif argv == "__built_in__":
            return 1
        elif argv == "type":
            return [".hagaki",".fgw"]
        elif argv == "type_ex":
            return "Hagaki(postcard) project file"
        else:
            return 0
    def file_new(open_pas):
        pass

    def file_open(open_path, ofps, master):
        master.open_path = open_path
        master.directory = "./tmp"+define.GetRandomStr(5)
        if not os.path.exists(master.directory):
            os.mkdir(master.directory)
        if ofps == 0:
            pass
        else:
            pass
        return [open_path]
        #open

    def file_save(master, save_other="0"):
        pass
    def file_main(master):
        root = master
        lang_jp = ["ヘルプ","表(宛名)","裏(レイアウト)",""]
        ntbook = ttk.Notebook(root)
        ntbook.pack(fill="both")
        omote = ttk.Frame(root)
        ura = ttk.Frame(root)
        ntbook.add(omote, text="表(宛名)")
        ntbook.add(ura, text="裏(レイアウト)")
        #omote
        omote_menu = ttk.Frame(omote)
        omote_menu.pack(side="left")
        omote_menu_b1 = ttk.Button(omote_menu,text="住所録新規作成")
        omote_menu_b1.pack(side="left")
        omote_menu_b2 = ttk.Button(omote_menu,text="インポート")
        omote_menu_b2.pack(side="left")
        omote_menu_b3 = ttk.Button(omote_menu,text="エクスポート")
        omote_menu_b3.pack(side="left")
        omote_main = ttk.Frame(omote)
        omote_main.pack(fill="both")
        omote_right = ttk.Frame(omote_main)
        omote_right.grid(column=1,row=0,sticky="ns")
        omote_left = ttk.Frame(omote_main)
        omote_left.grid(column=1,row=0,sticky="ns")
        #ura
        ura_menu = ttk.Frame(ura)
        ura_menu.pack(side="left")
        ura_menu_b1 = ttk.Button(ura_menu,text="作品新規作成")
        ura_menu_b1.pack(side="left")
        ura_menu_b2 = ttk.Button(ura_menu,text="インポート")
        ura_menu_b2.pack(side="left")
        ura_menu_b3 = ttk.Button(ura_menu,text="エクスポート")
        ura_menu_b3.pack(side="left")
        ura_main = ttk.Frame(ura)
        ura_main.pack(fill="both")
        ura_right = ttk.Frame(omote_main)
        ura_right.grid(column=1,row=0,sticky="ns")
        ura_left = ttk.Frame(omote_main)
        ura_left.grid(column=1,row=0,sticky="ns")
    def file_exit(master):
        if os.path.exists(master.directory):
            shutil.rmtree(master.directory)
if __name__ == "__main__":
    os.chdir("../")
    master = tkinter.Tk()
    edit.file_open("./test.mvid",0,master)
    edit.file_main(master)
    edit.file_exit(master)
