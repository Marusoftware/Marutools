import os

class Edit():
    name="Text"
    description="Text editor"
    file_types=["txt","py"]
    def __init__(self, api):
        self.encoding="utf-8"
        self.lang="lang"
        self.api=api
        self.text=self.api.ui.Input.Text(scroll=True, command=self.on_modify)
        self.text.pack(fill="both", expand=True)
        self.orig=""
        if os.path.exists(self.api.filepath):
            try:
                from chardet import UniversalDetector
            except:
                pass
            else:
                detector = UniversalDetector()
                try:
                    with open(self.api.filepath, mode='rb') as f:
                        while True:
                            binary = f.readline()
                            if binary == b'':
                                break
                            detector.feed(binary)
                            if detector.done:
                                break
                finally:
                    detector.close()
                self.encoding=detector.result["encoding"]
                self.lang=detector.result["language"]
            with open(api.filepath, "r", encoding=self.encoding) as f:
                self.orig=f.read()
                self.text.insert("end", self.orig)
            self.api.saved=True
        else:
            self.api.saved=False
    def on_modify(self):
        self.api.logger.debug("modify")
        if self.orig == self.text.get('1.0', 'end -1c'):
            return
        self.api.saved=False
        self.api.logger.debug("change")
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