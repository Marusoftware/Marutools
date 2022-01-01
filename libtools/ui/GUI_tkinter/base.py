from . import WidgetBase

class Label(WidgetBase):
    def __init__(self, master, image=None, **options):
        super().__init__(master=master)
        if not image is None:
            from PIL import Image, ImageTk
            self.image=ImageTk.PhotoImage(Image.open(image))
            options.update(image=self.image)
        from tkinter.ttk import Label
        self.widget=Label(self.master, **options)
