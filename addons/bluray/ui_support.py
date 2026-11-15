"""Helpers for list events and native Tk surfaces."""

from copy import copy


def tk_theme_colors(widget):
    from tkinter.ttk import Style

    style = Style(master=widget)
    background = style.lookup("TFrame", "background")
    foreground = style.lookup("TLabel", "foreground")
    # Some native themes leave style values unset and rely on Tk system colors.
    from tkinter import Label

    if not background or not foreground:
        sample = Label(widget)
        try:
            background = background or sample.cget("background")
            foreground = foreground or sample.cget("foreground")
        finally:
            sample.destroy()
    return background, foreground


def split_frames(parent):
    if getattr(parent, "backend", None) == "tkinter":
        from tkinter.ttk import Panedwindow

        panes = Panedwindow(parent.widget, orient="horizontal")
        # Frame() creates its native widget under its parent's .root.
        # Make the panels actual children of the paned window so they
        # cannot be obscured by a sibling paned window in the Tk stack.
        pane_parent = frame_parent(parent, panes)
        left, right = pane_parent.Frame(), pane_parent.Frame()
        panes.add(left.widget, weight=0)
        panes.add(right.widget, weight=1)
        panes.pack(fill="both", expand=True)
    else:
        left, right = parent.Frame(), parent.Frame()
        for pane in (left, right):
            pane.pack(side="left", fill="both", expand=True)
    return left, right


def frame_parent(parent, widget):
    wrapper = copy(parent)
    wrapper.root = widget
    wrapper.children = []
    return wrapper


def project_tabs(parent):
    if not callable(getattr(parent, "Notebook", None)):
        return parent, parent
    notebook = parent.Notebook()
    if getattr(notebook, "backend", None) == "tkinter":
        notebook.parent = frame_parent(parent, notebook.widget)
    media = notebook.add_tab(label="素材")
    menu = notebook.add_tab(label="メニュー")
    notebook.pack(fill="both", expand=True)
    return media.frame, menu.frame


def install_history_menu(api, editor_type):
    ui = getattr(getattr(api, "app", None), "ui", None)
    edit_menu = getattr(getattr(ui, "menu", None), "edit", None)
    notebook = getattr(ui, "notebook", None)
    if getattr(edit_menu, "backend", None) != "tkinter" or getattr(notebook, "backend", None) != "tkinter":
        return None

    controller = getattr(edit_menu, "_bluray_history_menu", None)
    if controller is None:
        controller = HistoryMenu(edit_menu.menu, notebook, editor_type)
        edit_menu._bluray_history_menu = controller
    return controller


class HistoryMenu:
    def __init__(self, menu, notebook, editor_type):
        self.menu = menu
        self.notebook = notebook
        self.editor_type = editor_type
        self.commands = {}
        notebook.widget.bind("<<NotebookTabChanged>>", self.refresh, add="+")

    def active_editor(self):
        selected = self.notebook.widget.select()
        for tab in self.notebook.list_tab():
            if tab.id == selected:
                editor = getattr(getattr(tab, "addon", None), "addon", None)
                if isinstance(editor, self.editor_type):
                    return editor
                break
        return None

    def run(self, action):
        editor = self.active_editor()
        if editor is not None:
            getattr(editor, action)()

    def refresh(self, event=None):
        editor = self.active_editor()
        if not self.commands and editor is not None:
            for action, label in (("undo", "元に戻す"), ("redo", "やり直す")):
                self.menu.add_command(label=label, command=lambda action=action: self.run(action))
                self.commands[self.menu.entrycget("end", "command")] = action

        if not self.commands:
            return
        last = self.menu.index("end")
        for index in range(last if last is not None else -1, -1, -1):
            if self.menu.type(index) != "command":
                continue
            action = self.commands.get(self.menu.entrycget(index, "command"))
            if action is None:
                continue
            if editor is None:
                self.menu.delete(index)
            else:
                entries = editor.history.past if action == "undo" else editor.history.future
                self.menu.entryconfigure(index, state="normal" if entries else "disabled")
        if editor is None:
            self.commands.clear()


class SelectionList:
    def __init__(self, frame, height, width, on_select=None):
        self.control = frame.Input.List(height=height, selectmode="browse")
        self.control.pack(fill="both", expand=True)
        # Input.List exposes insertion and selection, with no removal or event hook.
        self.widget = self.control.widget
        self.widget.column("#0", width=width, minwidth=90)
        if on_select:
            self.widget.bind("<<TreeviewSelect>>", lambda event: on_select(), add="+")

    @property
    def selected(self):
        values = self.control.value
        return values[0] if values else None

    def select(self, key):
        self.control.set_selection((key,) if key else ())
        if key:
            self.widget.see(key)

    def replace(self, rows, selected=None):
        children = self.widget.get_children()
        if children:
            self.widget.delete(*children)
        ids = []
        for key, label in rows:
            ids.append(key)
            self.control.add_item(id=key, label=label, index="end")
        selected = selected if selected in ids else next(iter(ids), None)
        self.select(selected)


class SeekBar:
    """Select a title-relative position with a native themed scale."""

    def __init__(self, frame, on_change, on_seek):
        self.widget = None
        self.updating = False
        self.dragging = False
        self.duration = None
        if getattr(frame, "backend", None) != "tkinter":
            return
        from tkinter.ttk import Scale

        def change(value):
            if not self.updating:
                on_change(int(float(value)))

        self.widget = Scale(frame.widget, orient="horizontal", from_=0, to=1, command=change, state="disabled")
        def release(event):
            if self.dragging:
                self.dragging = False
                on_seek()

        def press(event):
            self.dragging = self.widget.instate(["!disabled"])

        self.widget.bind("<ButtonPress-1>", press)
        self.widget.bind("<ButtonRelease-1>", release)
        self.widget.bind("<KeyRelease-Left>", lambda event: on_seek())
        self.widget.bind("<KeyRelease-Right>", lambda event: on_seek())
        self.widget.bind("<Return>", lambda event: on_seek())
        self.widget.pack(fill="x", padx=8, pady=(4, 0))

    def update(self, position, duration):
        if self.widget is None:
            return
        self.updating = True
        try:
            if duration != self.duration:
                self.widget.configure(to=max(1, duration - 1) if duration else 1,
                                      state="normal" if duration and duration > 1 else "disabled")
                self.duration = duration
            self.widget.set(position)
        finally:
            self.updating = False
