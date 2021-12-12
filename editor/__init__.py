import argparse, libtools, os, sys

class Main():
    def __init__(self, setup_info=None):
        #LoadConfig
        config = libtools.Config()
        conf = config.readConf()
        #getl10n
        lang = libtools.Lang()
        txt = lang.getText(conf["lang"])
        #logging
        if "log_dir" in conf:
            log_dir = conf["log_dir"]
        else:
            log_dir = os.path.join(config.conf_dir,"log/")
        self.logger=libtools.core.Logger(log_dir=log_dir, log_level=argv.log_level)
        if not setup_info is None:
            self.setup_info=libtools.core.adjustEnv(logger=self.logger.getChild("AdjustEnv"))
        self.addon=libtools.Addon(conf, self.logger.getLogger("Addon"))
        self.addon.loadAll(self.setup_info["addons"],"editor")
        self.ui=libtools.UI(conf, self.logger.getLogger("UI"))

if __name__ == "__main__":
    """INIT"""
    #argvParse
    argv_parser = argparse.ArgumentParser("Marueditor", description="Marueditor. The best editor.")
    argv_parser.add_argument("--shell", dest="shell", help="Start in shell mode.", action="store_true")
    argv_parser.add_argument("--debug", dest="debug", help="Start in debug mode.", action="store_true")
    argv_parser.add_argument("-log_level", action="store", type=int, dest="log_level", default=0 ,help="set Log level.(0-50)")
    argv = argv_parser.parse_args()
    app=Main()