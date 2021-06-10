import os, getpass, pickle, locale, platform
__all__ = ["Config"]

class Config():
    def __init__(self):
        if platform.system() == "Linux":
            self.conf_path = os.path.join(os.path.expanduser("~"),".config","marueditor","marueditor.conf")
        elif platform.system() == "Windows":
            try:
                self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming","marueditor","marueditor.conf")
            except:
                self.conf_path = os.path.join(os.path.expanduser("~"),"Appdata","Roaming","marueditor","marueditor.conf")
        elif platform.system() == "Darwin":
                self.conf_path = "./"+ getpass.getuser() + "marueditor.conf"
        self.conf_dir = os.path.dirname(self.conf_path)
        os.makedirs(self.conf_dir,exist_ok=True)
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
    def setConfig(self, dictionary):
        self.conf = dictionary
        pickle.dump(self.conf ,open(self.conf_path,"wb"))