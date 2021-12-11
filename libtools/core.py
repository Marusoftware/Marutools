import sys, os, platform, logging

def adjustEnv():
    #setCurrentDirectoryAnd_macOS_BUNDLE_NAME
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        if platform.system() == "Darwin":
            cd = sys._MEIPASS
        elif platform.system() == "Windows":
            cd = os.path.abspath(os.path.dirname(sys.executable))
    else:
        if platform.system() == "Darwin":
            try:
                from Foundation import NSBundle
                bundle = NSBundle.mainBundle()
                if bundle:
                    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                    if info and info['CFBundleName'] == 'Python':
                        info['CFBundleName'] = "Marueditor"
            except:
                pass
        cd = os.path.abspath(os.path.dirname(sys.argv[0]))
    os.chdir(cd)
    # __pycache__ deletion
    sys.dont_write_bytecode = True
    #path setting
    sys.path.append(os.path.join(cd,"share"))#share library path
    setup_info={"arch":(sys.maxsize > 2 ** 32), "cd":cd, "share":os.path.join(cd,"share")}
    if platform.system() == "Windows":
        import ctypes
        if setup_info["arch"]:
            setup_info["share_os"]=os.path.join(cd,"share_os","win64")
        else:
            setup_info["share_os"]=os.path.join(cd,"share_os","win32")
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    elif platform.system() == "Linux":
        if platform.machine() == "armv7":
            setup_info["share_os"]=os.path.join(cd,"share_os","raspi")
        else: 
            if setup_info["is64bit"]:
                setup_info["share_os"]=os.path.join(cd,"share_os","linux64")
            else:
                setup_info["share_os"]=os.path.join(cd,"share_os","linux32")    
    elif platform.system() == "Darwin":
        setup_info["share_os"]=os.path.join(cd,"share_os","macos")
    else:
        print("Unknown System. ("+platform.system()+")Please report this to Marusoftware(marusoftware@outlook.jp).")
        exit(-1)
    os.environ["PATH"] += ":"+setup_info["share_os"]
    sys.path.append(setup_info["share_os"])
    return setup_info

class Logger():
    def __init__(self, log_dir=None, name="main", log_level=0):
        os.makedirs(log_dir ,exist_ok=True)
        print("Start Logging on ",os.path.join(log_dir, str(len(os.listdir(log_dir))+1)+".log"))
        logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s| %(message)s',level=log_level)
        logger = logging.getLogger(name)
        logger.stdErrOut= logging.StreamHandler()
        logger.stdErrOut.setLevel(log_level)
        logger.stdErrOut.setFormatter(logging.Formatter('%(levelname)s:%(asctime)s:%(name)s| %(message)s'))
        logger.fileOut= logging.FileHandler(os.path.join(log_dir, str(len(os.listdir(log_dir))+1)+".log"))
        logger.fileOut.setLevel(log_level)
        #logger.addHandler(logger.stdErrOut)#multiple stderr deletion
        logger.addHandler(logger.fileOut)
        self.logger=logger
    def getChild(self):
        pass
    def info(self, text):
        self.logger.info(text)
    def error(self, text):
        self.logger.error(text)
    def warn(self, text):
        self.logger.warn(text)
    def critical(self, text):
        self.logger.critical(text)