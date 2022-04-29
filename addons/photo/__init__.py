class Edit():
    name="Photo"
    description="Photo editor"
    file_types=["png", "jpeg", "gif", "ico"]
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