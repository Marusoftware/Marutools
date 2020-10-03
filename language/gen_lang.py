langs = {"en_US" : "en",}
src_lang = ["ja_JP","ja"]

import babel, googletrans, traceback, pickle

translator=googletrans.Translator()
b={}
src = pickle.load(open(src_lang[0]+".lang","rb"))
for l in babel.localedata.locale_identifiers():
    if l in langs:
        for t in src.keys():

            b[t]=translator.translate(src[t], src=src_lang[1], dest=langs[l]).text
        pickle.dump(b, open(l+".lang","wb"))
        b = {}
