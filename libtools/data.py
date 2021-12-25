import os, getpass, pickle, locale, platform, sys
__all__ = ["Config"]

class Config():
    def __init__(self):
        self.default_data = {}
        self.appinfo={"arch":(sys.maxsize > 2 ** 32), "os":platform.system(), "machine":platform.machine()}
        if os.path.exists(self.data_path):
            self.data = pickle.load(open(self.data_path, "rb"))
        else:
            self.data=self.default_data
            self._syncData()
        for index in self.default_data:
            if not index in self.data:
                self.data[index]=self.default_data[index]
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            if platform.system() == "Darwin":
                cd = sys._MEIPASS
            elif platform.system() == "Windows":
                cd = os.path.abspath(os.path.dirname(sys.executable))
        else:
            cd = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.appinfo.update(cd=cd, share=os.path.join(cd,"share"), addons=list(os.path.join(cd,"addons")))
        if platform.system() == "Linux":
            self.conf_path = os.path.join(os.path.expanduser("~"),".config","marueditor","marueditor.conf")
        elif platform.system() == "Windows":
            try:
                self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming","marueditor","marueditor.conf")
            except:
                self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming","marueditor","marueditor.conf")
        elif platform.system() == "Darwin":
                self.conf_path = "./"+ getpass.getuser() + "marueditor.conf"
        #platform specific
        if self.appinfo["os"] == "Windows":
            if self.appinfo["arch"]:
                self.appinfo["share_os"]=os.path.join(cd,"share_os","win64")
            else:
                self.appinfo["share_os"]=os.path.join(cd,"share_os","win32")
            #Hi DPI Support
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        elif self.appinfo["os"] == "Linux":
            if self.appinfo["machine"] == "armv7":
                self.appinfo["share_os"]=os.path.join(cd,"share_os","raspi")
            else:
                if self.appinfo["is64bit"]:
                    self.appinfo["share_os"]=os.path.join(cd,"share_os","linux64")
                else:
                    self.appinfo["share_os"]=os.path.join(cd,"share_os","linux32")    
        elif self.appinfo["os"] == "Darwin":
            self.appinfo["share_os"]=os.path.join(cd,"share_os","macos")
        else:
            print(f'Unknown System. ({self.appinfo["os"]})Please report this to Marusoftware(marusoftware@outlook.jp).')
            exit(-1)
        self.conf_dir = os.path.dirname(self.conf_path)
        os.makedirs(self.conf_dir,exist_ok=True)
    def _syncData(self):
        pickle.dump(self.data, open(self.data_path, "wb"))
    def getProperty(self, property_name):
        if not property_name in self.data:
            return False
        else:
            return self.data[property_name]
    def setProperty(self, property_name, value):
        self.data[property_name]=value
        self._syncData()
    def readConf(self):
        if os.path.exists(self.conf_path):
            try:
                self.conf = pickle.load(open(self.conf_path,"rb"))
            except:
                os.remove(self.conf_path)
            self.first = 0
        else:
            self.conf = {}
            self.conf.update(welcome=1)
            if platform.system() == "Windows":
                self.conf.update(theme="xpnative")
            elif platform.system() == "Darwin":
                self.conf.update(theme="aqua")
            else:
                self.conf.update(theme="default")
            if None in locale.getlocale():
                self.conf.update([("lang",locale.getlocale()[0]),("encode",locale.getlocale()[1])])
            else:
                self.conf.update([("lang",locale.getdefaultlocale()[0]),("encode",locale.getdefaultlocale()[1])])
            if self.conf["lang"] == None:
                self.conf.update(lang="ja_JP")
            pickle.dump(self.conf,open(self.conf_path,"wb"))
            self.first = 1
        return self.conf
    def addConf(self, key, value):
        self.conf.update([(key,value)])
        pickle.dump(self.conf ,open(self.conf_path,"wb"))
    def delConf(self, key):
        self.conf.pop(key)
        pickle.dump(self.conf ,open(self.conf_path,"wb"))

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