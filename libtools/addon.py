import libtools, os, sys
from importlib import import_module

class Addon():
    def __init__(self, logger):
        self.loaded_addon={}
        self.loaded_addon_info={}
        self.extdict={}
        self.logger=logger
    def install(self):
        pass
    def uninstall(self):
        pass
    def load(self, addon_file, addon_type):
        try:
            module=import_module(os.path.splitext(os.path.basename(addon_file))[0], os.path.dirname(addon_file).replace(os.path.sep, "."))
        except:
            self.logger.warn(f"Can't import addon({addon_file}). (Not a collect python file.)")
            return
        if addon_type == "editor" and hasattr(module, "Edit"):
            if not callable(module.Edit):
                self.logger.warn(f"Can't import addon({addon_file}). (Edit class is not callable.)")
                return
            attrs=["name","file_types"]
            addon=module.Edit()#add args
            for attr in attrs:
                if not hasattr(addon.Edit, attr):
                    self.logger.warn(f"Can't import addon({addon_file}). (Missing {attr} attr.)")
                    break
            else:
                if addon.name in self.loaded_addon:
                    self.logger.warn(f"Can't import addon({addon_file}). (Used addon name.)")
                    return
                self.loaded_addon[addon.name]=addon
                self.loaded_addon_info[addon.name]={"name":addon.name,"file_types":addon.file_types}
                if not addon.file_types in self.extdict:
                    self.extdict[addon.file_types]=[]
                self.extdict[addon.file_types].append(addon.name)
    def unload(self):
        pass
    def loadAll(self, load_dirs:list, addon_type, ignorelist=[]):
        sys.path.extend(load_dirs)
        for load_dir in load_dirs:
            for addon_file in os.listdir(load_dir):
                addon_path=os.path.join(load_dir, addon_file)
                if not addon_path in ignorelist:
                    self.load(addon_file=addon_path, addon_type=addon_type)
                

class AddonAPI():
    def __init__(self, name, conf):
        self.name=name
        self.logger=libtools.core.Logger(name=name)