import os, getpass, json, locale, platform, sys
__all__ = ["Config"]

class Config():
    def __init__(self, appname, module):
        self.default_conf = {}
        self.default_conf.update(welcome=1)
        if platform.system() == "Windows":
            self.default_conf.update(theme="xpnative")
        elif platform.system() == "Darwin":
            self.default_conf.update(theme="aqua")
        else:
            self.default_conf.update(theme="default")
        if None in locale.getlocale():
            self.default_conf.update([("lang",locale.getlocale()[0]),("encode",locale.getlocale()[1])])
        else:
            self.default_conf.update([("lang",locale.getdefaultlocale()[0]),("encode",locale.getdefaultlocale()[1])])
        if self.conf["lang"] == None:
            self.conf.update(lang="ja_JP")
        self.appinfo={"arch":(sys.maxsize > 2 ** 32), "os":platform.system(), "machine":platform.machine(), "appname":appname}
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            if platform.system() == "Darwin":
                cd = sys._MEIPASS
            elif platform.system() == "Windows":
                cd = os.path.abspath(os.path.dirname(sys.executable))
        else:
            cd = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.appinfo.update(cd=cd, share=os.path.join(cd,"share"), addons=list(os.path.join(cd,"addons")))
        if platform.system() == "Linux":
            self.conf_path = os.path.join(os.path.expanduser("~"),".config", appname, module+".conf")
            if self.appinfo["machine"] == "armv7":
                self.appinfo["share_os"]=os.path.join(cd,"share_os","raspi")
            else:
                if self.appinfo["is64bit"]:
                    self.appinfo["share_os"]=os.path.join(cd,"share_os","linux64")
                else:
                    self.appinfo["share_os"]=os.path.join(cd,"share_os","linux32")
        elif platform.system() == "Windows":
            try:
                self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming", appname, module+".conf")
            except:
                self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming", appname, module+".conf")
            if self.appinfo["arch"]:
                self.appinfo["share_os"]=os.path.join(cd,"share_os","win64")
            else:
                self.appinfo["share_os"]=os.path.join(cd,"share_os","win32")
        elif platform.system() == "Darwin":
            self.conf_path = os.path.join(os.path.expanduser("~"), ".config", appname, module+".conf")
            self.appinfo["share_os"]=os.path.join(cd,"share_os","macos")
        else:
            print(f'Unknown System. ({self.appinfo["os"]})Please report this to Marusoftware(marusoftware@outlook.jp).')
            exit(-1)
        self.readConf()
    def _syncData(self):
        json.dump(self.conf, open(self.conf_path, "w"))
    def readConf(self):
        self.conf_dir = os.path.dirname(self.conf_path)
        os.makedirs(self.conf_dir,exist_ok=True)
        self.appinfo.update(conf=self.conf_dir)
        if os.path.exists(self.conf_path):
            self.conf = json.load(open(self.conf_path, "r"))
        else:
            self.appinfo.update(first=True)
            self.conf=self.default_data
            self._syncData()
        for index in self.default_data:
            if not index in self.data:
                self.data[index]=self.default_data[index]
    def addConf(self, key, value):
        self.conf.update([(key,value)])
        self._syncData()
    def delConf(self, key):
        self.conf.pop(key)
        self._syncData()

class Lang():
    def __init__(self):
        pass
    def getText(self, lang):
        req = ['welcome', 'marueditor', 'exit', 'close_all', 'close_tab', 'save', 'save_as', 'save_from', 'open_from', 'open',
        'new', 'file', 'open_new', 'full_screen', 'help', 'window', 'setting', 'addon', 'file_addon', 'delete', 'marueditor_file',
        'all', 'error', 'error_cant_open', 'select_file_type', 'next', 'check', 'save_check', 'were_sorry', 'new_main', 'back', 
        'cancel', 'dir_name', 'choose_dir', 'file_name', 'new_sub1', 'new_sub2', 'new_check', 'wait', 'done', 'new_e1', 'new_e2', 
        'new_e3', 'done_msg', 'new_e1_msg', 'chk_upd', 'style', 'lang', 'st_open_from', 'st_dnd', 'new_check2', 'about']
        if os.path.exists(os.path.abspath("./language/"+lang+".lang")):
            txt = pickle.load(open("./language/"+lang+".lang","rb"))
            for i in range(len(req)):
                if req[i] in txt:
                    tmp = 1
                else:
                    tmp = 0
                    break
            if not tmp:
                raise KeyError("No Enough Key is in Language File.")
        else:
            raise FileNotFoundError("Language File is not found.(Path: "+os.path.abspath("./language/"+lang+".lang")+")")
        return txt