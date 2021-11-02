langs = {"en_US" : "en", "af" : "af", "zh" : "zh-CN", "zh_Hans" : "zh-CN", "zh_Hant" : "zh-TW",
 "zh_Hant_TW": "zh-TW", "zh_Hant_HK" : "zh-TW", "zh_Hant_MO" : "zh-TW"}
src_lang = ["ja_JP","ja"]
import os
cd=os.path.join(os.getcwd(),"language")
#cd = "/home/maruo/ドキュメント/program/Marutools/language"

import babel, googletrans, traceback, pickle, os, sys
os.chdir(cd)
translator=googletrans.Translator()
b={}
if len(sys.argv) > 1:
    l1 = {}
    print("process"+str(sys.argv))
    for i in range(len(sys.argv)-1):
        if sys.argv[i+1] in langs:
            l1[sys.argv[i+1]] = langs[sys.argv[i+1]]
            print(sys.argv[i+1])
    langs = l1
print(langs)
src = pickle.load(open(src_lang[0]+".lang","rb"))
for l in babel.localedata.locale_identifiers():
    if l in langs:
        if os.path.exists(l+".lang"):
            b = pickle.load(open(l+".lang","rb"))
        for t in src.keys():
            if not t in b:
                try:
                    b[t]=translator.translate(src[t], src=src_lang[1], dest=langs[l]).text
                except ValueError:
                    print([langs[l],t])
                    break
        pickle.dump(b, open(l+".lang","wb"))
        b = {}
