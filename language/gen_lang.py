langs = {"en_US" : "en", "af" : "af", "zh" : "zh-CN", "zh_Hans" : "zh-CN", "zh_Hant" : "zh-TW",
 "zh_Hant_TW": "zh-TW", "zh_Hant_HK" : "zh-TW", "zh_Hant_MO" : "zh-TW"}
src_lang = ["ja_JP","ja"]
cd = "/home/maruo/ドキュメント/program/Marutools/language"

import babel, googletrans, traceback, pickle, os, sys
os.chdir(cd)
translator=googletrans.Translator()
b={}
sys.argv.pop(0)
if len(sys.argv) > 0:
    l1 = {}
    print("process"+sys.argv)
    for i in range(len(sys.argv)):
        if i in langs:
            l1[i] = langs[i]
    langs = l1
            
src = pickle.load(open(src_lang[0]+".lang","rb"))
for l in babel.localedata.locale_identifiers():
    if l in langs:
        for t in src.keys():
            try:
                b[t]=translator.translate(src[t], src=src_lang[1], dest=langs[l]).text
            except ValueError:
                print([langs[l],t])
                break
        pickle.dump(b, open(l+".lang","wb"))
        b = {}
