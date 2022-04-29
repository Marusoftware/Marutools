class Edit():
    name="Video"
    description="Video editor"
    file_types=["mp4","gif"]
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