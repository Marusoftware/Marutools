"""The editable, scrollable video timeline canvas."""
from addons.bluray.project import format_time
from addons.bluray.ui_support import tk_theme_colors

from .project import TRACKS, duration, end, length

RULER = 28
ROW = 48
GUTTER = 10


class Timeline:
    def __init__(self, parent, editor):
        from tkinter import Canvas
        from tkinter.ttk import Scrollbar

        self.editor = editor
        self.scale = 0.09  # Canvas pixels per millisecond.
        self.drag = None
        widget = parent.widget
        height = RULER + len(TRACKS) * ROW
        self.labels = Canvas(widget, width=54, height=height, highlightthickness=0)
        self.canvas = Canvas(widget, width=560, height=height, highlightthickness=0, takefocus=True)
        bar = Scrollbar(widget, orient="horizontal", command=self.scroll)
        self.canvas.configure(xscrollcommand=bar.set)
        self.labels.grid(row=0, column=0, sticky="ns")
        self.canvas.grid(row=0, column=1, sticky="nsew")
        bar.grid(row=1, column=1, sticky="ew")
        widget.columnconfigure(1, weight=1)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        self.canvas.bind("<<ThemeChanged>>", lambda event: self.draw())
        self.labels.bind("<Button-1>", self.choose_track)
        self.canvas.bind("<ButtonPress-1>", self.press)
        self.canvas.bind("<B1-Motion>", self.motion)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        for key, action in (("<Delete>", editor.delete_clip), ("<space>", editor.toggle_playback),
                            ("<Control-z>", editor.undo), ("<Control-y>", editor.redo)):
            self.canvas.bind(key, lambda event, action=action: (action(), "break")[1])

    def x(self, milliseconds):
        return GUTTER + milliseconds * self.scale

    def scroll(self, *args):
        self.canvas.xview(*args)
        self.draw()

    def choose_track(self, event):
        track = self.track_at(event.y)
        if track:
            self.editor.select_clip(None, track)
            self.draw()

    def time(self, canvas_x):
        return max(0, round((canvas_x - GUTTER) / self.scale))

    def track_at(self, y):
        index = (int(y) - RULER) // ROW
        return TRACKS[index] if 0 <= index < len(TRACKS) else None

    def pointer_location(self, x_root, y_root):
        x, y = x_root - self.canvas.winfo_rootx(), y_root - self.canvas.winfo_rooty()
        track = self.track_at(y)
        if 0 <= x < self.canvas.winfo_width() and track:
            return track, self.time(self.canvas.canvasx(x))
        return None

    def zoom(self, factor):
        self.scale = min(0.8, max(0.015, self.scale * factor))
        self.draw()
        self.show_position(self.editor.position)

    def row_y(self, track):
        return RULER + TRACKS.index(track) * ROW

    def draw(self):
        self.canvas.delete("all")
        self.labels.delete("all")
        background, foreground = tk_theme_colors(self.canvas)
        self.canvas.configure(background=background)
        self.labels.configure(background=background)
        timeline_end = max(duration(self.editor.project), self.editor.position)
        visible_width = max(1, self.canvas.winfo_width())
        width = max(visible_width, round(self.x(timeline_end + 2000)))
        height = RULER + len(TRACKS) * ROW
        self.canvas.configure(scrollregion=(0, 0, width, height))
        for track in TRACKS:
            y = self.row_y(track)
            active = track == self.editor.track
            self.labels.create_rectangle(0, y, 54, y + ROW, fill="#33618b" if active else background,
                                         outline=foreground, width=1)
            self.labels.create_text(27, y + ROW // 2, text=track, fill="white" if active else foreground)
            self.canvas.create_line(0, y, width, y, fill=foreground, stipple="gray25")
        # Draw ruler ticks only in the visible part, plus a margin for horizontal scrolling.
        start = self.time(self.canvas.canvasx(0))
        minimum = 100 / self.scale
        step = next((step for step in (500, 1000, 2000, 5000, 10000, 30000, 60000, 300000)
                     if step >= minimum), 600000)
        for tick in range(start // step * step, self.time(self.canvas.canvasx(visible_width)) + step, step):
            x = self.x(tick)
            self.canvas.create_line(x, RULER - 8, x, RULER, fill=foreground)
            self.canvas.create_text(x + 4, 10, text=format_time(tick), anchor="w", fill=foreground)
        for clip in self.editor.project["clips"]:
            self.draw_clip(clip)
        self.playhead = self.canvas.create_line(0, 0, 0, height, fill="#e3523b", width=2)
        self.position(self.editor.position)

    def draw_clip(self, clip):
        y = self.row_y(clip["track"])
        x0, x1 = self.x(clip["start"]), max(self.x(clip["start"]) + 2, self.x(end(clip)))
        selected = clip["id"] == self.editor.selected
        video = clip["track"].startswith("V")
        tag = "clip:" + clip["id"]
        self.canvas.create_rectangle(x0, y + 4, x1, y + ROW - 4,
                                     fill="#315e91" if video else "#326b53",
                                     outline="#ffcd65" if selected else "#bac8d2", width=2 if selected else 1,
                                     tags=(tag,))
        if x1 - x0 >= 36:
            name = self.editor.asset_name(clip["asset"])
            if clip["muted"]:
                name = "× " + name
            label_width = max(2, int((x1 - x0 - 12) / 8))
            if len(name) > label_width:
                name = name[:label_width - 1] + "…"
            self.canvas.create_text(x0 + 6, y + ROW // 2, text=name, fill="white", anchor="w", tags=(tag,))

    def position(self, milliseconds):
        x = self.x(milliseconds)
        self.canvas.coords(self.playhead, x, 0, x, RULER + len(TRACKS) * ROW)
        self.canvas.tag_raise(self.playhead)

    def show_position(self, milliseconds):
        x = self.x(milliseconds)
        left = self.canvas.canvasx(0)
        visible = self.canvas.winfo_width()
        if x < left or x > left + visible:
            extents = self.canvas.cget("scrollregion").split()
            width = max(1, float(extents[2]))
            self.canvas.xview_moveto(max(0, x - visible / 3) / width)
            self.draw()

    def press(self, event):
        self.drag = None
        self.canvas.focus_set()
        x, y = self.canvas.canvasx(event.x), event.y
        track = self.track_at(y)
        tags = [tag for item in self.canvas.find_overlapping(x, y, x, y) for tag in self.canvas.gettags(item)
                if tag.startswith("clip:")]
        self.editor.select_clip(tags[-1][5:] if tags else None, track)
        self.editor.seek_to(self.time(x))
        clip = self.editor.clip
        if clip:
            mode = "move"
            if self.x(end(clip)) - self.x(clip["start"]) >= 23:
                if x - self.x(clip["start"]) <= 8:
                    mode = "left"
                elif self.x(end(clip)) - x <= 8:
                    mode = "right"
            self.drag = (dict(clip), x, event.y, mode)
        self.draw()

    def candidate(self, event):
        clip, start_x, start_y, mode = self.drag
        x = self.canvas.canvasx(event.x)
        if abs(x - start_x) < 3 and abs(event.y - start_y) < 3:
            return None
        delta = round((x - start_x) / self.scale)
        updated = dict(clip)
        if mode == "left":
            change = max(-min(clip["start"], clip["in"]), min(length(clip) - 1, delta))
            updated.update(start=clip["start"] + change, **{"in": clip["in"] + change})
        elif mode == "right":
            asset = self.editor.project["assets"][clip["asset"]]
            updated["out"] = max(clip["in"] + 1, min(asset["duration"], clip["out"] + delta))
        else:
            updated.update(start=max(0, clip["start"] + delta), track=self.track_at(event.y) or clip["track"])
        return updated

    def motion(self, event):
        if not self.drag:
            return
        self.canvas.delete("ghost")
        clip = self.candidate(event)
        if clip:
            y = self.row_y(clip["track"])
            self.canvas.create_rectangle(self.x(clip["start"]), y + 3, self.x(end(clip)), y + ROW - 3,
                                         outline="#ffcd65", dash=(4, 3), width=2, tags=("ghost",))

    def release(self, event):
        if not self.drag:
            return
        clip = self.candidate(event)
        self.drag = None
        self.canvas.delete("ghost")
        if clip:
            self.editor.update_clip(clip)
