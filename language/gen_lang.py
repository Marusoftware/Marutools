src_lang = ["it","it"]
import os
from langs import langs, same
cd=os.getcwd()
#cd = "/home/maruo/ドキュメント/program/Marutools/language"

import babel, googletrans, json, os, sys
os.chdir(cd)
translator=googletrans.Translator()

src = json.load(open(src_lang[0]+".lang","r", encoding="utf8"))
def translate(lang, glang, langs=None):
    if langs is None:
        if os.path.exists(lang+".lang"):
            with open(lang+".lang","r", encoding="utf8") as f:
                temp = json.load(f)
        else:
            temp={}
    else:
        for i in langs:
            if os.path.exists(i+".lang"):
                with open(i+".lang","r", encoding="utf8") as f:
                    temp = json.load(f)
                break
            else:
                temp={}
    for id, src_text in src.items():
        if not id in temp:
            try:
                temp[id]=translator.translate(src_text, src=src_lang[1], dest=glang).text
            except ValueError:
                print(lang, id)
                break
    else:
        with open(lang+".lang","w", encoding="utf8") as f:
            json.dump(temp, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if input(f'The lang file will be save at "{cd}". Is it OK? [y/n]')!="y": exit()
    for glang, slangs in same.items():
        try:
            print(glang, end="", flush=True)
            translate(slangs[0], glang)
        except:
            print("...error!!")
        else:
            print("...done")