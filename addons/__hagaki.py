from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import tkinter, random, string, pickle, os, sys

def randomstr(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
def file_open():
    return 0

#default var
varsion = "pre0.0.1beta"
openning = 0
lang = "en"
#---------

lang_en = ["Greeting Card","File","New","Help","Front(Name)","Back(Layout)"]
lang_jp = ["年賀状"]
#load setting
load = tkinter.Tk()
load.title("loading...")
load_l = ttk.Label(load, text="loading...")
load_l.pack()
load_p = ttk.Progressbar(load, length=200, value=0)
load_p.pack()
if os.path.exists("./.config"):
    config = pickle.load(open("./.config","rb"))
    lang = config["lang"]
else:
    config = {}
    config.update(lang="en")
    lang = "en"
    pickle.dump(config, open("./.config","wb"))
load_p.configure(value=50)
load_p.update
#load lang
if not os.path.exists("./."+lang+".lang"):
    messagebox.showerror("Error","[code:1]Languagefile is not found.")
    text = lang_en
else:
    text = pickle.load(open("./."+lang+".lang","rb"))
load.destroy()
#make window
root = tkinter.Tk()
root.title(text[0])
#menu
app_menu = tkinter.Menu(root)
root.configure(menu=app_menu)
app_menu_file = tkinter.Menu(app_menu)
app_menu.add_cascade(label="ファイル", menu=app_menu_file)
app_menu_file.add_command(label="新規作成")
app_menu_help = tkinter.Menu(app_menu)
app_menu_help.add_command(label="このアプリケーションについて")
app_menu.add_cascade(label="ヘルプ", menu=app_menu_help)
#notebook
ntbook = ttk.Notebook(root)
ntbook.pack(fill="both")
omote = ttk.Frame(root)
ura = ttk.Frame(root)
ntbook.add(omote, text="表(宛名)")
ntbook.add(ura, text="裏(レイアウト)")
#omote
omote_menu = ttk.Frame(omote)
omote_menu.pack(side="left")
omote_menu_b1 = ttk.Button(omote_menu,text="住所録新規作成")
omote_menu_b1.pack(side="left")
omote_menu_b2 = ttk.Button(omote_menu,text="インポート")
omote_menu_b2.pack(side="left")
omote_menu_b3 = ttk.Button(omote_menu,text="エクスポート")
omote_menu_b3.pack(side="left")
omote_preview = ttk.Frame(omote)
omote_preview.pack()
#ura
ura_menu = ttk.Frame(ura)
ura_menu.pack(side="left")
ura_menu_b1 = ttk.Button(ura_menu,text="作品新規作成")
ura_menu_b1.pack(side="left")
ura_menu_b2 = ttk.Button(ura_menu,text="インポート")
ura_menu_b2.pack(side="left")
ura_menu_b3 = ttk.Button(ura_menu,text="エクスポート")
ura_menu_b3.pack(side="left")
ura_preview = ttk.Frame(ura)
ura_preview.pack()
root.mainloop()
