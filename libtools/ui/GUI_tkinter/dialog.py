class Dialog():
    def __init__(self):
        pass
    def askfile(self, multi=False, save=False, **options):
        from .filedialog import askopenfilename, askopenfilenames, asksaveasfilename
        if save:
            return asksaveasfilename(**options)
        else:
            if multi:
                return askopenfilenames(**options)
            else:
                return askopenfilename(**options)
    def askdir(self, **options):
        from .filedialog import askdirectory
        return askdirectory(**options)
    def error(self):
        pass
    def question(self):
        pass