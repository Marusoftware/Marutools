import sys
import os
cd = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(cd)
sys.path.append(os.path.join(cd,"share"))
is64bit = sys.maxsize > 2 ** 32
if os.name == "nt":
    if is64bit:
        sys.path.append(os.path.join(os.path.join(cd,"share_os"),"win64"))
    else:
        sys.path.append(os.path.join(os.path.join(cd,"share_os"),"win32"))
elif os.name == "posix":
    if is64bit:
        sys.path.append(os.path.join(os.path.join(cd,"share_os"),"linux_86_64"))
    else:
        sys.path.append(os.path.join(os.path.join(cd,"share_os"),"linux_i386"))
else:
    sys.path.append(os.path.join(os.path.join(cd,"share_os"),"macos"))
import media.video
import media.audio
import tkinter
from tkinter import ttk
import filedialog

def stop(audio_video):
    if audio_video:
        audio.stop()
        root.destroy()
    else:
        video.stop()
        root.destroy()

root = tkinter.Tk()
video = media.video.Video()
audio = media.audio.Audio()
f = ttk.Frame(root)
f.pack(fill="both",expand=True)
path = filedialog.askopenfilename()
if ".mp3" in path:
    audio.openfile(path)
    audio.play(f)
    root.protocol("WM_DELETE_WINDOW", lambda: stop(1))
    root.mainloop()
elif ".wav" in path:
    audio.openfile(path)
    audio.play(f)
    root.protocol("WM_DELETE_WINDOW", lambda: stop(1))
    root.mainloop()
elif ".mp4" in path:
    video.openfile(path)
    video.play(f)
    root.protocol("WM_DELETE_WINDOW", lambda: stop(0))
    root.mainloop()
elif ".webm" in path:
    video.openfile(path)
    video.play(f)
    root.protocol("WM_DELETE_WINDOW", lambda: stop(0))
    root.mainloop()
