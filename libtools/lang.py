import os, pickle

class Lang():
    def __init__(self):
        pass
    def getText(self, lang):
        req = ['welcome', 'maruediter', 'exit', 'close_all', 'close_tab', 'save', 'save_as', 'save_from', 'open_from', 'open',
        'new', 'file', 'open_new', 'full_screen', 'help', 'window', 'setting', 'addon', 'file_addon', 'delete', 'maruediter_file',
        'all', 'error', 'error_cant_open', 'select_file_type', 'next', 'check', 'save_check', 'were_sorry', 'new_main', 'back', 
        'cancel', 'dir_name', 'choose_dir', 'file_name', 'new_sub1', 'new_sub2', 'new_check', 'wait', 'done', 'new_e1', 'new_e2', 
        'new_e3', 'done_msg', 'new_e1_msg', 'chk_upd', 'style', 'lang', 'st_open_from', 'st_dnd', 'new_check2', 'about']
        if os.path.exists(os.path.abspath("./language/"+lang+".lang")):
            txt = pickle.load(open("./language/"+lang+".lang","rb"))
            for i in range(len(req)):
                if req[i] in txt:
                    tmp = 1
                else:
                    tmp = 0
                    break
            if not tmp:
                raise
        else:
            raise FileNotFoundError
        return txt