import libmarusoftware, os, sys
from importlib import import_module

class Addon():
    def __init__(self, logger, appinfo):
        self.loaded_addon={}
        self.loaded_addon_info={}
        self.extdict={}
        self.logger=logger
        self.appinfo=appinfo
    def install(self):
        pass
    def uninstall(self):
        pass
    def load(self, addon_file, addon_type):
        self.logger.debug(f"Start loading '{addon_file}' as {addon_type}.")
        try:
            module=import_module(os.path.splitext(os.path.basename(addon_file))[0], os.path.dirname(addon_file).replace(os.path.sep, "."))
        except:
            self.logger.warn(f"Can't import addon({addon_file}). (Not a collect python file.)")
            return False
        if addon_type == "editor" and hasattr(module, "Edit"):
            if not callable(module.Edit):
                self.logger.warn(f"Can't import addon({addon_file}). (Edit class is not callable.)")
                return False
            attrs=["name", "file_types", "save", "close", "new"]
            addon=module.Edit
            for attr in attrs:
                if not hasattr(addon, attr):
                    self.logger.warn(f"Can't import addon({addon_file}). (Missing {attr} attr.)")
                    break
            else:
                if addon.name in self.loaded_addon:
                    self.logger.warn(f"Can't import addon({addon_file}). (Used addon name.)")
                    return False
                self.loaded_addon[addon.name]=addon
                self.loaded_addon_info[addon.name]={"name":addon.name,"filetypes":addon.file_types}
                for ext in addon.file_types:
                    if not ext in self.extdict:
                        self.extdict[ext]=[]
                    self.extdict[ext].append(addon.name)
                self.logger.debug(f"{addon.name} was loaded")
                return True
            return False
    def unload(self):
        pass
    def loadAll(self, load_dirs, addon_type, ignorelist=[]):
        self.logger.info("Start addon loading.")
        sys.path.extend(load_dirs)
        for load_dir in load_dirs:
            self.logger.debug(f"Load from '{load_dir}' .")
            for addon_file in os.listdir(load_dir):
                addon_path=os.path.join(load_dir, addon_file)
                if not addon_path in ignorelist:
                    self.load(addon_file=addon_path, addon_type=addon_type)
        self.logger.info(f'{", ".join(list(self.loaded_addon.keys()))} was loaded.')
    def getAddon(self, addon, filepath, ext, ui, app, callback):
        api=AddonAPI(addon, self.appinfo, filepath, ext, ui, app, callback)
        addon_ctx=self.loaded_addon[addon](api)
        api.addon=addon_ctx
        return api

class AddonAPI(object):
    def __init__(self, name, appinfo, filepath, ext, ui, app, callback):
        self.name=name
        self.logger=libmarusoftware.core.Logger(name=name, log_dir=appinfo["log"])
        self.appinfo=appinfo
        self.filepath=filepath
        self.ext=ext
        self.ui=ui
        self.app=app
        self._saved=True
        self._callback=[callback]
        self.api_ver=0
        self.api_ver_minor=0
    @property
    def saved(self):
        return self._saved
    @saved.setter
    def saved(self, value):
        if self._saved != value:
            self._saved=value
            self._callback[0](self)
    def getConfig(self, module="main", default_conf={}):
        self.config=libmarusoftware.Config(appname=self.name, module=module, default_conf=default_conf, addon=self.appinfo)