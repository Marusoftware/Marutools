import os
import pickle
import tkinter
from tkinter import ttk
import cv2
import random
import string
import shutil
import filedialog
import tkinter.messagebox
import threading
import PIL
import PIL.ImageTk
import time

class define():
    def GetRandomStr(num):
        dat = string.digits + string.ascii_lowercase + string.ascii_uppercase
        return ''.join([random.choice(dat) for i in range(num)])

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
        else:
            return 0
    
    def file_new(open_pas):
        pass

    def file_open(open_path, ofps, master):
        master.open_path = open_path
        master.directory = "./tmp"+define.GetRandomStr(5)
        if not os.path.exists(master.directory):
            os.mkdir(master.directory)
        else:
            master.directory = "./tmp"+define.GetRandomStr(5)
            os.mkdir(master.directory)
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
                if os.path.splitext(file)[1] in [".mp4"]:
                    if os.path.getsize(file):
                        if tkinter.messagebox.askyesno("確認","このファイルをプロジェクトファイルの内部に\n配置しますか?"):
                            shutil.copy(file,master.directory)
                            file = os.path.join(master.directory,file)
                        else:
                            pass
                        master.main[0]["files"].append(["video",cv2.VideoCapture(file)])
                        if master.main[0]["files"][-1][1].isOpened():
                            master.f1.lb1.insert("end",master.main[0]["files"][-1][0]+" : "+file)
                        else:
                            master.main[0]["files"].pop(-1)
        def preview(p):
            class Preview:
                def __init__(self, window, window_title, video_source=0):
                    self.window = window
                    self.window.title(window_title)
                    self.video_source = video_source
                    self.vid = MyVideoCapture(self.video_source)
                    self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
                    self.canvas.pack(fill="both")
                    self.l = ttk.Label(window,text="0")
                    self.l.pack()
                    self.video_source.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
                    self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
                    self.btn_reset=ttk.Button(window, text="reset", command=lambda: self.video_source.set(cv2.CAP_PROP_POS_FRAMES, 0))
                    self.btn_reset.pack()
                    self.update()
                    self.window.mainloop()
                def snapshot(self):
                    ret, frame = self.vid.get_frame()
                    if ret:
                        cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                def update(self):
                    ret, frame = self.vid.get_frame()
                    if ret:
                        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame), master=self.window)
                        self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
                        self.l.configure(text=str(self.video_source.get(cv2.CAP_PROP_POS_FRAMES)))

                    self.window.after(int(self.video_source.get(5)), self.update)
            class MyVideoCapture:
                def __init__(self, video_source=0):
                    # Open the video source
                    self.vid = video_source
                    if not self.vid.isOpened():
                        raise ValueError("Unable to open video source", video_source)

                    self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                    self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
                def get_frame(self):
                    if self.vid.isOpened():
                        ret, frame = self.vid.read()
                        if ret:
                            return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        else:
                            return (ret, None)
                    else:
                        return (ret, None)
                def __del__(self):
                    if self.vid.isOpened():
                        self.vid.release()
            Preview(tkinter.Tk(),"Preview",p[1])
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
        master.f1.lb1.menu.add_command(label="プレビュー", command=lambda: preview(master.main[0]["files"][master.f1.lb1.curselection()[0]]))
        master.f1.lb1.bind('<Button-3>',lambda event:show_menu(event, "file"))
        master.images.append(tkinter.PhotoImage(file='./image/empty_dark.png', master=master))
        master.f2.l1 = ttk.Label(master.f2,text="プレビュー:")
        master.f2.l1.pack(side="top",fill="both")
        master.f2.c1 = tkinter.Canvas(master.f2)
        master.f2.c1.pack()
        master.f2.c1.create_image(200, 150, image=master.images[-1])
        master.f3.f1 = ttk.Frame(master.f3)
        master.f3.f1.grid(column=0,row=0, sticky = 'nsew')
        master.f3.f2 = ttk.Frame(master.f3)
        master.f3.f2.grid(column=1,row=0, sticky = 'nsew')
        master.f3.f1.menu = tkinter.Menu(master,tearoff=False)
        master.f3.f1.menu.add_command(label="dummy")
        if os.path.exists(master.directory+"/main.conf"):
            master.main = pickle.load(open(master.directory+"/main.conf","rb"))
        else:
            master.main = []
            master.tmp = {}
            master.tmp.update(files=list())
            master.main.append(master.tmp)
            pickle.dump(master.main,open(master.directory+"/main.conf","wb"))
        master.track = 5
        master.tracks1 = []
        master.tracks2 = []
        for i in range(master.track):
            master.tracks1.append(ttk.Button(master.f3.f1, text="track"+str(i)))
            master.tracks1[-1].pack()
            master.tracks1[-1].bind("<1>",lambda event:show_menu(event, "track"))
            master.tracks1[-1].bind('<Button-3>',lambda event:show_menu(event, "track"))
            master.tracks2.append(ttk.Frame(master.f3.f2, width = 1000, height = 26, relief="ridge"))
            master.tracks2[-1].pack()
            master.tracks2[-1].bind('<Button-3>',lambda event:show_menu(event, "track"))
    def file_exit(master):
        if os.path.exists(master.directory):
            shutil.rmtree(master.directory)
if __name__ == "__main__":
    os.chdir("../")
    master = tkinter.Tk()
    edit.file_open("./test.mvid",0,master)
    edit.file_main(master)
    edit.file_exit(master)
