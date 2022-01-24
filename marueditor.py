import argparse, libtools, os

__version__="Marueditor b1.0.0"
__revision__="3"

class DefaultArgv:
    log_level=0
    filepath=None

class Editor():
    def __init__(self, argv=DefaultArgv):
        self.argv=argv
        self.opening={}
    def Setup(self, appinfo=None):
        self.LoadConfig()
        self.Loadl10n()
        self.LoadLogger()
        if not appinfo is None:
            self.appinfo.update(**appinfo)
        libtools.core.adjustEnv(self.logger.getChild("AdjustEnv"), self.appinfo)
        self.addon=libtools.Addon(self.logger.getChild("Addon"), self.appinfo)
        self.addon.loadAll(self.appinfo["addons"],"editor")
        self.logger.info("start")
        self.ui=libtools.UI.UI(self.config, self.logger.getChild("UI"))
        self.ui.changeIcon(os.path.join(self.appinfo["image"],"marueditor.png"))
        self.ui.setcallback("close", self.exit)
        self.ui.changeSize('500x500')
        self.ui.notebook=self.ui.Notebook(close=True, command=self.close, onzero=self.exit)
        self.ui.notebook.pack(fill="both", expand=True)
    def mainloop(self):
        self.ui.mainloop()
    def LoadConfig(self):
        import platform, locale
        default_conf={"welcome":1, "lang":None, "open_as":True}
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
        req = ['file', 'new', 'open', 'open_as', 'save', 'save_as', 'close_tab', 'close_all', 'edit', 'window',
        'full_screen', 'open_window', 'setting', 'help', 'about', 'welcome', 'welcome_tab',
        'dnd_area', 'select_file_type', 'ok', 'cancel', 'error', 'error_cant_open',
        'new_main', 'next', 'new_sub1', 'new_sub2', 'check', 'save_check', 'st_open_from',
        'st_dnd', 'marueditor', 'exit', 'addon', 'file_addon', 'delete', 'all', 'were_sorry',
        'back', 'dir_name', 'choose_dir', 'file_name', 'new_check', 'wait', 'done', 'new_e1',
        'new_e2', 'new_e3', 'done_msg', 'new_e1_msg', 'chk_upd', 'style', 'lang', 'new_check2',
        'version', 'licence', 'marueditor_file']
        self.lang = libtools.Lang(self.appinfo, req)
        self.txt = self.lang.getText(language)
    def LoadLogger(self):
        #logging
        if "log_dir" in self.conf:
            self.appinfo["log"] = self.conf["log_dir"]
        log_dir = self.appinfo["log"]
        self.logger=libtools.core.Logger(log_dir=log_dir, log_level=self.argv.log_level, name="")
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
        self.ui.menu.file=self.ui.menu.add_category(self.txt["file"])#File
        self.ui.menu.file.add_item(type="button", label=self.txt["new"], command=self.new)
        self.ui.menu.file.add_item(type="button", label=self.txt["open"], command=self.open)
        if self.conf["open_as"]:
            self.ui.menu.file.add_item(type="button", label=self.txt["open_as"], command=lambda: self.open(force_select=True))
        self.ui.menu.file.add_item(type="button", label=self.txt["save"], command=self.save)
        self.ui.menu.file.add_item(type="button", label=self.txt["save_as"], command=lambda: self.save(as_other=True))
        self.ui.menu.file.add_item(type="button", label=self.txt["close_tab"], command=self.close)
        self.ui.menu.file.add_item(type="button", label=self.txt["close_all"], command=self.exit)
        self.ui.menu.edit=self.ui.menu.add_category(self.txt["edit"], name="edit")#Edit
        self.ui.menu.window=self.ui.menu.add_category(self.txt["window"], name="window")#Window
        self.ui.menu.window.add_item(type="checkbutton", label=self.txt["full_screen"], command=self.ui.fullscreen)
        self.ui.menu.window.add_item(type="button", label=self.txt["open_window"], command=lambda: run(argv=self.argv))
        self.ui.menu.settings=self.ui.menu.add_item(type="button", label=self.txt["setting"], command=self.setting)#Settings
        self.ui.menu.help=self.ui.menu.add_category(self.txt["help"], name="help")#Help
        self.ui.menu.help.add_item(type="button", label=self.txt["about"], command=self.version)
    def welcome(self):
        self.welcome_tab=self.ui.notebook.add_tab(label=self.txt["welcome"])
        self.welcome_tab.label=self.welcome_tab.Label(label=self.txt["welcome_tab"])
        self.welcome_tab.label.pack()
        self.welcome_tab.new=self.welcome_tab.Input.Button(label=self.txt["new"], command=self.new)
        self.welcome_tab.new.pack(fill="x", side="top")
        self.welcome_tab.open=self.welcome_tab.Input.Button(label=self.txt["open"], command=lambda: self.open(as_diff_type=True))
        self.welcome_tab.open.pack(fill="x", side="top")
        if self.welcome_tab.backend=="tkinter":
            if self.welcome_tab.dnd:
                def dnd_process(event):
                    for file in event.data:
                        self.open(file=file, as_diff_type=True)
                self.welcome_tab.frame=self.welcome_tab.Frame(label=self.txt["dnd_area"])
                self.welcome_tab.frame.pack(fill="both", expand=True)
                self.welcome_tab.frame.setup_dnd(dnd_process, "file")
    def open(self, file=None, as_diff_type=False, force_select=False):#TODO: mime and directory
        def select_addon(exts, file, recom=None):
            root=self.ui.makeSubWindow(dialog=True)
            root.title=root.Label(label=f"{self.txt['select_file_type']}\n{self.txt['file']}:{file}")
            root.title.pack()
            root.list=root.Input.List()
            root.list.pack(expand=True, fill="both")
            def cancel():
                root.list.set_selection([])
                root.close()
            def ok():
                if len(root.list.value) == 1:
                    root.close()
            root.ok=root.Input.Button(label=self.txt["ok"], command=ok)
            root.ok.pack(expand=True, fill="both", side="bottom")
            root.cancel=root.Input.Button(label=self.txt["cancel"], command=cancel)
            root.cancel.pack(expand=True, fill="both", side="bottom")
            for ext, addons in exts.items():
                for addon in addons:
                    if not root.list.exist_item(addon):
                        root.list.add_item(label=addon, id=addon)
                    root.list.add_item(label=ext, id=addon+"."+ext, parent=addon)
            root.wait()
            if len(root.list.value) == 1:
                value=root.list.value[0].split(".")
                return value[0], (value[1] if len(value)==2 else self.addon.loaded_addon_info[value[0]]["filetypes"][0])
            else:
                return
        if file is None:
            file=self.ui.Dialog.askfile()
            if not os.path.exists(file):
                return
        ext=os.path.splitext(file)[1].lstrip(".")
        if force_select:
            selected=select_addon(self.addon.extdict, file=file, recom=(self.addon.extdict[ext] if ext in self.addon.extdict else None))
            if selected is None:
                return
            addon, ext = selected
        else:
            if ext in self.addon.extdict:
                addon=self.addon.extdict[ext][0]
            else:
                if as_diff_type:
                    selected=select_addon(self.addon.extdict, file=file)
                    if selected is None:
                        return
                    addon, ext = selected
                else:
                    self.ui.Dialog.error(title=self.txt["error"], message=self.txt["error_cant_open"])
                    return
        label=f'{os.path.basename(file)} {f"[{ext}]" if os.path.splitext(file)[1]!="."+ext else ""}'
        tab=self.ui.notebook.add_tab(label=label)
        self.ui.notebook.select_tab("end")
        ctx=self.addon.getAddon(addon, file, ext, tab, self)
        self.opening[label]=ctx
        ctx.saved=False
    def save(self, as_other=False):
        if not self.ui.notebook.value in self.opening:
            return
        if as_other:
            file=self.ui.Dialog.askfile()
            if not os.path.exists(file):
                return
            self.opening[self.ui.notebook.value].addon.save(file)
        else:
            self.opening[self.ui.notebook.value].addon.save()
    def new(self, **options):
        def dialog():
            def close():
                buttons.next.release()
                root.close()
            root=self.ui.makeSubWindow(dialog=True)
            root.setcallback("close", close)
            root.changeSize('300x300')
            body=root.Frame()
            body.pack(side="top", fill="x")
            body.title=body.Label(label=self.txt["new_main"])
            body.title.pack()
            buttons=root.Frame()
            buttons.pack(side="bottom", fill="x")
            buttons.cancel=buttons.Input.Button(label=self.txt["cancel"], command=close)
            buttons.cancel.pack(side="left", fill="x")
            buttons.next=buttons.Input.Button(label=self.txt["next"])
            buttons.next.pack(side="right", fill="x")
            options={"file":None, "filetype":None}
            buttons.next.wait()
            if not body.exist():
                return options
            while 1:
                for i in options:
                    if options[i] is None:
                        break
                else:
                    break
                if i == "file":
                    body.title.configure(text=self.txt["new_sub1"])
                    body.file=body.Input.Form(type="filesave")
                    body.file.pack(fill="both", expand=True)
                elif i == "filetype":
                    body.title.configure(text=self.txt["new_sub2"])
                    body.filetype=body.Input.List()
                    body.filetype.pack(fill="both")
                    for ext, addons in self.addon.extdict.items():
                        for addon in addons:
                            if not body.filetype.exist_item(addon):
                                body.filetype.add_item(label=addon, id=addon)
                            body.filetype.add_item(label=ext, id=addon+"."+ext, parent=addon)
                buttons.next.wait()
                if not body.exist():
                    break
                if i == "file":
                    if body.file.value != "":
                        options["file"]=body.file.value
                    body.file.destroy()
                elif i == "filetype":
                    if len(body.filetype.value) == 1:
                        filetype=body.filetype.value[0].split(".")
                        options["filetype"]=filetype
                        options["addon"]=filetype[0]
                        if len(filetype) == 1:
                            options["ext"]=self.addon.loaded_addon_info[addon]["filetypes"][0]
                        else:
                            options["ext"]=filetype[1]
                    body.filetype.destroy()
            root.close()
            return options
        if not "file" in options or not "filetype" in options:
            options=dialog()
        if None in options.values():
            return
        file=options["file"]
        addon=options["addon"]
        ext=options["ext"]
        if getattr(self.addon.loaded_addon[addon], "append_ext", True):
            file+="."+ext
        label=f'{os.path.basename(file)} {f"[{ext}]" if os.path.splitext(file)[1]!="."+ext else ""}'
        tab=self.ui.notebook.add_tab(label=label)
        self.ui.notebook.select_tab("end")
        ctx=self.addon.getAddon(addon, file, ext, tab, self)
        self.opening[label]=ctx
        ctx.saved=False
        ctx.addon.new()
    def close(self, value=None, question=-1):
        if value is None:
            value=self.ui.notebook.value
        if not value in self.opening:
            self.ui.notebook.del_tab("current")
            return
        if not self.opening[value].saved:
            if question == -1:
                question=self.ui.Dialog.question("yesnocancel", self.txt["check"], f"{self.txt['save_check']}\n{self.txt['file']}:{value}")
            if question == True:
                self.save()
            elif question != False:
                return
        self.opening[value].addon.close()
        self.opening.pop(value)
        self.ui.notebook.del_tab("current")
    def exit(self):
        try:
            for i in self.opening:
                if not self.opening[i].saved:
                    question=self.ui.Dialog.question("yesnocancel", self.txt["check"], f"{self.txt['save_check']}\n{self.txt['file']}:{i}")
                    if question is None:
                        break
                else:
                    question=None
                self.close(i, question)
            else:
                self.ui.close()
        except RuntimeError:
            self.exit()
    def update_state(self):
        index=self.ui.notebook.value
        if not index in self.opening:
            return
        before=self.opening[index]
        old_index=index
        if before.saved and "*" in index:
            self.opening.pop(index)
            index=index.lstrip("*")
            self.ui.notebook.config_tab(old_index, text=index)
            self.opening[index]=before
        elif not before.saved and not "*" in index:
            self.opening.pop(index)
            index="*"+index
            self.ui.notebook.config_tab(old_index, text=index)
            self.opening[index]=before
        self.ui.notebook.callback()
    def version(self):
        root=self.ui.makeSubWindow(dialog=True)
        root.changeTitle(self.appinfo["appname"]+" - "+self.txt["about"])
        root.note=root.Notebook()
        root.note.pack(fill="both", expand=True)
        version=root.note.add_tab(label="Version")
        version.title=version.Image(image="init.png")
        version.title.pack()
        version.text=version.Label(label=f"{__version__} {__revision__} -2023 Marusoftware")
        version.text.pack()
        licence=root.note.add_tab(label="Licence")
        licence.text=licence.Input.Text(scroll=True, readonly=True)
        licence.text.pack(fill="both", expand=True)
        with open(os.path.join(self.appinfo["cd"], "LICENCE")) as f:
            licence.text.insert("end", f.read())
    def setting(self):
        root=self.ui.makeSubWindow(dialog=True)
        root.changeSize('300x200')
        root.note=root.Notebook()
        root.note.pack(fill="both", expand=True)
        editor=root.note.add_tab(self.txt["marueditor"])
        editor.open_as=editor.Input.CheckButton(label=self.txt["st_open_from"], default=self.conf["open_as"], command=lambda: self.config.addConf("open_as", editor.open_as.value))
        editor.open_as.pack()
        def setlang():
            self.config.addConf("lang", editor.lang.value)
            self.Loadl10n(language=editor.lang.value)
        editor.lang=editor.Input.Select(values=self.lang.lang_list, inline=True, default=self.lang.lang, command=setlang, label=self.txt["lang"]+":")
        editor.lang.pack()
        if self.ui.backend=="tkinter":
            style=editor.Input.Select(values=self.ui.style.theme_names(), inline=True, default=self.conf["theme"], command=lambda: (self.ui.style.theme_use(style.value),self.config.addConf("theme", style.value)), label=self.txt["style"]+":")
            style.pack()

"""
#help
class hlp():
    #show help
    def help():
        pass
    def update():
        pass """

def run(argv=DefaultArgv):
    app=Editor(argv)
    app.Setup()
    app.CreateMenu()
    app.welcome()
    if not argv.filepath is None:
        app.open(file=argv.filepath, as_diff_type=True)
    app.mainloop()

if __name__ == "__main__":
    """INIT"""
    #argvParse
    argv_parser = argparse.ArgumentParser("marueditor", description="Marueditor. The best editor.")
    argv_parser.add_argument("--shell", dest="shell", help="Start in shell mode.", action="store_true")
    argv_parser.add_argument("--debug", dest="debug", help="Start in debug mode.", action="store_true")
    argv_parser.add_argument("-log_level", action="store", type=int, dest="log_level", default=0 ,help="set Log level.(0-50)")
    argv_parser.add_argument("filepath", action="store", type=str, default=None ,help="Open file path.", nargs='?')
    argv = argv_parser.parse_args()
    run(argv)