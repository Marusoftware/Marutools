#! /usr/bin/python3
print("[info] import core libraly")
import sys
import os
import tkinter
import platform
sys.dont_write_bytecode = True
cd = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(cd)
sys.path.append(os.path.join(cd,"share"))
is64bit = sys.maxsize > 2 ** 32
if os.name == "nt":
    if is64bit:
        sys.path.append(os.path.join(cd,"share_os","win64"))
        os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","win64","tkdnd")
    else:
        sys.path.append(os.path.join(cd,"share_os","win32"))
        os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","win32","tkdnd")
elif os.name == "posix":
    if is64bit:
        sys.path.append(os.path.join(cd,"share_os","linux64"))
        os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","linux64","tkdnd")
    else:
        if platform.machine() == "armv7":
            sys.path.append(os.path.join(cd,"share_os","linux32"))
            os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","linux32","tkdnd")
        else:
            sys.path.append(os.path.join(cd,"share_os","linux32"))
            os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","linux32","tkdnd")
else:
    sys.path.append(os.path.join(cd,"share_os","macos"))
    os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","macos","tkdnd")
print("[info] import additional libraly")
import tkinter.filedialog
try:
    from tkdnd import *
    en_dnd = True
except:
    from tkinter import Tk
    en_dnd = False
try:
    from ttkthemes import ThemedStyle as Style
except:
    from tkinter.ttk import Style
