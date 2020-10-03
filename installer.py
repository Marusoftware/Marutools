#! /usr/bin/python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter import ttk
from tkinter import filedialog
import tkinter.messagebox as tkmsg
import os
import time
import sys
import subprocess

############add APP info here###############
APP_NAME = "maruediter"
APP_NAME_TITLE = "Maruediter"
APP_LUA_JP = [""]
APP_LUA_EN = [""]
APP_TYPE = "32" # 64 , 32 , select
APP_ICON = "./maruediter.png"
APP_VER = "1.0"
APP_COMPANY = "Marusoftare"
############################################

lang = 0
step_v = 0

def bye():
    next_step()
    root.destroy()
    exit()

def next_step():
    global step_v, step
    step_v = step_v + 1
    step.set(step_v)

root = tkinter.Tk(className=APP_NAME+" Installer")
step = tkinter.IntVar()
if os.path.exists(APP_ICON):
    root.iconphoto(True, tkinter.PhotoImage(file=APP_ICON))

step.set(0)
lang_v = tkinter.IntVar()
root.title("Language")
root.protocol("WM_DELETE_WINDOW", bye)
l = ttk.Label(root, text="Please select language when use install.")
l.pack(side="top")
b1 = ttk.Button(root, text='NEXT', command=next_step)
b1.pack(side="bottom")
rb1 = ttk.Radiobutton(text = '日本語', variable = lang_v, value = 0)
rb1.pack()
rb2 = ttk.Radiobutton(text = 'English', variable = lang_v, value = 1)
rb2.pack()
root.wait_variable(step)
root.geometry("500x300")
lang = lang_v.get()
lua_v = tkinter.IntVar()
l2 = tkinter.Listbox(root)
l2.pack()
if lang == 0:
    root.title(APP_NAME_TITLE + " インストーラ")
    rb1.configure(text="許諾", variable = lua_v)
    rb2.configure(text="拒否", variable = lua_v)
    l.configure(text="下記の利用規約をお読みください。")
    for i in range(len(APP_LUA_JP)):
        l2.insert("end", APP_LUA_JP[i])
else:
    root.title(APP_NAME_TITLE + " Installer")
    rb1.configure(text="accept", variable = lua_v)
    rb2.configure(text="ignore", variable = lua_v)
    l.configure(text="Please read LUA.")
    for i in range(len(APP_LUA_EN)):
        l2.insert("end", APP_LUA_EN[i])
root.wait_variable(step)
if lua_v.get() == 1:
    exit()
l2.destroy()
if APP_TYPE == "select":
    type_v = tkinter.IntVar()
    if lang == 0:
        l.configure(text="バージョンを選択してください。")
    else:
        l.configure(text="Please select version.")
    rb1.configure(text="64bit", variable=type_v)
    rb2.configure(text="32bit", variable=type_v)
    root.wait_variable(step)
    if type_v.get() == 0:
        APP_TYPE = "64"
    else:
        APP_TYPE = "32"
else:
    pass
rb1.destroy()
rb2.destroy()
e = ttk.Entry(root)
e.pack()
if os.name == 'nt':
    if APP_TYPE == "64":
        def_dir = os.environ["ProgramW6432"]
    else:
        def_dir = os.environ["ProgramFiles(x86)"]
else:
    def_dir = "/"
e.insert("0",def_dir)
def select():
    e.delete(0,tkinter.END)
    e.insert("0",filedialog.askdirectory(initialdir=def_dir))
    if e.get() == "":
        e.insert("end",def_dir)
if lang == 0:
    b2 = ttk.Button(root, text="選択", command=select)
    l.configure(text="インストール先を選択してください。")
    b1.configure(text="インストール")
else:
    b2 = ttk.Button(root, text="Select", command=select)
    l.configure(text="Please select install directory.")
    b1.configure(text="Install")
b2.pack()
root.wait_variable(step)
i_dir = e.get()
if not os.path.exists(i_dir):
    i_dir = def_dir
i_dir = os.path.join(i_dir,APP_NAME)
print(i_dir)
e.destroy()
b2.destroy()
p = ttk.Progressbar(root, orient="h", length=200, mode='determinate', maximum=100, value=0)
p.pack()
if lang == 0:
    l.configure(text="インストール中です。")
else:
    l.configure(text="Installing.")
b1.config(state="disable")
try:
    if not os.path.exists(i_dir):
        os.mkdir(i_dir)
        p.configure(value=10)
        p.update()
except PermissionError:
    try:
        os.chmod(os.path.dirname(i_dir),777)
        os.mkdir(i_dir)
        p.configure(value=10)
        p.update()
    except PermissionError:
        if os.name == 'nt':
            if lang == 0:
                tkmsg.showerror("エラー","権限エラー:\n管理者権限で実行してください。")
                exit()
            else:
                tkmsg.showerror("Error","PermissionError:\nPlease run in administer.")
                exit()
        else:
            if lang == 0:
                tkmsg.showerror("エラー","権限エラー:\nroot権限で('sudo'を付けて)再実行してください。")
                exit()
            else:
                tkmsg.showerror("Error","PermissionError:\nPlease run in root.(add 'sudo')")
                exit()
############add install command here#########
root.wait_variable(step)
#############################################
p.configure(value=100)
p.update()
if lang == 0:
    l.configure(text="完了しました。")
    b1.configure(text="終了")
else:
    l.configure(text="Done.")
    b1.configure(text="Exit")
b1.config(state="active")
root.wait_variable(step)
exit()
root.mainloop()
