import json, os, datetime

class Edit():
    name="Tex"
    description="Tex editor"
    file_types=["mtex"]
    def __init__(self, api):
        self.api=api
        self.text=self.api.ui.Input.Text(scroll=True, command=self.on_modify)
        self.text.pack(fill="both", expand=True)
        self.orig=""
        if os.path.exists(self.api.filepath):
            from zipfile import ZipFile, is_zipfile
            if is_zipfile(self.api.filepath):
                with ZipFile(self.api.filepath, "r") as zipfile:
                    filelist=zipfile.namelist()
                    for fname in filelist:
                        if fname.startswith("media/"):
                            zipfile.extract(fname)
                        elif fname=="struct.json":
                            import json
                            self.info=json.load(zipfile.open(fname, "r"))
                        else:
                            pass
            self.api.saved=True
        else:
            self.api.saved=False
            self.info={"title":"", "author":"", "date":datetime.datetime.now().isoformat()}
        try:
            from pylatex import Document
        except ImportError:
            self.api.ui.Dialog.error("pylatexがインストールされていません。(err1)")
            self.api.logger.error("pylatex not found(err1)")
            return
        self.doc=Document(documentclass="jarticle")
        self.doc.create()
    def save(self, file=None):
        if file is None:
            file=self.api.filepath
        with open(file, mode="w", encoding=self.encoding) as f:
            f.write(self.text.get('1.0', 'end -1c'))
        self.api.saved=True
    def new(self):
        pass
    def close(self):
        pass