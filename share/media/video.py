import tkinter
from tkinter import ttk
import imageio
from PIL import ImageTk, Image
import time
from . import audio
import threading
from imageio.plugins.ffmpeg import FfmpegFormat
import _tkinter

class Video():
    def __init__(self):
        self.audio = audio.Audio()
        format = FfmpegFormat(
            "ffmpeg",
            "Many video formats and cameras (via ffmpeg)",
            ".mov .avi .mpg .mpeg .mp4 .mkv .wmv .webm .m2ts .mts",
            "I",
            )
        imageio.formats.add_format(format,True)
        self.stopd = 0
    def openfile(self, file_path):
        try:
            self.video = imageio.get_reader(file_path)
        except imageio.core.fetching.NeedDownloadError:
            imageio.plugins.avbin.download()
            self.video = imageio.get_reader(file_path)
        self.audio.openfile(file_path)
    
    def play(self, frame, place=0):
        self.stopd = 0
        self.frame = frame
        self.frame.vidframe = tkinter.Canvas(self.frame)
        self.frame.vidframe.pack(fill="both",expand=True)
        self.vid_frame_rate=self.video.get_meta_data()
        self.video_thread = threading.Thread(target=self._stream,args=(place,))
        self.video_thread.start()
    def pause(self):
        self.stopd = 1
    def stop(self):
        self.audio.stop()
        self.stopd = 1
    def goto(self,place):
        pass
##    def goto_audio(self,place):
##        self.audio.goto()
    def close(self):
        pass
    def _stream(self,place):
        self.audio.play()
        start_time=time.time()
        sleeptime = 1/self.video.get_meta_data()["fps"]
        frame_now = 0
        for image in self.video.iter_data():
            frame_now = frame_now + 1
            if frame_now*sleeptime >= place:
                if frame_now*sleeptime >= time.time()-start_time:
                    if not self.stopd:
                        try:
                            self.image = Image.fromarray(image)
                            self.image = self.image.resize((int(self.frame.winfo_width()),int(self.frame.winfo_height())),Image.BICUBIC)
                            self.frame_image = ImageTk.PhotoImage(self.image,master=self.frame)
                            self.frame.vidframe.config(image=self.frame_image)
                            self.frame.vidframe.image = self.frame_image
                            time.sleep(sleeptime)
                        except RuntimeError:
                            break
                        except _tkinter.TclError:
                            break
                    else:
                        break
                else:
                    pass
            else:
                pass
