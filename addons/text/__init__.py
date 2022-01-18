import os

class Edit():
    name="Text"
    file_types=["txt","py"]
    def __init__(self, api):
        self.encoding="utf-8"
        self.lang="lang"
        self.api=api
        self.text=self.api.ui.Input.Text(scroll=True)
        self.text.pack(fill="both", expand=True)
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
                self.text.insert("end", f.read())
    def save(self, filename=None):
        pass
    def close(self):
        pass