from custom_note import CustomNotebook
from importlib import import_module
import tkinter.messagebox as tkmsg
import filedialog as filedialog
#from tkfontchooser import askfont
import tkinter.simpledialog
import tkinter.ttk as ttk
#from pathlib import Path
import urllib.request
import subprocess
import file_addon
import gui_addon
import threading
import datetime
import getpass
import shutil
import pickle
import media
import random
import string
import locale
import random
import string
import time
try:
    print("[info] start")
    
    #import file addon
    file_addon_list = file_addon.get()
    file_addons = []
    file_addon_type = []
    file_addon_type_ex = []
    tmp = ""
    history = []
    info = ["ver=b0.1","rever=0"]
    openning = []
    tema = 0
    saved = 0
    
    while 1:
        if len(file_addons) < len(file_addon_list):
            try:
                file_addons.append(import_module("." + file_addon_list[len(file_addons)], "file_addon").edit)
            except:
                print("Error is huppun in progress on import addon.\nNow in restarting.")
                if "--debug" in sys.argv:
                    import traceback
                    print("error report=====\n"+traceback.format_exc())
                file_addon.remove(file_addon.get_file()[len(file_addons)])
                time.sleep(1)
                os.chdir(cd)
                subprocess.Popen([sys.argv[0]], shell=True)
                exit(-1)
            else:
                try:
                    if file_addons[-1].get_info("enable") == 0:
                        raise
                    if type(file_addons[-1].get_info("type")) == str:
                        file_addon_type.append(file_addons[-1].get_info("type"))
                        file_addon_type_ex.append(file_addons[-1].get_info("type_ex"))
                    elif type(file_addons[-1].get_info("type")) == list:
                        if type(file_addons[-1].get_info("type_ex")) == list:
                            if len(file_addons[-1].get_info("type")) == len(file_addons[-1].get_info("type_ex")):
                                for i in range(len(file_addons[-1].get_info("type"))):
                                    file_addon_list.append(file_addon_list[-1])
                                    file_addon_type.append(file_addons[-1].get_info("type")[i])
                                    file_addons.append(file_addons[-1])
                                    file_addon_type_ex.append(file_addons[-1].get_info("type_ex")[i])
                            else:
                                file_addon_type.append(file_addons[-1].get_info("type"))[0]
                                file_addon_type_ex.append(file_addons[-1].get_info("type_ex"))[0]
                        else:
                            file_addon_type.append(file_addons[-1].get_info("type")[0])
                            file_addon_type_ex.append(file_addons[-1].get_info("type_ex"))
                    else:
                        file_addon_list.pop(len(file_addons)-1)
                        file_addons.pop(len(file_addons)-1)
                    if file_addons[len(file_addons)-1].get_info("__built_in__"):
                        pass
                except:
                    file_addon_list.pop(len(file_addons)-1)
                    file_addons.pop(len(file_addons)-1)
        else:
            break

    print("[info] loaded addon:" + str(file_addon_list))
    print("[info] loaded addon type:" + str(file_addon_type))
    print("[info] loaded addon module:" + str(file_addons))

    #current directory
    os.chdir(cd)
    
    #load conf
    #conf_path = "./"+ getpass.getuser() + "maruediter.conf"
    if os.name == "posix":
        conf_path = os.path.join(os.path.expanduser("~"),".config","maruediter",getpass.getuser()+ "maruediter.conf")
        os.makedirs(os.path.dirname(conf_path),exist_ok=True)
    elif os.name == "nt":
        conf_path = os.path.join(os.path.expanduser("~"),"Appdata","maruediter",getpass.getuser()+ "maruediter.conf")
        os.makedirs(os.path.dirname(conf_path),exist_ok=True)
    else:
        conf_path = "./"+ getpass.getuser() + "maruediter.conf"
    if os.path.exists(conf_path):
        try:
            conf = pickle.load(open(conf_path,"rb"))
        except:
            os.remove(conf_path)
        first = 0
    else:
        conf = {}
        conf.update(welcome=1)
        if os.name == "nt":
            conf.update(theme="winnative")
        else:
            conf.update(theme="default")
        if None in locale.getlocale():
            conf.update([("lang",locale.getlocale()[0]),("encode",locale.getlocale()[1])])
        else:
            conf.update([("lang",locale.getdefaultlocale()[0]),("encode",locale.getdefaultlocale()[1])])
        if conf["lang"] == None:
            conf.update(lang="ja_JP")
        pickle.dump(conf,open(conf_path,"wb"))
        first = 1
    
    if "lang" in conf:
        print("[info] Language:"+conf["lang"])
        req = ["maruediter","welcome","exit","close_all","close_tab","save","save_as","open_from","open","new","file","open_new","full_screen","version","help",
               "window","setting","addon","file_addon","delete","maruediter_file","all","error","error_cant_open","select_file_type","next","check","save_check",
               "were_sorry","new_main","back","cancel","dir_name","file_name","choose_dir","file_name","new_sub1","new_sub2","new_check","wait","done","new_e1",
               "new_e2","new_e3","done_msg","new_e1_msg"]
        if os.path.exists("./language/"+conf["lang"]+".lang"):
            txt = pickle.load(open("./language/"+conf["lang"]+".lang","rb"))
            #print(txt)
            for i in range(len(req)):
                if req[i] in txt:
                    tmp = 1
                else:
                    tmp = 0
                    break
            if not tmp:
                raise
    else:
        raise

    if first:
        first = tkinter.Tk(className="Maruediter")
        first.title(txt["welcome"])
        first.l1 = ttk.Label(first, text="==="+txt["welcome"]+"===")
        first.l1.pack()
        first.b1 = ttk.Button(first,text=txt["next"],command=first.destroy)
        first.b1.pack()
        first.mainloop()
    
    class Editer():
        def __init__(self, root):
            self.root = root
            self.File = File
            self.Main = main
            self.Help = help
    
    class Main(Editer):
        pass
    
    #cui tools
    def cui():
        def cui_help(a):
            if a == 0:
                print("[Usage] {option} {file}\n \n[options]\n    -c - file_addon_config\n    -cui - cui mode")
            else:
                print("[commands]\nexit or quit - exit.\nhelp or ? - help.")
        print("[info]open in cui mode.")
        while 1:
            print(">>>", end="")
            input_var = input()
            if input_var == "exit":
                exit()
            elif input_var == "quit":
                exit()
            elif input_var == "":
                pass
            elif input_var == "help":
                print(info)
                cui_help(1)
            elif input_var == "?":
                print(info)
                cui_help(1)
            else:
                print("[error] '" + input_var + "' is not available.")

    # window class
    class window():
        #fullscreen
        def fullscreen():
            if fl.get() == 1:
                root.attributes("-fullscreen", True)
                print("[window]fullscreen on")
            else:
                root.attributes("-fullscreen", False)
                print("[window]fullscreen off")
        #open new window
        def newwin():
            subprocess.Popen([sys.argv[0]], shell=True)
        def welcome():
            if root.note.index("end") == 0:
                root.note.welcome = ttk.Frame(root.note)
                root.note.welcome.pack(fill="both")
                #root.tkdnd.bindtarget(root.note.welcome, lambda event: Main(root).File().open_file(dnd=event), "text/uri-list")
                root.note.welcome.bt1 = ttk.Button(root.note.welcome,text=txt["new"],command=Main(root).File().new)
                root.note.welcome.bt1.pack(fill="both")#,side="left")
                root.note.welcome.bt2 = ttk.Button(root.note.welcome,text=txt["open"],command=lambda: Main(root).File().open_file(2))
                root.note.welcome.bt2.pack(fill="both")#,side="right")
                root.note.add(root.note.welcome,text=txt["welcome"])
                root.note.welcome.opened = 1
                root.menu.m_f.entryconfigure(txt["save"]+" (S)",state="disabled")
                root.menu.m_f.entryconfigure(txt["save_as"]+" (A)",state="disabled")
                root.menu.m_f.entryconfigure(txt["close_tab"]+" (C)",state="disabled")
                if en_dnd:
                    root.note.dnd_frame = ttk.LabelFrame(root.note.welcome,text="Drop file here")
                    root.note.dnd_frame.pack(anchor="c",fill="both",expand=True)
                    root.note.dnd_frame.drop_target_register(DND_FILES)
                    root.note.dnd_frame.dnd_bind('<<Drop>>', lambda event: Main(root).File().open_file(open_path=event.data))
            else:
                if len(openning) != 0:
                    if root.note.welcome.opened == 1:
                        root.note.forget(0)
                        root.note.welcome.opened = 0
                        root.menu.m_f.entryconfigure(txt["save"]+" (S)",state="normal")
                        root.menu.m_f.entryconfigure(txt["save_as"]+" (A)",state="normal")
                        root.menu.m_f.entryconfigure(txt["close_tab"]+" (C)",state="normal")

    
    class File(Main):
        """ File edit Main Class"""
        def __init__(self):
            pass
        def _randomstr(self, n):
            """ Generate random string. """
            return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
        def save(self, other_name=0, save_all=1):
            """ Save file(s)."""
            print("[save]")
            if not self.root.note.welcome.opened:
                if save_all == 1:
                    if other_name == 0:
                        threading.Thread(target=lambda:openning[self.self.root.note.index("current")][1].file_save(openning[self.self.root.note.index("current")][0],"0")).start()
                    else:
                        path = filedialog.asksaveasfilename()
                        if path == None:
                            pass
                        else:
                            threading.Thread(target=lambda:openning[self.root.note.index("current")][1].file_save(openning[self.root.note.index("current")][0],path)).start()
                else:
                    for i in range(len(openning)):
                        threading.Thread(target=lambda:openning[i][1].file_save(openning[i][0],"0")).start()
        #open file
        def open_file(self, ofps=0, open_path=None, dnd=None):
            print("[file][open] run")
            if ofps == 1:
                if os.name == "posix":
                    ftype = [(txt["maruediter_file"],str(file_addon_type).lstrip("[").rstrip("]").replace(".","*.").replace("'","").replace(", ","|"))]
                elif os.name == "nt":
                    ftype = [(txt["maruediter_file"],tuple(file_addon_type))]
                else:
                    ftype = []
                for i in range(len(file_addons)):
                    ftype.append((file_addon_type_ex[i],file_addon_type[i]))
                ftype.append((txt["all"],"*.*"))
                time.sleep(0.1)
                if dnd != None:
                    print(dnd.data)
                    open_path = str(dnd.data).encode("iso8859-1").decode("utf-8")
                else:
                    open_path = filedialog.askopenfilename(filetypes=ftype, master=self.root)
            elif ofps == 2:
                open_path = filedialog.askopenfilename(filetypes=[(txt["all"],"*.*")])
            elif ofps == 3:
                pass
            if open_path == '':
                print("[file:warn](001):no file select.")
            elif type(open_path) != str:
                print("[file:warn](002):no such file or directory.({})".format(open_path))
            elif ofps != 0 and not os.path.exists(open_path):
                print("[file:warn](002):no such file or directory.({})".format(open_path))
            else:
                if ofps == 0 or ofps == 1:
                    for i in range(len(file_addon_list)):
                        if file_addon_type[i] in open_path:
                            openning.append([ttk.Frame(self.root.note),file_addons[i]])
                            openning[-1][0].pack(fill="both")
                            #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: Main(root).File().open_file(dnd=event), "text/uri-list")
                            self.root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                            window.welcome()
                            openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),Main(root).File()._randomstr(10))
                            os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                            file_addons[i].file_open(open_path, ofps, openning[-1][0])
                            Main.Main(open_path, len(openning)-1, i)
                            break
                        elif len(file_addon_list)-1 == i:
                            tkmsg.showerror(txt["error"],txt["error_cant_open"])
                        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
                elif ofps == 3:
                    for i in range(len(file_addon_list)):
                        if file_addon_type[i] in open_path:
                            openning.append([ttk.Frame(self.root.note),file_addons[i]])
                            openning[-1][0].pack(fill="both")
                            #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: Main(root).File().open_file(dnd=event), "text/uri-list")
                            self.root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                            window.welcome()
                            openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),Main(root).File()._randomstr(10))
                            os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                            file_addons[i].file_open(open_path, ofps, openning[-1][0])
                            Main.Main(open_path, len(openning)-1, i)
                            break
                        elif len(file_addon_list)-1 == i:
                            self = tkinter.Toplevel()
                            self.title(txt["select_file_type"])
                            self.lb = tkinter.Listbox(self)
                            self.lb.pack()
                            for i in range(len(file_addons)):
                                self.lb.insert("end",(file_addon_type_ex[i],file_addon_type[i]))
                            def fileopen(open_path):
                                global openning
                                openning.append([ttk.Frame(self.root.note),file_addons[i]])
                                openning[-1][0].pack(fill="both")
                                #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: Main(root).File().open_file(dnd=event), "text/uri-list")
                                self.root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                                window.welcome()
                                openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),Main(root).File()._randomstr(10))
                                os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                                file_addons[i].file_open(open_path, ofps, openning[-1][0])
                                Main.Main(open_path, len(openning)-1, self.lb.curselection()[0])
                            self.bt1 = ttk.Button(self, text=txt["next"], command=lambda:(fileopen(open_path),self.destroy()))
                            self.bt1.pack()
                            #self.mainloop()
                            break
                    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
                else:
                    self = tkinter.Toplevel()
                    self.title(txt["select_file_type"])
                    self.lb = tkinter.Listbox(self)
                    self.lb.pack()
                    for i in range(len(file_addons)):
                        self.lb.insert("end",(file_addon_type_ex[i],file_addon_type[i]))
                    def fileopen(open_path):
                        global openning
                        openning.append([ttk.Frame(self.root.note),file_addons[i]])
                        openning[-1][0].pack(fill="both")
                        #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: Main(root).File().open_file(dnd=event), "text/uri-list")
                        self.root.note.add(openning[-1][0], text=os.path.basename(open_path))
                        window.welcome()
                        openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),Main(root).File()._randomstr(10))
                        os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                        file_addons[i].file_open(open_path, ofps, openning[-1][0])
                        Main.Main(open_path, len(openning)-1, self.lb.curselection()[0])
                    self.bt1 = ttk.Button(self, text=txt["next"], command=lambda:(fileopen(open_path),self.destroy()))
                    self.bt1.pack()
                    #self.mainloop()
        #exit  
        def exit(self):
            def remove():
                if not self.root.note.welcome.opened:
                    for j in range(len(openning)):
                        for i in range(len(file_addon_list)):
                            try:
                                openning[i][1].file_exit(openning[j][0])
                                if os.path.exists(openning[i][0].temp_dir):
                                    shutil.rmtree(openning[i][0].temp_dir)
                            except:
                                pass
                            break
            e = tkmsg.askyesnocancel(txt["check"], txt["save_check"])
            if e == True:
                Main(root).File().save()
                remove()
                print("[info] exit")
                self.root.destroy()
                os._exit(0)
                sys.exit()
                
            elif e == False:
                remove()
                print("[info] exit(Not saved)")
                self.root.destroy()
                os._exit(0)
                sys.exit()
            else:
                pass
        #close tab
        def close_tab(self):
            if not self.root.note.welcome.opened:
                def remove(select):
                    try:
                        openning[select][1].file_exit(openning[select][0])
                    except:
                        pass
                    openning.pop(select)
                select = self.root.note.index("current")
                e = tkmsg.askyesnocancel(txt["check"], txt["save_check"])
                if e == True:
                    Main(root).File().save()
                    remove(select)
                    print("[file]close tab")
                    self.root.note.forget("current")
                    window.welcome()
                elif e == False:
                    remove(select)
                    print("[file]close tab(No saved)")
                    self.root.note.forget("current")
                    window.welcome()
                else:
                    pass
            else:
                Main(root).File().exit()
        #new file
        def new(self):
            def delaw(master):
                if len(master.widgets) != 0:
                    for i in range(len(master.widgets)):
                        master.widgets[i].destroy()
                    for i in range(len(master.widgets)):
                        master.widgets.pop(0)
            def packaw(master):
                if len(master.widgets) != 0:
                    for i in range(len(master.widgets)):
                        master.widgets[i].pack()
            print("[file][new] run")
            win = tkinter.Toplevel()
            win.resizable(0,0)
            win.title(txt["new"])
            win.geometry('500x300')
            master = ttk.Frame(win)
            master.pack(fill="both",expand=True)
            master.nstep = tkinter.IntVar(master, value=0)
            master.n_l = ttk.Label(master, text=txt["new_main"])
            master.n_f = ttk.Frame(master)
            master.n_b1 = ttk.Button(master.n_f, text=txt["next"], command=lambda:master.nstep.set(master.nstep.get()+1))
            master.n_b2 = ttk.Button(master.n_f, text=txt["back"], command=lambda:master.nstep.set(master.nstep.get()-1))
            master.n_b3 = ttk.Button(master.n_f, text=txt["cancel"], command=lambda:master.nstep.set(-1))
            master.n_l.pack()
            master.n_f.pack(side="bottom", fill="y")
            master.n_b1.pack(side="right")
            master.n_b2.pack(side="right")
            master.n_b3.pack(side="right")
            master.widgets = []
            while 1:
                master.wait_variable(master.nstep)
                if master.nstep.get() == -1:
                    delaw(master)
                    master.nstep.set(0)
                    win.destroy()
                    break
                elif master.nstep.get() == 0:
                    delaw(master)
                    master.n_l.configure(text=txt["new_main"])
                elif master.nstep.get() == 1:
                    delaw(master)
                    master.widgets.append(ttk.Label(master, text=txt["dir_name"]+":"))
                    master.widgets.append(ttk.Entry(master))
                    master.widgets.append(ttk.Button(master, text=txt["choose_dir"], command=lambda:(master.widgets[1].delete("-1","end"),master.widgets[1].insert("end",filedialog.askdirectory(master=master)))))
                    master.widgets.append(ttk.Label(master, text=txt["file_name"]+":"))
                    master.widgets.append(ttk.Entry(master))
                    master.n_l.configure(text=txt["new_main"]+"\n"+txt["new_sub1"])
                    packaw(master)
                elif master.nstep.get() == 2:
                    master.n_l.configure(text=txt["new_main"]+"\n"+txt["new_sub2"])
                    master.directory = master.widgets[1].get()
                    master.filename = master.widgets[4].get()
                    delaw(master)
                    master.widgets.append(tkinter.Listbox(master, width=30))
                    packaw(master)
                    master.filetypes=[]
                    for i in range(len(file_addons)):
                        master.filetypes.append(file_addon_type[i] + "(" + file_addon_type_ex[i] + ")")
                    for i in range(len(master.filetypes)):
                        master.widgets[0].insert("end", master.filetypes[i])
                elif master.nstep.get() == 3:
                    if type(master.directory) == str and os.path.exists(master.directory):
                        if not len(master.widgets[0].curselection()) == 0:
                            if not len(master.filename) == 0:
                                master.filetype = master.widgets[0].get(master.widgets[0].curselection())
                                if "." in master.filename:
                                    if tkmsg.askyesno(txt["check"], txt["new_check"].replace("(_path_)",master.directory+"/"+master.filename+file_addon_type[int(master.widgets[0].curselection()[0])]).replace("(_type_)",str(master.filetype)), parent=win):
                                        master.open_path = master.directory +"/" + master.filename
                                        print("[file][new]:Path" + master.directory +"/" + master.filename + "\n[file][new]Type:" + str(master.filetype))
                                        delaw(master)
                                        master.n_l.configure(text=txt["wait"])
                                        for i in range(len(file_addon_list)):
                                            if file_addon_list[i] in master.open_path:
                                                file_addons[i].file_new(master.open_path)
                                                break
                                        master.n_l.configure(text=txt["done_msg"])
                                        master.n_b2.destroy()
                                        master.n_b3.destroy()
                                        master.n_b1.configure(text=txt["done"], command=lambda:(self.open_file(open_path=master.open_path),master.nstep.set(-1)))
                                    else:
                                        master.nstep.set(2)
                                else:
                                    if tkmsg.askyesno(txt["check"], txt["new_check"].replace("(_path_)",master.directory+"/"+master.filename+file_addon_type[int(master.widgets[0].curselection()[0])]).replace("(_type_)",str(master.filetype)), parent=win):
                                        master.open_path = master.directory +"/" + master.filename + file_addon_type[int(master.widgets[0].curselection()[0])]
                                        print("[file][new]Path:" + master.directory +"/" + master.filename + file_addon_type[int(master.widgets[0].curselection()[0])] + "\n[file][new]Type:" + str(master.filetype))
                                        delaw(master)
                                        master.n_l.configure(text=txt["wait"])
                                        for i in range(len(file_addon_list)):
                                            if file_addon_list[i] in master.open_path:
                                                file_addons[i].file_new(master.open_path)
                                                break
                                        master.n_l.configure(text=txt["done_msg"])
                                        master.n_b2.destroy()
                                        master.n_b3.destroy()
                                        master.n_b1.configure(text=txt["done"], command=lambda:(Main(root).File().open_file(open_path=master.open_path),master.nstep.set(-1)))
                                    else:
                                        master.nstep.set(2)
                            else:
                                tkmsg.showerror(txt["error"],txt["new_e1"],parent=win)
                                master.n_b2.configure(command=None)
                                master.nstep.set(2)
                                master.filename=tkinter.simpledialog.askstring(txt["file_name"],txt["new_e1_msg"],parent=win)
                        else:
                            master.n_b2.configure(command=None)
                            master.nstep.set(2)
                            tkmsg.showerror(txt["error"],txt["new_e2"],parent=win)
                    else:
                        tkmsg.showerror(txt["error"],txt["new_e3"],parent=win)
                        master.n_b2.configure(command=None)
                        master.nstep.set(2)
                        master.directory = filedialog.askdirectory(parent=win)
            #win.mainloop()
        # setting
        def setting(self):
            def done():
                conf.update(theme=s.style.get())
                conf.update(open_other=s_v1.get())
                if conf["lang"] != s.lang.get():
                    tkmsg.showinfo("Info","Language Changing will apply when you start maruediter next time.", parent=s)
                    conf.update(lang=s.lang.get())
                pickle.dump(conf, open(conf_path, "wb"))
                s.destroy()
            def cancel():
                self.root.style.theme_use(conf["theme"])
                s.destroy()
            def change(gomi, argv):
                if argv == "style":
                    self.root.style.theme_use(s.style.get())
                elif argv == "lang":
                    pass
            s = tkinter.Toplevel()
            s.title(txt["setting"])
            s.note = ttk.Notebook(s)
            s.note.pack(fill="both",expand=True)
            s.frames = {}
            s.frames.update(Main=ttk.Frame(s.note))
            s.note.add(s.frames["Main"],text="Main")
            s.frames["Main"].note = ttk.Notebook(s.frames["Main"])
            s.frames["Main"].note.pack(fill="both",expand=True)
            Main = {"Appearance" : "", "Addons" : ""}
            for i in Main.keys():
                Main[i] = (ttk.Frame(s.frames["Main"].note))
                s.frames["Main"].note.add(Main[i], text=i)
            s_b1 = ttk.Button(s, text=txt["done"], command=done)
            s_b2 = ttk.Button(s, text=txt["cancel"], command=cancel)
            if "open_other" in conf:
                s_v1 = tkinter.IntVar(Main["Appearance"], value=conf["open_other"])
            else:
                s_v1 = tkinter.IntVar(Main["Appearance"], value=0)
            s_c1 = ttk.Checkbutton(Main["Appearance"], text=txt["st_open_from"], variable=s_v1)
            s_c1.pack()
            s_b1.pack(side="left",fill="both",expand=True)
            s_b2.pack(side="left",fill="both",expand=True)
            def remove():
                try:
                    file_addon.remove(file_addon.get_file()[adon.a_fl.curselection()[0]-1])
                    adon.a_fl.delete(adon.a_fl.curselection()[0]-1)
                except:
                    pass
                os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
            s.style = ttk.Combobox(Main["Appearance"], width=30, value=self.root.style.theme_names())
            s.style.pack()
            s.lang = ttk.Combobox(Main["Appearance"], width=30, value=list(map(lambda value: value.replace(".lang",""), list(filter(lambda value: ".lang" in value, os.listdir(cd+"/language"))))))
            s.lang.pack()
            s.a_fl = tkinter.Listbox(Main["Addons"], width=30)
            s.a_fl.pack()
            s.a_fl.insert("end",txt["file_addon"]+":")
            s.a_b1 = ttk.Button(Main["Addons"], text=txt["delete"], command=remove)
            s.a_b1.pack()
            s.style.insert("end",self.root.style.theme_use())
            s.lang.insert("end",conf["lang"])
            s.style.bind('<<ComboboxSelected>>', lambda null: change(gomi=null, argv="style"))
            s.lang.bind('<<ComboboxSelected>>', lambda null: change(gomi=null, argv="lang"))
            s.style.bind('<Return>', lambda null: change(gomi=null, argv="style"))
            s.lang.bind('<Return>', lambda null: change(gomi=null, argv="lang"))
            for i in range(len(file_addons)):
                s.a_fl.insert("end", "  " + file_addon_list[i] + "(" + file_addon_type[i] + " " +file_addon_type_ex[i] + ")")
    #help
    class Help():
        #show version
        def var(self):
            print("[info] show version")
            h = tkinter.Toplevel(self.root)
            h.title(txt["version"])
            h._h = ttk.Label(h)
            h._h.pack(fill="both",expand=True)
            #h.img = tkinter.PhotoImage(file='./image/maruediter.gif', master=h)
            h.img = tkinter.PhotoImage(file='./image/init.png', master=h._h)
            h_l1 = ttk.Label(h._h, image=h.img)
            h_l1.pack(side="top")
            h_l2 = ttk.Label(h._h, text="version:" + info[0].lstrip("ver=") + "  reversion:" + info[1].lstrip("rever=") + "  2019-2020 Marusoftware")
            h_l2.pack(side="bottom")
        #show help
        def help(self):
            pass
        def update(self):
            pass

    def main(self, open_path, num1, num2):
        file_addons[num2].file_main(openning[num1][0])

    def tkerror(exception, value, t):
        import tkinter
        sorry = tkinter.Toplevel()
        sorry.title("Maruediter - Error")
        tkinter.Label(sorry,text="We're sorry.\n\nError is huppun.").pack()
        t = tkinter.Text(sorry)
        t.pack()
        t.insert("end","Error report=========\n")
        t.insert("end",str(exception)+"\n")
        t.insert("end",str(value)+"\n")
        t.insert("end",str(t)+"\n")
        tkinter.Button(sorry, text="EXIT", command=sorry.destroy).pack()
        sorry.protocol("WM_DELETE_WINDOW",sorry.destroy)
        #sorry.mainloop()
    
    ##if not os.path.exists("./addonlist.txt"):
    ##try:
    ##    urllib.request.urlretrieve("http://raspi-maru2004.ddns.net/downloads/data_pool/maruediter_addon/addonlist.txt","./addonlist.txt")
    ##except:
    ##    pass

    if not len(sys.argv) == 0:
        if "-cui" in sys.argv:
            cui()
        elif "--help" in sys.argv:
            cui_help(0)
            sys.exit()

    try:
        root = Tk(className='Maruediter')
    except:
        cui()
    root.withdraw()
    root.style = Style()
    print("[info] Theme:"+conf["theme"])
    if "theme" in conf:
        root.style.theme_use(conf["theme"])
    root.title(txt["maruediter"])

    if os.path.exists("./image/maruediter.png"):
        root.iconphoto(True, tkinter.PhotoImage(file='./image/maruediter.png'))
    else:
        print("[info] Icon file not found.")
    
    root.report_callback_exception=tkerror
    root.protocol("WM_DELETE_WINDOW", Main(root).File().exit)
    root.menu = tkinter.Menu(root)
    root.menu.m_f = tkinter.Menu(root.menu, tearoff=0)
    root.menu.m_f.add_command(label=txt["new"]+" (N)", command=Main(root).File().new ,under=len(txt["new"])+2)
    root.menu.m_f.add_command(label=txt["open"]+" (O)", command=lambda: threading.Thread(target=Main(root).File().open_file,args=[1]).start(),under=len(txt["open"])+2)
    if "open_other" in conf:
        if conf["open_other"] == 1:
            root.menu.m_f.add_command(label=txt["open_from"]+" (P)", command=lambda: threading.Thread(target=Main(root).File().open_file,args=[2]).start(),under=len(txt["open_from"])+2)
    root.menu.m_f.add_command(label=txt["save_as"]+" (A)", command=lambda:Main(root).File().save(other_name=1),under=len(txt["save_as"])+2)
    root.menu.m_f.add_command(label=txt["save"]+" (S)", command=Main(root).File().save,under=len(txt["save"])+2)
    root.menu.m_f.add_command(label=txt["close_tab"]+" (C)",command=Main(root).File().close_tab,under=len(txt["close_tab"])+2)
    root.menu.m_f.add_command(label=txt["close_all"]+" (X)", command=Main(root).File().exit,under=len(txt["close_all"])+2)
    root.menu.m_d = tkinter.Menu(root.menu, tearoff=0)
    fl = tkinter.BooleanVar()
    root.menu.m_d.add_command(label=txt["open_new"]+" (N)", command=window.newwin,under=len(txt["open_new"])+2)
    root.menu.m_d.add_checkbutton(label=txt["full_screen"]+" (F)", variable=fl, command=window.fullscreen,under=len(txt["full_screen"])+2)
    root.menu.m_h = tkinter.Menu(root.menu, tearoff=0)
    root.menu.m_h.add_command(label=txt["version"]+" (V)", command=Main.Help.var,under=len(txt["version"])+2)
    root.menu.m_h.add_command(label=txt["help"]+" (H)", command=Main.Help.help,under=len(txt["help"])+2)
    root.menu.m_h.add_command(label=txt["chk_upd"]+" (C)", command=Main.Help.help,under=len(txt["chk_upd"])+2)
    root.menu.add_cascade(label=txt["file"]+" (F)", menu=root.menu.m_f,under=len(txt["file"])+2)
    root.menu.add_cascade(label=txt["window"]+" (W)", menu=root.menu.m_d,under=len(txt["window"])+2)
    root.menu.add_command(label=txt["setting"]+" (S)", under=len(txt["setting"])+2,command=Main(root).File().setting)
    root.menu.add_cascade(label=txt["help"]+" (H)", menu=root.menu.m_h,under=len(txt["help"])+2)
    root.config(menu=root.menu)
    root.__root = ttk.Frame(root)
    root.__root.pack(fill="both",expand=True)
    root.note = CustomNotebook(root.__root, style=root.style)
    root.note.pack(fill="both",expand=True)
    root.note.enable_traversal()
    root.bind("<<NotebookTabClosed>>",lambda null: Main(root).File().close_tab())
    if en_dnd:
        print("[info] tkdnd enable")
    if os.path.exists(sys.argv[-1]) and sys.argv[0] != sys.argv[-1]:
        print("[info] open from argv("+sys.argv[-1]+")")
        Main(root).File().open_file(ofps=3,open_path=sys.argv[-1])
    window.welcome()
    root.geometry('500x500')
    root.update_idletasks()
    root.deiconify()
    root.mainloop()
except Exception as e:
    import traceback
    import sys
    import os
    print("We're sorry. Error is huppun.")
    print(traceback.format_exc())
    import tkinter
    sorry = tkinter.Tk(className="Maruediter")
    sorry.title("Maruediter - Error")
    tkinter.Label(sorry,text="We're sorry.\n\nError is huppun.").pack()
    t = tkinter.Text(sorry)
    t.pack()
    t.insert("end","Error report=========\n")
    t.insert("end",str(traceback.format_exc())+"\n")
    tkinter.Button(sorry, text="EXIT", command=lambda: exit()).pack()
    sorry.protocol("WM_DELETE_WINDOW",lambda: exit())
    os._exit(-1)
    sys.exit(-1)
