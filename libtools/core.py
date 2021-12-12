import sys, os, platform, logging

def adjustEnv(logger):
    #setCurrentDirectoryAnd_macOS_BUNDLE_NAME
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        logger.debug("detect frozen")
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
                logger.debug("Error was happen on changeing MacOS ProcessName")
            else:
                logger.debug("MacOS ProcessName was succesfully changed.")
        cd = os.path.abspath(os.path.dirname(sys.argv[0]))
    # __pycache__ deletion
    sys.dont_write_bytecode = True
    #init setup_info
    setup_info={"arch":(sys.maxsize > 2 ** 32), "os":platform.system(), "machine":platform.machine(), "cd":cd, "share":os.path.join(cd,"share"), "addons":list(os.path.join(cd,"addons"))}
    #path setting
    if not setup_info["share"] in sys.path:
        sys.path.append(setup_info["share"])#share library path
    #platform specific
    if setup_info["os"] == "Windows":
        if setup_info["arch"]:
            setup_info["share_os"]=os.path.join(cd,"share_os","win64")
        else:
            setup_info["share_os"]=os.path.join(cd,"share_os","win32")
        #Hi DPI Support
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    elif setup_info["os"] == "Linux":
        if setup_info["machine"] == "armv7":
            setup_info["share_os"]=os.path.join(cd,"share_os","raspi")
        else:
            if setup_info["is64bit"]:
                setup_info["share_os"]=os.path.join(cd,"share_os","linux64")
            else:
                setup_info["share_os"]=os.path.join(cd,"share_os","linux32")    
    elif setup_info["os"] == "Darwin":
        setup_info["share_os"]=os.path.join(cd,"share_os","macos")
    else:
        logger.critical(f'Unknown System. ({setup_info["os"]})Please report this to Marusoftware(marusoftware@outlook.jp).')
        exit(-1)
    if not setup_info["share_os"] in os.environ["PATH"]:
        os.environ["PATH"] += ":"+setup_info["share_os"]
    if not setup_info["share_os"] in sys.path:
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
        logger.addHandler(logger.fileOut)
        self.logger=logger
        self.childs=[]
    def getChild(self, name):
        child=self.logger.getChild(name)
        self.childs.append(child)
        return child
    def getLogger(self, name):
        logger=logging.getLogger(name)
        self.childs.append(logger)
        return 
    def info(self, text):
        self.logger.info(text)
    def error(self, text):
        self.logger.error(text)
    def warn(self, text):
        self.logger.warn(text)
    def critical(self, text):
        self.logger.critical(text)