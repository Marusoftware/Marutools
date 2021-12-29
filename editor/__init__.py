import argparse, libtools, os, sys

__version__="Marueditor b1.0.0"
__revision__="0"

class DefaultArgv:
    log_level=0

class Editor():
    def __init__(self, argv=DefaultArgv):
        self.argv=argv
    def Setup(self, appinfo=None):
        self.LoadConfig()
        self.Loadl10n()
        self.LoadLogger()
        if not appinfo is None:
            self.appinfo.update(**appinfo)
        libtools.core.adjustEnv(self.logger.getChild("AdjustEnv"), self.appinfo)
        self.addon=libtools.Addon(self.logger.getLogger("Addon"))
        self.addon.loadAll(self.appinfo["addons"],"editor")
        self.logger.info("start")
        self.ui=libtools.UI.UI(self.config, self.logger.getLogger("UI"))
        self.ui.changeIcon(os.path.join(self.appinfo["image"],"marueditor.png"))
        self.ui.setcallback("close", self.exit)
        self.ui.changeSize('500x500')
        self.ui.notebook=self.ui.Notebook()
    def mainloop(self):
        self.ui.mainloop()
    def exit(self):
        sys.exit()
    def LoadConfig(self):
        import platform, locale
        default_conf={"welcome":1, "lang":"ja_JP"}
        if platform.system() == "Windows":
            default_conf.update(theme="xpnative")
        elif platform.system() == "Darwin":
            default_conf.update(theme="aqua")
        else:
            default_conf.update(theme="default")
        if None in locale.getlocale():
            default_conf.update([("lang",locale.getlocale()[0]),("encode",locale.getlocale()[1])])
        else:
            default_conf.update([("lang",locale.getdefaultlocale()[0]),("encode",locale.getdefaultlocale()[1])])
        self.config=libtools.Config("Marueditor", default_conf=default_conf)
        self.appinfo=self.config.appinfo
        self.conf=self.config.conf
    def Loadl10n(self, language=None):
        if language is None:
            language=self.conf["lang"]
        req = ['welcome', 'marueditor', 'exit', 'close_all', 'close_tab', 'save', 'save_as', 'save_from', 'open_from', 'open',
        'new', 'file', 'open_new', 'full_screen', 'help', 'window', 'setting', 'addon', 'file_addon', 'delete', 'marueditor_file',
        'all', 'error', 'error_cant_open', 'select_file_type', 'next', 'check', 'save_check', 'were_sorry', 'new_main', 'back', 
        'cancel', 'dir_name', 'choose_dir', 'file_name', 'new_sub1', 'new_sub2', 'new_check', 'wait', 'done', 'new_e1', 'new_e2', 
        'new_e3', 'done_msg', 'new_e1_msg', 'chk_upd', 'style', 'lang', 'st_open_from', 'st_dnd', 'new_check2', 'about']
        self.lang = libtools.Lang(self.appinfo, req)
        self.txt = self.lang.getText(language)
    def LoadLogger(self):
        #logging
        if "log_dir" in self.conf:
            log_dir = self.conf["log_dir"]
        else:
            log_dir = self.appinfo["log"]
        self.logger=libtools.core.Logger(log_dir=log_dir, log_level=self.argv.log_level)
    def CreateMenu(self):
        self.ui.menu=self.ui.Menu(type="bar")
        self.ui.menu.apple=self.ui.menu.add_category("apple", name="apple")#Macos apple menu
        if not self.ui.menu.apple is None:
            self.ui.menu.apple.add_item(type="button", label="About Marueditor")
            self.ui.menu.apple.add_item(type="separator")
        #self.ui.menu.system=self.ui.menu.add_category("system", name="system")#Windows icon menu(Disabled)
        #if not self.ui.menu.system is None:
        #    self.ui.menu.system.add_item(type="checkbutton", label="Fullscreen", command=self.ui.fullscreen)
        #    self.ui.menu.system.add_item(type="separator")
        self.ui.menu.file=self.ui.menu.add_category("File")#File
        self.ui.menu.file.add_item(type="button", label="New File")
        self.ui.menu.file.add_item(type="button", label="Open")
        self.ui.menu.file.add_item(type="button", label="Open as...")
        self.ui.menu.file.add_item(type="button", label="Save")
        self.ui.menu.file.add_item(type="button", label="Save as...")
        self.ui.menu.file.add_item(type="button", label="Close tab")
        self.ui.menu.file.add_item(type="button", label="Close all")
        self.ui.menu.edit=self.ui.menu.add_category("Edit", name="edit")#Edit
        self.ui.menu.window=self.ui.menu.add_category("Window", name="window")#Window
        self.ui.menu.window.add_item(type="checkbutton", label="Fullscreen", command=self.ui.fullscreen)
        self.ui.menu.settings=self.ui.menu.add_item(type="button", label="Settings")#Settings
        self.ui.menu.edit=self.ui.menu.add_category("Help", name="help")#Help
    def open(self, as_diff_type=False, self_select=False):
        pass
    def save(self):
        pass
    def new(self):
        pass
    def close(self):
        pass
