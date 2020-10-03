from my_tkaddon import htmlwidget
from tkinter import ttk
import urllib.request
import tkinter

root = tkinter.Tk()
def b():
    local_filename, headers = urllib.request.urlretrieve(e1.get())
    print(htmlwidget.html.read((open(local_filename,"r",encoding="utf8"))))
e1 = ttk.Entry(root)
b1 = ttk.Button(root, text="GO", command=b)
e1.pack()
b1.pack()
