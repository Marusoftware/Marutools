class Edit():
    name="Audio"
    description="Audio editor"
    file_types=["wav","mp3"]
    def __init__(self, api):
        self.api=api
    def on_modify(self):
        pass
    def save(self, file=None):
        pass
    def new(self):
        pass
    def close(self):
        pass