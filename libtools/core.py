import sys, os, platform, logging

def cd_and_macosBN():
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

class Logger():
    def __init__(self, log_dir, name="main", log_level=0):
        os.makedirs(log_dir ,exist_ok=True)
        print("Start Logging on ",os.path.join(log_dir, str(len(os.listdir(log_dir))+1)+".log"))
        logging.basicConfig(format='%(levelname)s:%(asctime)s:%(name)s| %(message)s',level=argv.log_level)
        logger = logging.getLogger(name)
        logger.stdErrOut= logging.StreamHandler()
        logger.stdErrOut.setLevel(log_level)
        logger.stdErrOut.setFormatter(logging.Formatter('%(levelname)s:%(asctime)s:%(name)s| %(message)s'))
        logger.fileOut= logging.FileHandler(os.path.join(log_dir, str(len(os.listdir(log_dir))+1)+".log"))
        logger.fileOut.setLevel(log_level)
        #logger.addHandler(logger.stdErrOut)#multiple stderr deletion
        logger.addHandler(logger.fileOut)
        self.logger=logger
    def info(self, text):
        self.logger.info(text)
    def error(self, text):
        self.logger.error(text)
    def warn(self, text):
        self.logger.warn(text)
    def critical(self, text):
        self.logger.critical(text)