"""
        print(setup_info)
        if setup_info["gui_dnd"]:
            print("[info] tkdnd enable")
            #oot.__root.dnd_frame = ttk.LabelFrame(root.note.welcome,text="Drop file here")
            #root.__root.dnd_frame.pack(anchor="c",fill="both",expand=True)
            root.__root.drop_target_register(DND_FILES)
            root.__root.dnd_bind('<<Drop>>', lambda event: mfile.open_file(ofps=3, open_path=event.data))
        if os.path.exists(sys.argv[-1]) and sys.argv[0] != sys.argv[-1]:
            print("[info] open from argv("+sys.argv[-1]+")")
            mfile.open_file(ofps=3,open_path=sys.argv[-1])
        window.welcome()
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
                subprocess.Popen(["python3",sys.argv[0]])
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
                    if setup_info["gui_dnd"]:
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
                def open_file(ofps=0, open_path=None, dnd=None):#todo: rebuild
                    print("[file][open] run")
                    if ofps == 1:
                        if os.name == "posix":
                            ftype = [(txt["marueditor_file"],str(file_addon_type).lstrip("[").rstrip("]").replace(".","*.").replace("'","").replace(", ","|"))]
                        elif os.name == "nt":
                            ftype = [(txt["marueditor_file"],tuple(file_addon_type))]
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
                                    openning[-1][0].temp_dir = os.path.join(os.path.dirname(config.conf_path),mfile._randomstr(10))
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
                                    openning[-1][0].temp_dir = os.path.join(os.path.dirname(config.conf_path),mfile._randomstr(10))
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
                                        root.note.add(openning[-1][0], text=os.path.basename(config.open_path), sticky="nsew")
                                        window.welcome()
                                        openning[-1][0].temp_dir = os.path.join(os.path.dirname(config.conf_path),mfile._randomstr(10))
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
                                openning[-1][0].temp_dir = os.path.join(os.path.dirname(config.conf_path),mfile._randomstr(10))
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
                    e = tkmsg.askyesnocancel(txt["check"], txt["save_check"], parent=root)
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
                        select = root.note.index("current")
                        e = tkmsg.askyesnocancel(txt["check"], txt["save_check"], parent=root)
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
                            for tmp in self.widgets:
                                tmp.destroy()
                            for tmp in range(len(self.widgets)):
                                self.widgets.pop(0)
                    def packaw(self):
                        if len(self.widgets) != 0:
                            for tmp in self.widgets:
                                tmp.pack()
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
                            self.widgets.append(ttk.Button(self, text=txt["choose_dir"],
                            command=lambda:(self.widgets[1].delete("-1","end"),self.widgets[1].insert("end",filedialog.askdirectory(parent=self)))))
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
                            tkmsg.showinfo("Info","Language Changing will apply when you start Marueditor next time.", parent=s)
                            conf.update(lang=s.lang.get())
                        config.setConfig(conf)
                        #pickle.dump(conf, open(conf_path, "wb"))
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
                            addons.remove(addons.get_file()[s.a_fl.curselection()[0]-1])
                            s.a_fl.delete(s.a_fl.curselection()[0]-1)
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
                    h_l2 = ttk.Label(h._h, text="Version:" + info[0] + "  subVersion:" + info[1].lstrip("rever=") + "  2019-2021 Marusoftware")
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
                    pass """

def run(argv=DefaultArgv):
    app=Editor(argv)
    app.Setup()
    app.CreateMenu()
    app.mainloop()

if __name__ == "__main__":
    """INIT"""
    #argvParse
    argv_parser = argparse.ArgumentParser("Marueditor", description="Marueditor. The best editor.")
    argv_parser.add_argument("--shell", dest="shell", help="Start in shell mode.", action="store_true")
    argv_parser.add_argument("--debug", dest="debug", help="Start in debug mode.", action="store_true")
    argv_parser.add_argument("-log_level", action="store", type=int, dest="log_level", default=0 ,help="set Log level.(0-50)")
    argv = argv_parser.parse_args()
    run(argv)