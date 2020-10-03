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
from importlib import import_module
from custom_note import CustomNotebook
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
#import tkinter
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
    
    
    ##if not os.path.exists("./addonlist.txt"):
    ##try:
    ##    urllib.request.urlretrieve("http://raspi-maru2004.ddns.net/downloads/data_pool/maruediter_addon/addonlist.txt","./addonlist.txt")
    ##except:
    ##    pass
    

    class Maruediter():
        def __init__(self):
            print("[info] start")
            print("[info]system_info:",str(platform.uname()))
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
                if not self.root.note.welcome.opened:
                    if save_all == 1:
                        if other_name == 0:
                            threading.Thread(target=lambda:openning[self.root.note.index("current")][1].file_save(openning[self.root.note.index("current")][0],"0")).start()
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
            def open_file(ofps=0, open_path=None, dnd=None):
                print("[file][open] run")
                if ofps == 1:
                    if os.name == "posix":
                        ftype = [(self.txt["maruediter_file"],str(file_addon_type).lstrip("[").rstrip("]").replace(".","*.").replace("'","").replace(", ","|"))]
                    elif os.name == "nt":
                        ftype = [(self.txt["maruediter_file"],tuple(file_addon_type))]
                    else:
                        ftype = []
                    for i in range(len(file_addons)):
                        ftype.append((file_addon_type_ex[i],file_addon_type[i]))
                    ftype.append((self.txt["all"],"*.*"))
                    time.sleep(0.1)
                    open_path = filedialog.askopenfilename(filetypes=ftype, master=self.root)
                elif ofps == 2:
                    open_path = filedialog.askopenfilename(filetypes=[(self.txt["all"],"*.*")])
                elif ofps == 3:
                    pass
                if ofps == 4 and dnd != None:
                    if os.path.exists(dnd.data):
                        open_path = dnd.data
                    else:
                        open_path = str(dnd.data).encode("iso8859-1").decode("utf-8")
                if open_path == '':
                    print("[file:warn] (001):no file select.")
                elif type(open_path) != str:
                    print("[file:warn] (002):no such file or directory.({})".format(open_path))
                elif ofps != 0 and not os.path.exists(open_path):
                    print("[file:warn] (002):no such file or directory.({})".format(open_path))
                else:
                    if ofps == 0 or ofps == 1:
                        for i in range(len(file_addon_list)):
                            if file_addon_type[i] in open_path:
                                openning.append([ttk.Frame(self.root.note),file_addons[i]])
                                openning[-1][0].pack(fill="both")
                                #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                                self.root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                                window.welcome()
                                openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                                os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                                file_addons[i].file_open(open_path, ofps, openning[-1][0])
                                main(open_path, len(openning)-1, i)
                                break
                            elif len(file_addon_list)-1 == i:
                                tkmsg.showerror(self.txt["error"],self.txt["error_cant_open"])
                            os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
                    elif ofps == 3:
                        for i in range(len(file_addon_list)):
                            if file_addon_type[i] in open_path:
                                openning.append([ttk.Frame(self.root.note),file_addons[i]])
                                openning[-1][0].pack(fill="both")
                                #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                                self.root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                                window.welcome()
                                openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                                os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                                file_addons[i].file_open(open_path, ofps, openning[-1][0])
                                main(open_path, len(openning)-1, i)
                                break
                            elif len(file_addon_list)-1 == i:
                                self = tkinter.Toplevel()
                                self.title(self.txt["select_file_type"])
                                self.lb = tkinter.Listbox(self)
                                self.lb.pack()
                                for i in range(len(file_addons)):
                                    self.lb.insert("end",(file_addon_type_ex[i],file_addon_type[i]))
                                def fileopen(open_path):
                                    global openning
                                    openning.append([ttk.Frame(self.root.note),file_addons[i]])
                                    openning[-1][0].pack(fill="both")
                                    #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                                    self.root.note.add(openning[-1][0], text=os.path.basename(open_path), sticky="nsew")
                                    window.welcome()
                                    openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                                    os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                                    file_addons[i].file_open(open_path, ofps, openning[-1][0])
                                    main(open_path, len(openning)-1, self.lb.curselection()[0])
                                self.bt1 = ttk.Button(self, text=self.txt["next"], command=lambda:(fileopen(open_path),self.destroy()))
                                self.bt1.pack()
                                #self.mainloop()
                                break
                        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
                    else:
                        self = tkinter.Toplevel()
                        self.title(self.txt["select_file_type"])
                        self.lb = tkinter.Listbox(self)
                        self.lb.pack()
                        for i in range(len(file_addons)):
                            self.lb.insert("end",(file_addon_type_ex[i],file_addon_type[i]))
                        def fileopen(open_path):
                            global openning
                            openning.append([ttk.Frame(self.root.note),file_addons[i]])
                            openning[-1][0].pack(fill="both")
                            #self.root.tkdnd.bindtarget(openning[-1][0], lambda event: mfile.open_file(dnd=event), "text/uri-list")
                            self.root.note.add(openning[-1][0], text=os.path.basename(open_path))
                            window.welcome()
                            openning[-1][0].temp_dir = os.path.join(os.path.dirname(conf_path),mfile._randomstr(10))
                            os.makedirs(openning[-1][0].temp_dir,exist_ok=True)
                            file_addons[i].file_open(open_path, ofps, openning[-1][0])
                            main(open_path, len(openning)-1, self.lb.curselection()[0])
                        self.bt1 = ttk.Button(self, text=self.txt["next"], command=lambda:(fileopen(open_path),self.destroy()))
                        self.bt1.pack()
                        #self.mainloop()
            #exit  
            def exit():
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
                e = tkmsg.askyesnocancel(self.txt["check"], self.txt["save_check"])
                if e == True:
                    mfile.save()
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
            def close_tab():
                if not self.root.note.welcome.opened:
                    def remove(select):
                        try:
                            openning[select][1].file_exit(openning[select][0])
                        except:
                            pass
                        openning.pop(select)
                    select = self.root.note.index("current")
                    e = tkmsg.askyesnocancel(self.txt["check"], self.txt["save_check"])
                    if e == True:
                        mfile.save()
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
            #new file
            def new(self):
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
                window = tkinter.Toplevel()
                window.title(self.txt["new"])
                window.geometry('500x300')
                self = ttk.Frame(window)
                self.pack(fill="both",expand=True)
                self.nstep = tkinter.IntVar(self, value=0)
                self.n_l = ttk.Label(self, text=self.txt["new_main"])
                self.n_f = ttk.Frame(self)
                self.n_b1 = ttk.Button(self.n_f, text=self.txt["next"], command=lambda:self.nstep.set(self.nstep.get()+1))
                self.n_b2 = ttk.Button(self.n_f, text=self.txt["back"], command=lambda:self.nstep.set(self.nstep.get()-1))
                self.n_b3 = ttk.Button(self.n_f, text=self.txt["cancel"], command=lambda:self.nstep.set(-1))
                self.n_l.pack()
                self.n_f.pack(side="bottom", fill="y")
                self.n_b1.pack(side="right")
                self.n_b2.pack(side="right")
                self.n_b3.pack(side="right")
                self.widgets = []
                while 1:
                    self.wait_variable(self.nstep)
                    if self.nstep.get() == -1:
                        delaw(self)
                        self.nstep.set(0)
                        window.destroy()
                        break
                    elif self.nstep.get() == 0:
                        delaw(self)
                        self.n_l.configure(text=self.txt["new_main"])
                    elif self.nstep.get() == 1:
                        delaw(self)
                        self.widgets.append(ttk.Label(self, text=self.txt["dir_name"]+":"))
                        self.widgets.append(ttk.Entry(self))
                        self.widgets.append(ttk.Button(self, text=self.txt["choose_dir"], command=lambda:(self.widgets[1].delete("-1","end"),self.widgets[1].insert("end",filedialog.askdirectory(master=self)))))
                        self.widgets.append(ttk.Label(self, text=self.txt["file_name"]+":"))
                        self.widgets.append(ttk.Entry(self))
                        self.n_l.configure(text=self.txt["new_main"]+"\n"+self.txt["new_sub1"])
                        packaw(self)
                    elif self.nstep.get() == 2:
                        self.n_l.configure(text=self.txt["new_main"]+"\n"+self.txt["new_sub2"])
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
                        if type(self.directory) == str and os.path.exists(self.directory):
                            if not len(self.widgets[0].curselection()) == 0:
                                if not len(self.filename) == 0:
                                    self.filetype = self.widgets[0].get(self.widgets[0].curselection())
                                    if "." in self.filename:
                                        if tkmsg.askyesno(self.txt["check"], self.txt["new_check"].replace("(_path_)",self.directory+"/"+self.filename+file_addon_type[int(self.widgets[0].curselection()[0])]).replace("(_type_)",str(self.filetype)), parent=window):
                                            self.open_path = self.directory +"/" + self.filename
                                            print("[file][new]:Path" + self.directory +"/" + self.filename + "\n[file][new]Type:" + str(self.filetype))
                                            delaw(self)
                                            self.n_l.configure(text=self.txt["wait"])
                                            for i in range(len(file_addon_list)):
                                                if file_addon_list[i] in self.open_path:
                                                    file_addons[i].file_new(self.open_path)
                                                    break
                                            self.n_l.configure(text=self.txt["done_msg"])
                                            self.n_b2.destroy()
                                            self.n_b3.destroy()
                                            self.n_b1.configure(text=self.txt["done"], command=lambda:(mfile.open_file(open_path=self.open_path),self.nstep.set(-1)))
                                        else:
                                            self.nstep.set(2)
                                    else:
                                        if tkmsg.askyesno(self.txt["check"], self.txt["new_check"].replace("(_path_)",self.directory+"/"+self.filename+file_addon_type[int(self.widgets[0].curselection()[0])]).replace("(_type_)",str(self.filetype)), parent=window):
                                            self.open_path = self.directory +"/" + self.filename + file_addon_type[int(self.widgets[0].curselection()[0])]
                                            print("[file][new]Path:" + self.directory +"/" + self.filename + file_addon_type[int(self.widgets[0].curselection()[0])] + "\n[file][new]Type:" + str(self.filetype))
                                            delaw(self)
                                            self.n_l.configure(text=self.txt["wait"])
                                            for i in range(len(file_addon_list)):
                                                if file_addon_list[i] in self.open_path:
                                                    file_addons[i].file_new(self.open_path)
                                                    break
                                            self.n_l.configure(text=self.txt["done_msg"])
                                            self.n_b2.destroy()
                                            self.n_b3.destroy()
                                            self.n_b1.configure(text=self.txt["done"], command=lambda:(mfile.open_file(open_path=self.open_path),self.nstep.set(-1)))
                                        else:
                                            self.nstep.set(2)
                                else:
                                    tkmsg.showerror(self.txt["error"],self.txt["new_e1"],parent=window)
                                    self.n_b2.configure(command=None)
                                    self.nstep.set(2)
                                    self.filename=tkinter.simpledialog.askstring(self.txt["file_name"],self.txt["new_e1_msg"],parent=window)
                            else:
                                self.n_b2.configure(command=None)
                                self.nstep.set(2)
                                tkmsg.showerror(self.txt["error"],self.txt["new_e2"],parent=window)
                        else:
                            tkmsg.showerror(self.txt["error"],self.txt["new_e3"],parent=window)
                            self.n_b2.configure(command=None)
                            self.nstep.set(2)
                            self.directory = filedialog.askdirectory(master=window)
                window.mainloop()
            # setting
            def setting():
                def done():
                    conf.update(theme=s.style.get())
                    conf.update(open_other=s_v1.get())
                    pickle.dump(conf, open(conf_path, "wb"))
                    s.destroy()
                def cancel():
                    self.root.style.theme_use(conf["theme"])
                    s.destroy()
                def change(gomi, argv):
                    if argv == "style":
                        self.root.style.theme_use(s.style.get())
                s = tkinter.Toplevel()
                s.title(self.txt["setting"])
                s.note = ttk.Notebook(s)
                s.note.pack()
                s.frames = {}
                s.frames.update(Main=ttk.Frame(s))
                s.frames["Main"].pack()
                s.note.add(s.frames["Main"],text="Main")
                s_b1 = ttk.Button(s.frames["Main"], text=self.txt["done"], command=done)
                s_b2 = ttk.Button(s.frames["Main"], text=self.txt["cancel"], command=cancel)
                if "open_other" in conf:
                    s_v1 = tkinter.IntVar(s.frames["Main"], value=conf["open_other"])
                else:
                    s_v1 = tkinter.IntVar(s.frames["Main"], value=0)
                s_c1 = ttk.Checkbutton(s.frames["Main"], text="'別の形式で開く'の有効化", variable=s_v1)
                s_c1.pack()
                s_b1.pack(side="bottom")
                s_b2.pack(side="bottom")
                def remove():
                    try:
                        file_addon.remove(file_addon.get_file()[adon.a_fl.curselection()[0]-1])
                        adon.a_fl.delete(adon.a_fl.curselection()[0]-1)
                    except:
                        pass
                    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
                s.style = ttk.Combobox(s.frames["Main"], width=30, value=self.root.style.theme_names())
                s.style.pack()
                s.a_fl = tkinter.Listbox(s.frames["Main"], width=30)
                s.a_fl.pack()
                s.a_fl.insert("end",self.txt["file_addon"]+":")
                s.a_b1 = ttk.Button(s.frames["Main"], text=self.txt["delete"], command=remove)
                s.a_b1.pack()
                s.style.insert("end",self.root.style.theme_use())
                s.style.bind('<<ComboboxSelected>>', lambda null: change(gomi=null, argv="style"))
                s.style.bind('<Return>', lambda null: change(gomi=null, argv="style"))
                for i in range(len(file_addons)):
                    s.a_fl.insert("end", "  " + file_addon_list[i] + "(" + file_addon_type[i] + " " +file_addon_type_ex[i] + ")")
                s.mainloop()
        #help
        class hlp():
            #show version
            def var():
                print("[info] show version")
                h = tkinter.Toplevel()
                h.title(self.txt["version"])
                h.img = tkinter.PhotoImage(file='./image/maruediter.gif', master=h)
                h_l1 = tkinter.Label(h, image=h.img)
                h_l1.pack(side="top")
                h_l2 = ttk.Label(h, text="Maru editer\nversion:" + info[0].lstrip("ver=") + "\nreversion:" + info[1].lstrip("rever=") + "\n2019-2020 Marusoftware")
                h_l2.pack(side="bottom")
            #show help
            def help():
                pass

        def main(open_path, num1, num2):
            file_addons[num2].file_main(openning[num1][0])

        def tkerror(exception, value, t):
            import tkinter
            sorry = tkinter.Toplevel()
            sorry.title("Maru editer - Error")
            tkinter.Label(sorry,text="We're sorry.\n\nError is huppun.").pack()
            t = tkinter.Text(sorry)
            t.pack()
            t.insert("end","Error report=========\n")
            t.insert("end",str(exception)+"\n")
            t.insert("end",str(value)+"\n")
            t.insert("end",str(t)+"\n")
            tkinter.Button(sorry, text="EXIT", command=sorry.destroy).pack()
            sorry.protocol("WM_DELETE_WINDOW",sorry.destroy)
            sorry.mainloop()
        # window class
        class window():
            #fullscreen
            def fullscreen(self):
                if self.fl.get() == 1:
                    self.root.attributes("-fullscreen", True)
                    print("[window]fullscreen on")
                else:
                    self.root.attributes("-fullscreen", False)
                    print("[window]fullscreen off")
            #open new window
            def newwin(self):
                subprocess.Popen([sys.argv[0]], shell=True)
            def welcome(self):
                if self.root.note.index("end") == 0:
                    self.root.note.welcome = ttk.Frame(self.root.note)
                    self.root.note.welcome.pack(fill="both",expand=True)
                    self.root.note.welcome.bt1 = ttk.Button(self.root.note.welcome,text=self.txt["new"],command=self.mfile.new)
                    self.root.note.welcome.bt1.pack(fill="both")#,side="left")
                    self.root.note.welcome.bt2 = ttk.Button(self.root.note.welcome,text=self.txt["open"],command=lambda: self.mfile.open_file(2))
                    self.root.note.welcome.bt2.pack(fill="both")#,side="right")
                    self.root.note.add(self.root.note.welcome,text=self.txt["welcome"])
                    self.root.note.welcome.opened = 1
                    self.root.menu.m_f.entryconfigure(self.txt["save"]+" (S)",state="disabled")
                    self.root.menu.m_f.entryconfigure(self.txt["save_as"]+" (A)",state="disabled")
                    self.root.menu.m_f.entryconfigure(self.txt["close_tab"]+" (C)",state="disabled")
                    if en_dnd:
                        self.root.note.dnd_frame = ttk.LabelFrame(self.root.note.welcome,text="Drop file here")
                        self.root.note.dnd_frame.pack(anchor="c",fill="both",expand=True)
                        self.root.note.dnd_frame.drop_target_register(DND_FILES)
                        self.root.note.dnd_frame.dnd_bind('<<Drop>>', lambda event:mfile.open_file(ofps=4,dnd=event))
                else:
                    if len(openning) != 0:
                        if self.root.note.welcome.opened == 1:
                            self.root.note.forget(0)
                            self.root.note.welcome.opened = 0
                            self.root.menu.m_f.entryconfigure(self.txt["save"]+" (S)",state="normal")
                            self.root.menu.m_f.entryconfigure(self.txt["save_as"]+" (A)",state="normal")
                            self.root.menu.m_f.entryconfigure(self.txt["close_tab"]+" (C)",state="normal")
        def import_addon(self):
            cd = os.path.abspath(os.path.dirname(sys.argv[0]))
            #import file addon
            file_addon_list = file_addon.get()
            file_addons = []
            file_addon_type = []
            file_addon_type_ex = []
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
                            file_addon_list.pop(-1)
                            file_addons.pop(-1)
                else:
                    break
            self.file_addon = {}
            self.file_addon.update(addon_list=file_addon_list)
            self.file_addon.update(addons=file_addons)
            self.file_addon.update(addon_type=file_addon_type)
            self.file_addon.update(addon_type_ex=file_addon_type_ex)
            print("[info] loaded addon:" + str(file_addon_list))
            print("[info] loaded addon type:" + str(file_addon_type))
            print("[info] loaded addon module:" + str(file_addons))
            #set current directory
            os.chdir(cd)

        def load_conf(self):
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
            self.conf = conf

            if "lang" in conf:
                print("[info]Language:"+conf["lang"])
                req = ["maruediter","welcome","exit","close_all","close_tab","save","save_as","open_from","open","new","file","open_new","full_screen","version","help",
                       "window","setting","addon","file_addon","delete","maruediter_file","all","error","error_cant_open","select_file_type","next","check","save_check",
                       "were_sorry","new_main","back","cancel","dir_name","file_name","choose_dir","file_name","new_sub1","new_sub2","new_check","wait","done","new_e1",
                       "new_e2","new_e3","done_msg","new_e1_msg"]
                if os.path.exists("./language/"+conf["lang"]+".lang"):
                    txt = pickle.load(open("./language/"+conf["lang"]+".lang","rb"))
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
            self.txt = txt

            if first:
                first = tkinter.Tk(className="Maruediter")
                first.title(self.txt["welcome"])
                first.l1 = ttk.Label(first, text="==="+self.txt["welcome"]+"===")
                first.l1.pack()
                first.b1 = ttk.Button(first,text=self.txt["next"],command=first.destroy)
                first.b1.pack()
                first.mainloop()

        def splash(self):
            self.splash = tkinter.Tk(baseName='Maruediter', className='Maruediter')
            self.splash.l = ttk.Label(self.splash, text="starting...")
            self.splash.l.pack(fill="x",side="bottom")
            self.splash.image = tkinter.PhotoImage(file='./image/init.png',master=self.splash)
            self.splash.i = ttk.Label(self.splash,image=self.splash.image)
            self.splash.i.pack(fill="both",side="top")
        def argv(self):
            if not len(sys.argv) == 0:
                if "-cui" in sys.argv:
                    cui()
                elif "--help" in sys.argv:
                    cui_help(0)
                    sys.exit()
    
        def Main(self):
            #global self.root, info, txt, conf, conf_path
            #tmp = ""
            #history = []
            info = ["ver=b1.1","rever=0"]
            openning = []
            #tema = 0
            #saved = 0
        
            try:
                self.root = Tk(baseName='Maruediter', className='Maruediter')
            except:
                import traceback
                print("We're sorry. Error is huppun.\nError report ========")
                print(traceback.format_exc())
                cui()
            
            #self.root.withdraw()
            
            self.root.style = Style()
            print("[info]Theme:"+self.conf["theme"])
            if "theme" in self.conf:
                self.root.style.theme_use(self.conf["theme"])
            self.root.title(self.txt["maruediter"])

            if os.path.exists("./image/maruediter.png"):
                self.root.iconphoto(True, tkinter.PhotoImage(file='./image/maruediter.png',master=self.root))
            else:
                print("[error] Icon file not found.")
        
            self.root.report_callback_exception=self.tkerror
            self.root.protocol("WM_DELETE_WINDOW", self.mfile.exit)
            #menu
            self.root.menu = tkinter.Menu(self.root)
            self.root.menu.m_f = tkinter.Menu(self.root.menu, tearoff=0)
            self.root.menu.m_f.add_command(label=self.txt["new"]+" (N)", command=lambda: self.mfile.new(self) ,under=len(self.txt["new"])+2)
            self.root.menu.m_f.add_command(label=self.txt["open"]+" (O)", command=lambda: threading.Thread(target=self.mfile.open_file,args=[1]).start(),under=len(self.txt["open"])+2)
            if "open_other" in self.conf:
                if self.conf["open_other"] == 1:
                    self.root.menu.m_f.add_command(label=self.txt["open_from"]+" (P)", command=lambda: threading.Thread(target=self.mfile.open_file,args=[2]).start(),under=len(self.txt["open_from"])+2)
            self.root.menu.m_f.add_command(label=self.txt["save_as"]+" (A)", command=lambda:self.mfile.save(other_name=1),under=len(self.txt["save_as"])+2)
            self.root.menu.m_f.add_command(label=self.txt["save"]+" (S)", command=self.mfile.save,under=len(self.txt["save"])+2)
            self.root.menu.m_f.add_command(label=self.txt["close_tab"]+" (C)",command=self.mfile.close_tab,under=len(self.txt["close_tab"])+2)
            self.root.menu.m_f.add_command(label=self.txt["close_all"]+" (X)", command=self.mfile.exit,under=len(self.txt["close_all"])+2)
            self.root.menu.m_d = tkinter.Menu(self.root.menu, tearoff=0)
            fl = tkinter.BooleanVar()
            self.root.menu.m_d.add_command(label=self.txt["open_new"]+" (N)", command=self.window.newwin,under=len(self.txt["open_new"])+2)
            self.root.menu.m_d.add_checkbutton(label=self.txt["full_screen"]+" (F)", variable=fl, command=self.window.fullscreen,under=len(self.txt["full_screen"])+2)
            self.root.menu.m_h = tkinter.Menu(self.root.menu, tearoff=0)
            self.root.menu.m_h.add_command(label=self.txt["version"]+" (V)", command=self.hlp.var,under=len(self.txt["version"])+2)
            self.root.menu.m_h.add_command(label=self.txt["help"]+" (H)", command=self.hlp.help,under=len(self.txt["help"])+2)
            self.root.menu.add_cascade(label=self.txt["file"]+" (F)", menu=self.root.menu.m_f,under=len(self.txt["file"])+2)
            self.root.menu.add_cascade(label=self.txt["window"]+" (W)", menu=self.root.menu.m_d,under=len(self.txt["window"])+2)
            self.root.menu.add_command(label=self.txt["setting"]+" (S)", under=len(self.txt["setting"])+2,command=self.mfile.setting)
            self.root.menu.add_cascade(label=self.txt["help"]+" (H)", menu=self.root.menu.m_h,under=len(self.txt["help"])+2)
            self.root.config(menu=self.root.menu)
            self.root._root = ttk.Frame(self.root)
            self.root._root.pack(fill="both",expand=True)
            try:
                self.root.note = CustomNotebook(self.root._root)
            except:
                self.root.note = ttk.Notebook(self.root._root)
            self.root.note.bind("<<NotebookTabClosed>>",lambda null:mfile.close_tab())
            self.root.note.pack(fill="both",expand=True)
            self.root.note.enable_traversal()
            if os.path.exists(sys.argv[-1]) and sys.argv[0] != sys.argv[-1]:
                print("[info] open from argv("+sys.argv[-1]+")")
                mfile.open_file(ofps=3,open_path=sys.argv[-1])
            if en_dnd:
                print("[info] tkdnd enable")
            self.window.welcome(self)
            self.root.geometry('500x500')
            self.root.update_idletasks()
            self.root.deiconify()
            self.splash.destroy()
            self.root.mainloop()
    if __name__ == "__main__":
        maruediter = Maruediter()
        maruediter.splash()
        maruediter.import_addon()
        maruediter.load_conf()
        maruediter.argv()
        maruediter.Main()
except Exception as e:
    import traceback
    import sys
    import os
    print("We're sorry. Error is huppun.")
    print(traceback.format_exc())
    #os._exit(-1)
    #sys.exit(-1)
    import tkinter
    sorry = tkinter.Tk(className="Maruediter")
    sorry.title("Maru editer - Error")
    tkinter.Label(sorry,text="We're sorry.\n\nError is huppun.").pack()
    t = tkinter.Text(sorry)
    t.pack()
    t.insert("end","Error report=========\n")
    t.insert("end",str(traceback.format_exc())+"\n")
    tkinter.Button(sorry, text="EXIT", command=lambda: exit()).pack()
    sorry.protocol("WM_DELETE_WINDOW",lambda: exit())
    sorry.mainloop()
    os._exit(-1)
    sys.exit(-1)
