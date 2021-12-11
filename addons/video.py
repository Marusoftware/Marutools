import os
import pickle
import tkinter
from tkinter import ttk
import shutil
import filedialog
import media
import ttkwidgets
import tkinter.messagebox
import threading
import PIL
import PIL.ImageTk
import time

class edit():
    def get_info(argv):
        if argv == "enable":
            return 1
        if argv == "addon_var":
            return 0
        elif argv == "template_var":
            return "b0.0.3"
        elif argv == "__built_in__":
            return 0
        elif argv == "type":
            return ".mvid"
        elif argv == "type_ex":
            return "Maru video file"
        elif argv == "require":
            return []
        else:
            return 0
    
    def file_new(open_pas):
        pass

    def file_open(open_path, ofps, master):
        master.open_path = open_path
        if ofps == 0:
            pass
        else:
            pass
        return [open_path]

    def file_save(master):
        if os.path.exists(master.open_path):
            os.remove(master.open_path)
        pickle.dump(master.t.get('1.0', 'end -1c'),open(master.open_path,"wb"))
        
    def file_main(master):
        def show_menu(event, name):           
            if name == "track":
                master.f3.f1.menu.post(event.x_root,event.y_root)
                if event.widget in master.tracks1:
                    print(master.tracks1.index(event.widget))
                elif event.widget in master.tracks2:
                    print(master.tracks2.index(event.widget))
            elif name == "file":
                master.f1.lb1.menu.post(event.x_root,event.y_root)
        def add_file(path=None):
            if path != None:
                file = path
            else:
                file = filedialog.askopenfilename()
            if os.path.exists(file):
                if os.path.splitext(file)[1] in [".mp4",".webm"]:
                    if os.path.getsize(file):
                        if tkinter.messagebox.askyesno("確認","このファイルをプロジェクトファイルの内部に配置しますか?"):
                            shutil.copy(file,master.temp_dir)
                            file = os.path.join(master.temp_dir,file)
                        else:
                            pass
                        master.main[0]["files"].append(["video",media.video.Video()])
                        master.main[0]["files"][-1][1].openfile(file)
                        master.f1.lb1.insert("end",master.main[0]["files"][-1][0]+" : "+file)
        class preview():
            def __init__(self, vid):
                self.vid = vid
            def play(self):
                self.window = tkinter.Tk()
                self.f = ttk.Frame(self.window)
                self.f.pack()
                self.b = ttk.Button(self.window,text="Stop",command=preview.stop)
                self.b.pack()
                self.vid[1].play(frame=self.f)
                self.window.bind("<Configure>",lambda null: configure(null, 1))
                self.window.mainloop()
            def stop(self):
                self.vid[1].stop()
        def configure(null,num=0):
            if num == 0:
                if master.winfo_width()-100 > 0:
                    master.f3.t1.configure(width=master.winfo_width()-150)
            elif num == 1:
                if master.winfo_width()-100 > 0:
                    master.f3.t1.configure(width=master.winfo_width()-150)
        master.images = []
        master.files = {}
        master.files.update(movie=[])
        master.files.update(music=[])
        master.files.update(picture=[])
        master.files.update(movie_music=[])
        master.f0 = ttk.Frame(master)
        master.f1 = ttk.Frame(master)
        master.f2 = ttk.Frame(master)
        master.f3 = ttk.Frame(master)
        master.f0.grid(column=0,row=0, sticky = 'nsew', columnspan=2)
        master.f1.grid(column=0,row=1, sticky = 'nsew')
        master.f2.grid(column=1,row=1, sticky = 'nsew')
        master.f3.grid(column=0,row=2, sticky = 'nsew', columnspan=2)
        master.grid_columnconfigure(0,weight=1)
        master.grid_columnconfigure(1,weight=1)
        master.grid_rowconfigure(2,weight=1)
##        master.grid_rowconfigure(2, weight = 2)
##        master.f0.pack(side="top",expand=True)
##        master.f1.pack(side="left",expand=True)
##        master.f2.pack(side="left",expand=True)
##        master.f3.pack(side="bottom")
        if os.path.exists(master.open_path):
            master.t.insert("end",pickle.load(open(master.open_path,"rb")))
        master.f0.b1 = ttk.Button(master.f0, text="ファイル追加", command=add_file)
        master.f0.b1.pack(side="left")
        master.f1.l1 = ttk.Label(master.f1,text="ファイル:")
        master.f1.l1.pack(side="top",fill="both")
        master.f1.lb1 = tkinter.Listbox(master.f1)
        master.f1.lb1.pack(fill="both")
        master.f1.lb1.menu = tkinter.Menu(master,tearoff=False)
        master.f1.lb1.menu.add_command(label="ファイル追加", command=add_file)
        master.f1.lb1.menu.add_command(label="プレビュー", command=lambda: preview(master.main[0]["files"][master.f1.lb1.curselection()[0]]).play())
        master.f1.lb1.bind('<Button-3>',lambda event:show_menu(event, "file"))
        master.images.append(tkinter.PhotoImage(file='./image/empty_dark.png', master=master))
        master.f2.l1 = ttk.Label(master.f2,text="プレビュー:")
        master.f2.l1.pack(side="top",fill="both")
        master.f2.c1 = tkinter.Canvas(master.f2)
        master.f2.c1.pack()
        master.f2.c1.create_image(200, 150, image=master.images[-1])
        master.f3.t1 = ttkwidgets.TimeLine(master.f3,categories={str(key): {"text": "Category {}".format(key)} for key in range(0, 5)},extend=True,width=master.winfo_width())
        master.f3.t1.pack(expand=True)
        master.bind("<Configure>",configure)
        if os.path.exists(master.temp_dir+"/main.conf"):
            master.main = pickle.load(open(master.temp_dir+"/main.conf","rb"))
        else:
            master.main = []
            master.tmp = {}
            master.tmp.update(files=list())
            master.main.append(master.tmp)
            pickle.dump(master.main,open(master.temp_dir+"/main.conf","wb"))
    def file_exit(master):
        pass
if __name__ == "__main__":
    os.chdir("../")
    import sys
    sys.path.append(os.path.abspath("./share/"))
    import filedialog
    import media.video
    import ttkwidgets
    master = tkinter.Tk()
    master.temp_dir = "./"
    edit.file_open("./test.mvid",0,master)
    edit.file_main(master)
    edit.file_exit(master)
    master.mainloop()
