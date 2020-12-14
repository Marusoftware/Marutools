#!/usr/bin/env python3
import pickle
import sys
import os
import urllib.request
import libtools

#os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

def add(file):
    if __name__ == "__main__":
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    else:
        os.chdir(os.path.dirname(__file__))
    data = []
    data2 = []
    if os.path.exists("./flist.list"):
        data = pickle.load(open("./flist.list", "rb"))
        #os.remove("./flist.list")
    else:
        pass
    if os.path.exists("./list.list"):
        data2 = pickle.load(open("./list.list", "rb"))
        #os.remove("./list.list")
    else:
        pass
    if os.path.exists(file):
        data.append(file)
        data2.append(os.path.basename(os.path.splitext(file)[0]))
        if os.path.splitext(file)[1] == ".py":
            pickle.dump(data, open("./flist.list", "wb"))
            pickle.dump(data2, open("./list.list", "wb"))
            print("OK")
            return 1
        elif os.path.splitext(file)[1] == ".pyw":
            pickle.dump(data, open("./flist.list", "wb"))
            pickle.dump(data2, open("./list.list", "wb"))
            print("OK")
            return 1
        elif os.path.splitext(file)[1] == ".pyc":
            pickle.dump(data, open("./flist.list", "wb"))
            pickle.dump(data2, open("./list.list", "wb"))
            print("OK")
            return 1
        else:
            print("[error]: can't import addon")
            return 0
    else:
        print("[error]: not found")
        pickle.dump(data, open("./flist.list", "wb"))
        pickle.dump(data2, open("./list.list", "wb"))
        return 0
def get():
    if __name__ == "__main__":
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
        if os.path.exists("./list.list"):
            data = pickle.load(open("./list.list", "rb"))
        print(data)
    else:
        os.chdir(os.path.dirname(__file__))
        if os.path.exists("./list.list"):
            data = pickle.load(open("./list.list", "rb"))
        return data
def get_file():
    if __name__ == "__main__":
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    else:
        os.chdir(os.path.dirname(__file__))
    if os.path.exists("./flist.list"):
        data = pickle.load(open("./flist.list", "rb"))
        print(data)
        return data
def remove(file):
    if __name__ == "__main__":
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    else:
        os.chdir(os.path.dirname(__file__))
    data = []
    data2 = []
    if os.path.exists("./flist.list"):
        data = pickle.load(open("./flist.list", "rb"))
        os.remove("./flist.list")
    else:
        pass
    if os.path.exists("./list.list"):
        data2 = pickle.load(open("./list.list", "rb"))
        os.remove("./list.list")
    else:
        pass
    if os.path.exists(file):
        data.remove(file)
        data2.remove(os.path.basename(os.path.splitext(file)[0]))
        if os.path.splitext(file)[1] == ".py":
            pickle.dump(data, open("./flist.list", "wb"))
            pickle.dump(data2, open("./list.list", "wb"))
            print("OK")
            return 1
        elif os.path.splitext(file)[1] == ".pyw":
            pickle.dump(data, open("./flist.list", "wb"))
            pickle.dump(data2, open("./list.list", "wb"))
            print("OK")
            return 1
        elif os.path.splitext(file)[1] == ".pyc":
            pickle.dump(data, open("./flist.list", "wb"))
            pickle.dump(data2, open("./list.list", "wb"))
            print("OK")
            return 1
        elif os.path.splitext(file)[1] == ".pyo":
            pickle.dump(data, open("./flist.list", "wb"))
            pickle.dump(data2, open("./list.list", "wb"))
            print("OK")
            return 1
        else:
            print("[error]: can't import addon")
            return 0
    else:
        print("[error]: not found")
        pickle.dump(data, open("./flist.list", "wb"))
        pickle.dump(data2, open("./list.list", "wb"))
        return 0
def install(iput):
    read = pickle.load(open("file_addons","rb"))
    if iput in read["addonlist"]:
        pass
def uninstall():
    pass
def update(url=None):
    if url == None:
        pass

if __name__ in "__main__":
    if len(sys.argv) == 0:
        pass
    else:
        if len(sys.argv) == 1:
            pass
        else:
            if "add" == sys.argv[0]:
                add(sys.argv[1])
    if "-shell" in sys.argv:
        while 1:
            print("command:", end="")
            iput = input()
            if "add" in iput:
                print("name:", end="")
                iput = input()
                if iput == "":
                    print("[error]: not found")
                else:
                    add(iput)
            elif "get_file" in iput:
                get_file()
            elif "get" in iput:
                get()
            elif "exit" in iput:
                exit()
            elif "remove" in iput:
                print("name:", end="")
                iput = input()
                if iput == "":
                    print("[error]: not found")
                else:
                    remove(iput)
            elif "install" in iput:
                print("name:", end="")
                iput = input()
                if iput == "":
                    print("[error]: not found")
                else:
                    install(iput)
            else:
                pass
            

