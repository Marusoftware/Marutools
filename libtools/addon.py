import importlib, libtools, os, sys
from importlib import import_module

class Addon():
    def __init__(self, conf):
        self.loaded_addon={}
        self.conf=conf
    def loadAll(self, load_dirs:list):
        sys.path.extend(load_dirs)
        for load_dir in load_dirs:
            for addon_file in os.listdir(load_dir):
                
                addon=importlib.import_module(os.path.splitext(addon_file)[0])
                

class AddonAPI():
    def __init__(self, name, conf):
        self.name=name
        self.logger=libtools.core.Logger(name=name)