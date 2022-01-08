try:
    import Tkinter as tk
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    from tkinter import ttk

class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab
    This code was copied from https://stackoverflow.com/questions/39458337/is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "WithClose.TNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)
        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            #self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.style=style
        if not "WithClose.TNotebook.close" in style.element_names():
            self.images = (
                tk.PhotoImage("img_close", data='''
                    R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                    d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                    5kEJADs=
                    '''),
                tk.PhotoImage("img_closeactive", data='''
                    R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                    AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                    '''),
                tk.PhotoImage("img_closepressed", data='''
                    R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                    d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                    5kEJADs=
                ''')
            )

            style.element_create("WithClose.TNotebook.close", "image", "img_close",
                                ("active", "pressed", "!disabled", "img_closepressed"),
                                ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("WithClose.TNotebook", [("WithClose.TNotebook.client", {"sticky": "nswe"})])
        style.layout("WithClose.TNotebook.Tab", [
            ("WithClose.TNotebook.tab", {
                "sticky": "nswe", 
                "children": [
                    ("WithClose.TNotebook.padding", {
                        "side": "top", 
                        "sticky": "nswe",
                        "children": [
                            ("WithClose.TNotebook.focus", {
                                "side": "top", 
                                "sticky": "nswe",
                                "children": [
                                    ("WithClose.TNotebook.label", {"side": "left", "sticky": ''}),
                                    ("WithClose.TNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })   
        ])
