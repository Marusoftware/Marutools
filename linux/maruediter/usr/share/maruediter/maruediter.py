#! /usr/bin/python3
print("[info] import core library")
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
    if platform.machine() == "armv7":
        sys.path.append(os.path.join(cd,"share_os","raspi"))
        os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","raspi","tkdnd")
    else: 
        if is64bit:
            sys.path.append(os.path.join(cd,"share_os","linux64"))
            os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","linux64","tkdnd")
        else:
            sys.path.append(os.path.join(cd,"share_os","linux32"))
            os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","linux32","tkdnd")        
else:
    sys.path.append(os.path.join(cd,"share_os","macos"))
    os.environ['TKDND_LIBRARY'] = os.path.join(cd,"share_os","macos","tkdnd")
print("[info] import additional library")
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
from scrolledtext import ScrolledText
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
        req = ['welcome', 'maruediter', 'exit', 'close_all', 'close_tab', 'save', 'save_as', 'save_from', 'open_from', 'open', 'new', 'file', 'open_new', 'full_screen', 'help', 'window', 'setting', 'addon', 'file_addon', 'delete', 'maruediter_file', 'all', 'error', 'error_cant_open', 'select_file_type', 'next', 'check', 'save_check', 'were_sorry', 'new_main', 'back', 'cancel', 'dir_name', 'choose_dir', 'file_name', 'new_sub1', 'new_sub2', 'new_check', 'wait', 'done', 'new_e1', 'new_e2', 'new_e3', 'done_msg', 'new_e1_msg', 'chk_upd', 'style', 'lang', 'st_open_from', 'st_dnd', 'new_check2', 'about']
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
                #root.tkdnd.bindtarget(root.note.welcome, lambda event: mfile.open_file(dnd=event), "text/uri-list")
                root.note.welcome.bt1 = ttk.Button(root.note.welcome,text=txt["new"],command=mfile.new)
                root.note.welcome.bt1.pack(fill="both")#,side="left")
                root.note.welcome.bt2 = ttk.Button(root.note.welcome,text=txt["open"],command=lambda: mfile.open_file(2))
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
                    root.note.dnd_frame.dnd_bind('<<Drop>>', lambda event: mfile.open_file(open_path=event.data))
            else:
                if len(openning) != 0:
                    if root.note.welcome.opened == 1:
                        root.note.forget(0)
                        root.note.welcome.opened = 0
                        root.menu.m_f.entryconfigure(txt["save"]+" (S)",state="normal")
                        root.menu.m_f.entryconfigure(txt["save_as"]+" (A)",state="normal")
                        root.menu.m_f.entryconfigure(txt["close_tab"]+" (C)",state="normal")

    #file edit class
    class mfile():
        def __init__(self):
            pass
        #randomstr
        def _randomstr(n):
           return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
        #save file
        def save(other_name=0, save_all=1):
            print("[save]")
            if not root.note.welcome.opened:
                if save_all == 1:
                    if other_name == 0:
                        threading.Thread(target=lambda:openning[root.note.index("current")][1].file_save(openning[root.note.index("current")][0],"0")).start()
                    else:
                        path = filedialog.asksaveasfilename()
                        if path == None:
                            pass
                        else:
                            threading.Thread(target=lambda:openning[root.note.index("current")][1].file_save(openning[root.note.index("current")][0],path)).start()
                else:
                    for i in range(len(openning)):
                        threading.Thread(target=lambda:openning[i][1].file_save(openning[i][0],"0")).start()
        #open file
        def open_file(ofps=0, open_path=None, dnd=None):
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
                    open_path = filedialog.askopenfilename(filetypes=ftype, master=root)
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
                            openning.append([ttk.Frame(root.note),file_addons[i]])
                            openning[-1][0].pack(fill="both")
                            #root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                            root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                            window.welcome()
                            openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                            os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                            file_addons[i].file_open(open_path, ofps, openning[-1][0])
                            main(open_path, len(openning)-1, i)
                            break
                        elif len(file_addon_list)-1 == i:
                            tkmsg.showerror(txt["error"],txt["error_cant_open"])
                        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
                elif ofps == 3:
                    for i in range(len(file_addon_list)):
                        if file_addon_type[i] in open_path:
                            openning.append([ttk.Frame(root.note),file_addons[i]])
                            openning[-1][0].pack(fill="both")
                            #root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                            root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                            window.welcome()
                            openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                            os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                            file_addons[i].file_open(open_path, ofps, openning[-1][0])
                            main(open_path, len(openning)-1, i)
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
                                openning.append([ttk.Frame(root.note),file_addons[i]])
                                openning[-1][0].pack(fill="both")
                                #root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                                root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                                window.welcome()
                                openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                                os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                                file_addons[i].file_open(open_path, ofps, openning[-1][0])
                                main(open_path, len(openning)-1, self.lb.curselection()[0])
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
                        openning.append([ttk.Frame(root.note),file_addons[i]])
                        openning[-1][0].pack(fill="both")
                        #root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                        root.note.add(openning[-1][0], text=os.path.basename(open_path))
                        window.welcome()
                        openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                        os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                        file_addons[i].file_open(open_path, ofps, openning[-1][0])
                        main(open_path, len(openning)-1, self.lb.curselection()[0])
                    self.bt1 = ttk.Button(self, text=txt["next"], command=lambda:(fileopen(open_path),self.destroy()))
                    self.bt1.pack()
                    #self.mainloop()
        #exit  
        def exit():
            def remove():
                if not root.note.welcome.opened:
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
                mfile.save()
                remove()
                print("[info] exit")
                root.destroy()
                os._exit(0)
                sys.exit()
                
            elif e == False:
                remove()
                print("[info] exit(Not saved)")
                root.destroy()
                os._exit(0)
                sys.exit()
            else:
                pass
        #close tab
        def close_tab():
            if not root.note.welcome.opened:
                def remove(select):
                    try:
                        openning[select][1].file_exit(openning[select][0])
                    except:
                        pass
                    openning.pop(select)
                select = root.note.indScrolledTextex("current")
                e = tkmsg.askyesnocancel(txt["check"], txt["save_check"])
                if e == True:
                    mfile.save()
                    remove(select)
                    print("[file]close tab")
                    root.note.forget("current")
                    window.welcome()
                elif e == False:
                    remove(select)
                    print("[file]close tab(No saved)")
                    root.note.forget("current")
                    window.welcome()
                else:
                    pass
            else:
                mfile.exit()
        #new file
        def new():
            def delaw(self):
                if len(self.widgets) != 0:
                    for i in range(len(self.widgets)):
                        self.widgets[i].destroy()
                    for i in range(len(self.widgets)):
                        self.widgets.pop(0)
            def packaw(self):
                if len(self.widgets) != 0:
                    for i in range(len(self.widgets)):
                        self.widgets[i].pack()
            print("[file][new] run")
            win = tkinter.Toplevel()
            win.resizable(0,0)
            win.title(txt["new"])
            win.geometry('500x300')
            self = ttk.Frame(win)
            self.pack(fill="both",expand=True)
            self.nstep = tkinter.IntVar(self, value=0)
            self.n_l = ttk.Label(self, text=txt["new_main"])
            self.n_f = ttk.Frame(self)
            self.n_b1 = ttk.Button(self.n_f, text=txt["next"], command=lambda:self.nstep.set(self.nstep.get()+1))
            self.n_b2 = ttk.Button(self.n_f, text=txt["back"], command=lambda:self.nstep.set(self.nstep.get()-1))
            self.n_b3 = ttk.Button(self.n_f, text=txt["cancel"], command=lambda:self.nstep.set(-1))
            self.n_l.pack()
            self.n_f.pack(side="bottom", fill="y")
            self.n_b1.pack(side="right")
            self.n_b2.pack(side="right")
            self.n_b3.pack(side="right")
            self.widgets = []
            self.directory = ""
            self.filename = ""
            while 1:
                self.wait_variable(self.nstep)
                if self.nstep.get() == -1:
                    delaw(self)
                    self.nstep.set(0)
                    win.destroy()
                    break
                elif self.nstep.get() == 0:
                    delaw(self)
                    self.n_l.configure(text=txt["new_main"])
                elif self.nstep.get() == 1:
                    delaw(self)
                    self.widgets.append(ttk.Label(self, text=txt["dir_name"]+":"))
                    self.widgets.append(ttk.Entry(self))
                    self.widgets.append(ttk.Button(self, text=txt["choose_dir"], command=lambda:(self.widgets[1].delete("-1","end"),self.widgets[1].insert("end",filedialog.askdirectory(master=self)))))
                    self.widgets.append(ttk.Label(self, text=txt["file_name"]+":"))
                    self.widgets.append(ttk.Entry(self))
                    self.n_l.configure(text=txt["new_main"]+"\n"+txt["new_sub1"])
                    packaw(self)
                elif self.nstep.get() == 2:
                    self.n_l.configure(text=txt["new_main"]+"\n"+txt["new_sub2"])
                    self.directory = self.widgets[1].get()
                    self.filename = self.widgets[4].get()
                    delaw(self)
                    self.widgets.append(tkinter.Listbox(self, width=30))
                    packaw(self)
                    self.filetypes=[]
                    for i in range(len(file_addons)):
                        self.filetypes.append(file_addon_type[i] + "(" + file_addon_type_ex[i] + ")")
                    for i in range(len(self.filetypes)):
                        self.widgets[0].insert("end", self.filetypes[i])
                elif self.nstep.get() == 3:
                    if type(self.directory) != str or not os.path.exists(self.directory):
                        tkmsg.showerror(txt["error"],txt["new_e3"],parent=win)
                        self.n_b2.configure(command=None)
                        self.nstep.set(2)
                        self.directory = filedialog.askdirectory(parent=win)
                    elif len(self.widgets[0].curselection()) == 0:
                        self.n_b2.configure(command=None)
                        self.nstep.set(2)
                        tkmsg.showerror(txt["error"],txt["new_e2"],parent=win)
                    elif len(self.filename) == 0:
                        tkmsg.showerror(txt["error"],txt["new_e1"],parent=win)
                        self.n_b2.configure(command=None)
                        self.nstep.set(2)
                        self.filename=tkinter.simpledialog.askstring(txt["file_name"],txt["new_e1_msg"],parent=win)
                        print(self.filename)
                    else:
                        if "." in self.filename:
                            self.open_path = self.directory +"/" + self.filename
                        else:
                            self.open_path = self.directory +"/" + self.filename + file_addon_type[int(self.widgets[0].curselection()[0])]
                        if os.path.exists(self.open_path):
                            if not tkmsg.askyesno(txt["check"], txt["new_check2"], parent=win):
                                self.n_b2.configure(command=None)
                                self.nstep.set(2)
                            else:
                                self.nstep.set(4)
                        else:
                            self.nstep.set(4)
                        if self.nstep.get() == 4:
                            self.filetype = self.widgets[0].get(self.widgets[0].curselection())
                            if tkmsg.askyesno(txt["check"], txt["new_check"].replace("(_path_)",self.open_path).replace("(_type_)",str(self.filetype)), parent=win):
                                print("[file][new]:Path" + self.directory +"/" + self.filename + "\n[file][new]Type:" + str(self.filetype))
                                delaw(self)
                                self.n_l.configure(text=txt["wait"])
                                for i in range(len(file_addon_list)):
                                    if file_addon_list[i] in self.open_path:
                                        file_addons[i].file_new(self.open_path)
                                        break
                                self.n_l.configure(text=txt["done_msg"])
                                self.n_b2.destroy()
                                self.n_b3.destroy()
                                self.n_b1.configure(text=txt["done"], command=lambda:(mfile.open_file(open_path=self.open_path),self.nstep.set(-1)))
                            else:
                                self.nstep.set(2)                               

        # setting
        def setting():
            def done():
                conf.update(theme=s.style.get())
                conf.update(open_other=s_v1.get())
                if conf["lang"] != s.lang.get():
                    tkmsg.showinfo("Info","Language Changing will apply when you start maruediter next time.", parent=s)
                    conf.update(lang=s.lang.get())
                pickle.dump(conf, open(conf_path, "wb"))
                s.destroy()
            def cancel():
                root.style.theme_use(conf["theme"])
                s.destroy()
            def change(gomi, argv):
                if argv == "style":
                    root.style.theme_use(s.style.get())
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
            Main = {"Appearance" : "", "File" : "", "Addons" : ""}
            for i in Main.keys():
                Main[i] = (ttk.Frame(s.frames["Main"].note))
                s.frames["Main"].note.add(Main[i], text=i)
            s_b1 = ttk.Button(s, text=txt["done"], command=done)
            s_b2 = ttk.Button(s, text=txt["cancel"], command=cancel)
            if "open_other" in conf:
                s_v1 = tkinter.IntVar(Main["File"], value=conf["open_other"])
            else:
                s_v1 = tkinter.IntVar(Main["File"], value=0)
            if "en_dnd" in conf:
                s_v2 = tkinter.IntVar(Main["File"], value=conf["en_dnd"])
            else:
                s_v2 = tkinter.IntVar(Main["File"], value=0)
            s_c1 = ttk.Checkbutton(Main["File"], text=txt["st_open_from"], variable=s_v1)
            s_c1.pack(side="top",fill="x")
            s_c2 = ttk.Checkbutton(Main["File"], text=txt["st_dnd"], variable=s_v2)
            s_c2.pack(side="top",fill="x")
            s_b1.pack(side="left",fill="both",expand=True)
            s_b2.pack(side="left",fill="both",expand=True)
            def remove():
                try:
                    file_addon.remove(file_addon.get_file()[adon.a_fl.curselection()[0]-1])
                    adon.a_fl.delete(adon.a_fl.curselection()[0]-1)
                except:
                    pass
                os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
            s.style = ttk.Combobox(Main["Appearance"], width=30, value=root.style.theme_names())
            s.style.pack()
            s.lang = ttk.Combobox(Main["Appearance"], width=30, value=list(map(lambda value: value.replace(".lang",""), list(filter(lambda value: ".lang" in value, os.listdir(cd+"/language"))))))
            s.lang.pack()
            s.a_fl = tkinter.Listbox(Main["Addons"], width=30)
            s.a_fl.pack()
            s.a_fl.insert("end",txt["file_addon"]+":")
            s.a_b1 = ttk.Button(Main["Addons"], text=txt["delete"], command=remove)
            s.a_b1.pack()
            s.style.insert("end",root.style.theme_use())
            s.lang.insert("end",conf["lang"])
            s.style.bind('<<ComboboxSelected>>', lambda null: change(gomi=null, argv="style"))
            s.lang.bind('<<ComboboxSelected>>', lambda null: change(gomi=null, argv="lang"))
            s.style.bind('<Return>', lambda null: change(gomi=null, argv="style"))
            s.lang.bind('<Return>', lambda null: change(gomi=null, argv="lang"))
            for i in range(len(file_addons)):
                s.a_fl.insert("end", "  " + file_addon_list[i] + "(" + file_addon_type[i] + " " +file_addon_type_ex[i] + ")")
    #help
    class hlp():
        #show version
        def var():
            print("[info] show version")
            h = tkinter.Toplevel(root)
            h.title(txt["about"])
            h.note = ttk.Notebook(h)
            h.note.pack(fill="both",expand=True)
            h._h = ttk.Frame(h)
            h.note.add(h._h,text=txt["version"])
            h.img = tkinter.PhotoImage(file='./image/init.png', master=h._h)
            h_l1 = ttk.Label(h._h, image=h.img)
            h_l1.pack(side="top")
            h_l2 = ttk.Label(h._h, text="version:" + info[0].lstrip("ver=") + "  reversion:" + info[1].lstrip("rever=") + "  2019-2020 Marusoftware")
            h_l2.pack(side="bottom")
            h._h2 = ttk.Frame(h)
            h.note.add(h._h2,text=txt["licence"])
            h_t1 = ScrolledText(h._h2)
            h_t1.pack(fill="both",expand=True)
            h_t1.insert("end",open("./LICENCE","r").read())
            h_t1.configure(state="disabled")
        #show help
        def help():
            pass
        def update():
            pass

    def main(open_path, num1, num2):
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
    ##    urllib.request.urlretrieve("http://marusoftware.ddns.net/downloads/data_pool/maruediter_addon/addonlist.txt","./addonlist.txt")
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
        if endnd:
            try:
                root = tkinter.Tk(className='Maruediter')
            except:
                cui()
        else:
            cui()
    root.withdraw()
    try:
        root.style = Style()
    except:
        from tkinter.ttk import Style as oStyle
        root.style = oStyle()
    print("[info] Theme:"+conf["theme"])
    if "theme" in conf:
        root.style.theme_use(conf["theme"])
    root.title(txt["maruediter"])

    if os.path.exists("./image/maruediter.png"):
        root.iconphoto(True, tkinter.PhotoImage(file='./image/maruediter.png'))
    else:
        print("[info] Icon file not found.")
    if not "--debug" in sys.argv:
        root.report_callback_exception=tkerror
    root.protocol("WM_DELETE_WINDOW", mfile.exit)
    root.menu = tkinter.Menu(root)
    root.menu.m_f = tkinter.Menu(root.menu, tearoff=0)
    root.menu.m_f.add_command(label=txt["new"]+" (N)", command=mfile.new ,under=len(txt["new"])+2)
    root.menu.m_f.add_command(label=txt["open"]+" (O)", command=lambda: threading.Thread(target=mfile.open_file,args=[1]).start(),under=len(txt["open"])+2)
    if "open_other" in conf:
        if conf["open_other"] == 1:
            root.menu.m_f.add_command(label=txt["open_from"]+" (P)", command=lambda: threading.Thread(target=mfile.open_file,args=[2]).start(),under=len(txt["open_from"])+2)
    root.menu.m_f.add_command(label=txt["save_as"]+" (A)", command=lambda:mfile.save(other_name=1),under=len(txt["save_as"])+2)
    root.menu.m_f.add_command(label=txt["save"]+" (S)", command=mfile.save,under=len(txt["save"])+2)
    root.menu.m_f.add_command(label=txt["close_tab"]+" (C)",command=mfile.close_tab,under=len(txt["close_tab"])+2)
    root.menu.m_f.add_command(label=txt["close_all"]+" (X)", command=mfile.exit,under=len(txt["close_all"])+2)
    root.menu.m_d = tkinter.Menu(root.menu, tearoff=0)
    fl = tkinter.BooleanVar()
    root.menu.m_d.add_command(label=txt["open_new"]+" (N)", command=window.newwin,under=len(txt["open_new"])+2)
    root.menu.m_d.add_checkbutton(label=txt["full_screen"]+" (F)", variable=fl, command=window.fullscreen,under=len(txt["full_screen"])+2)
    root.menu.m_h = tkinter.Menu(root.menu, tearoff=0)
    root.menu.m_h.add_command(label=txt["about"]+" (V)", command=hlp.var,under=len(txt["about"])+2)
    root.menu.m_h.add_command(label=txt["help"]+" (H)", command=hlp.help,under=len(txt["help"])+2)
    root.menu.m_h.add_command(label=txt["chk_upd"]+" (C)", command=hlp.help,under=len(txt["chk_upd"])+2)
    root.menu.add_cascade(label=txt["file"]+" (F)", menu=root.menu.m_f,under=len(txt["file"])+2)
    root.menu.add_cascade(label=txt["window"]+" (W)", menu=root.menu.m_d,under=len(txt["window"])+2)
    root.menu.add_command(label=txt["setting"]+" (S)", under=len(txt["setting"])+2,command=mfile.setting)
    root.menu.add_cascade(label=txt["help"]+" (H)", menu=root.menu.m_h,under=len(txt["help"])+2)
    root.config(menu=root.menu)
    root.__root = ttk.Frame(root)
    root.__root.pack(fill="both",expand=True)
    root.note = CustomNotebook(root.__root, style=root.style)
    root.note.pack(fill="both",expand=True)
    root.note.enable_traversal()
    root.bind("<<NotebookTabClosed>>",lambda null: mfile.close_tab())
    if en_dnd:
        print("[info] tkdnd enable")
    if os.path.exists(sys.argv[-1]) and sys.argv[0] != sys.argv[-1]:
        print("[info] open from argv("+sys.argv[-1]+")")
        mfile.open_file(ofps=3,open_path=sys.argv[-1])
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
