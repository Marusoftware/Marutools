import os, getpass, json, locale, platform, sys
__all__ = ["Config"]

class Config():
    def __init__(self, appname, module=None, default_conf={}, cd=None, conf_dir=None, addon=None):
        if module is None:
            module=appname
        self.default_conf = default_conf
        if addon is None:
            self.appinfo={"arch":(sys.maxsize > 2 ** 32), "os":platform.system(), "machine":platform.machine(), "appname":appname}
            if cd is None:
                if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
                    if platform.system() == "Darwin":
                        cd = sys._MEIPASS
                    elif platform.system() == "Windows":
                        cd = os.path.abspath(os.path.dirname(sys.executable))
                else:
                    cd = os.path.abspath(os.path.dirname(sys.argv[0]))
            self.appinfo.update(cd=cd, share=os.path.join(cd,"share"), addons=[os.path.join(cd,"addons")], lang=os.path.join(cd, "language"), image=os.path.join(cd,"image"))
            if platform.system() == "Linux":
                self.conf_path = os.path.join(os.path.expanduser("~"),".config", appname.lower(), module+".conf")
                if self.appinfo["machine"] == "armv7":
                    self.appinfo["share_os"]=os.path.join(cd,"share_os","raspi")
                else:
                    if self.appinfo["arch"]:
                        self.appinfo["share_os"]=os.path.join(cd,"share_os","linux64")
                    else:
                        self.appinfo["share_os"]=os.path.join(cd,"share_os","linux32")
            elif platform.system() == "Windows":
                try:
                    self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming", appname.lower(), module+".conf")
                except:
                    self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming", appname.lower(), module+".conf")
                if self.appinfo["arch"]:
                    self.appinfo["share_os"]=os.path.join(cd,"share_os","win64")
                else:
                    self.appinfo["share_os"]=os.path.join(cd,"share_os","win32")
            elif platform.system() == "Darwin":
                self.conf_path = os.path.join(os.path.expanduser("~"), ".config", appname.lower(), module+".conf")
                self.appinfo["share_os"]=os.path.join(cd,"share_os","macos")
            else:
                print(f'Unknown System. ({self.appinfo["os"]})Please report this to Marusoftware(marusoftware@outlook.jp).')
                exit(-1)
        else:
            self.appinfo=addon
            self.conf_path=os.path.join(self.appinfo["conf"], appname, module+".conf")
        if not conf_dir is None:
            self.conf_path=os.path.join(conf_dir, appname.lower(), module+".conf")
        self.conf_dir = os.path.dirname(self.conf_path)
        os.makedirs(self.conf_dir,exist_ok=True)
        self.appinfo.update(conf=self.conf_dir, log=os.path.join(self.conf_dir, "log"))
        self.readConf()
    def _syncData(self):
        json.dump(self.conf, open(self.conf_path, "w"))
    def readConf(self):
        if os.path.exists(self.conf_path):
            f=open(self.conf_path, "r")
            try:
                self.conf = json.load(f)
            except:
                f.close()
                print("Conf file was broken. So Backup old and create new one.")
                os.rename(self.conf_path, self.conf_path+".bak")
                self.appinfo.update(first=True)
                self.conf=self.default_conf
                self._syncData()
        else:
            self.appinfo.update(first=True)
            self.conf=self.default_conf
            self._syncData()
        for index in self.default_conf:
            if not index in self.conf:
                self.conf[index]=self.default_conf[index]
    def addConf(self, key, value):
        self.conf.update([(key,value)])
        self._syncData()
    def delConf(self, key):
        self.conf.pop(key)
        self._syncData()

class Lang():
    def __init__(self, appinfo, requirement_text):
        self.req=requirement_text
        self.appinfo=appinfo
    def getText(self, lang):
        lang_path=os.path.join(self.appinfo["lang"],lang+".lang")
        if os.path.exists(lang_path):
            with open(lang_path,"r", encoding="utf8") as f:
                txt = json.load(f)
            for i in range(len(self.req)):
                if self.req[i] in txt:
                    tmp = 1
                else:
                    tmp = 0
                    break
            if not tmp:
                raise KeyError("No Enough Key is in Language File.")
        else:
            raise FileNotFoundError("Language File is not found.(Path: "+os.path.abspath("./language/"+lang+".lang")+")")
        return txt