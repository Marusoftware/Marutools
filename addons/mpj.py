import os
import shutil
import tkinter
from tkinter import ttk

class define():
    def GetRandomStr(num):
        import random
        import string
        dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
        return ''.join([random.choice(dat) for i in range(num)])

class edit():
    def get_info(argv):
        if argv == "enable":
            return 1
        if argv == "addon_var":
            return 0
        elif argv == "template_var":
            return "b0.0.1"
        elif argv == "__built_in__":
            return 1
        elif argv == "type":
            return ".mpj"
        elif argv == "type_ex":
            return "Maru editer project file"
        else:
            return 0
    def file_new(open_pas):
        pass

    def file_open(open_path, ofps, master):
        master.open_path = open_path
        master.directory = "./tmp"+define.GetRandomStr(5)
        if not os.path.exists(master.directory):
            os.mkdir(master.directory)
        if ofps == 0:
            pass
        else:
            shutil.copy(open_path, "./" + os.path.basename(open_path).rstrip(".mpj") + ".zip")
            shutil.unpack_archive("./" + os.path.basename(open_path).rstrip(".mpj") + ".zip", master.directory, "zip")
            os.remove("./"+os.path.basename(open_path).rstrip(".mpj")+".zip")
            if os.path.exists(master.directory+"/file.info"):
                master.info_file = open(master.directory+"/file.info","rb")
        return [open_path]
        #open

    def file_save(master, save_other="0"):
        s_zip = shutil.make_archive(master.directory, 'zip', root_dir=master.directory)
        shutil.move(master.directory+".zip", master.open_path)
        #os.remove(master.directory+".zip")
    def file_main(master):
        if os.path.exists(master.directory+"/file.info"):
            master.info_file = open(master.directory+"/file.info","rb")
    def file_exit(master):
        if os.path.exists(master.directory):
            shutil.rmtree(master.directory)
