"""Marutools Video editor."""
from copy import deepcopy
from pathlib import Path
from subprocess import TimeoutExpired
from tempfile import TemporaryDirectory
from threading import Thread
from uuid import uuid4

from addons.bluray.l10n import host_language, use_language
from addons.bluray.preview import Preview
from addons.bluray.project import History, format_time
from addons.bluray.ui_support import SelectionList, split_frames

from .jobs import render_with_progress
from .locale import JA
from .project import (EXTENSION, accepts, add_clip, duration, empty_project, end, inspect_asset, load,
                      save as save_project, split_clip, validate_clip)
from .timeline import Timeline


class Edit:
    name = "Video"
    description = "Video timeline editor"
    file_types = [EXTENSION[1:], "mp4", "gif"]

    def __init__(self, api):
        self.api = api
        self.locale = host_language(api)
        self.japanese = self.locale.lower().replace("_", "-").split("-", 1)[0] == "ja"
        self.dialog = api.ui.Dialog
        self.project = empty_project()
        self.saved_project = None
        self.load_error = None
        self.selected = None
        self.track = "V1"
        self.position = 0
        self.history = History()
        self.preview = None
        self.playing = None
        self.proxy = None
        self.retired_proxies = set()
        self.workspace = None
        self.timeline = None
        self.drag_asset = None
        path = Path(api.filepath) if api.filepath else None
        if path and path.is_file():
            try:
                if path.suffix.lower() == EXTENSION:
                    self.project = load(path)
                else:
                    asset_id = self.register_asset(path)
                    asset = self.project["assets"][asset_id]
                    add_clip(self.project, asset_id, "V1" if asset["video"] is not None else "A1", 0)
            except (OSError, ValueError, TypeError, KeyError, TimeoutExpired) as exc:
                self.load_error = str(exc)
            else:
                self.saved_project = deepcopy(self.project)
        self.build_ui()
        if self.load_error:
            self.report(self.t("Could not open: {0}", self.load_error))
        elif not self.project["assets"]:
            self.report(self.t("Add media to begin editing."))

    def t(self, message, *args):
        if self.japanese:
            message = JA.get(message, message)
        return message.format(*args) if args else message

    def label(self, parent, text, **options):
        label = parent.Label(label=text, **options)
        label.configure(wraplength=0)
        label.pack(fill="x", padx=5, pady=2)
        return label

    def buttons(self, parent, *actions):
        row = parent.Frame()
        row.pack(fill="x", pady=2)
        result = []
        for caption, action in actions:
            button = row.Input.Button(label=self.t(caption), command=action, width=0)
            button.pack(side="left", padx=2)
            result.append(button)
        return result

    def build_ui(self):
        root = self.api.ui.Frame()
        root.pack(fill="both", expand=True, padx=6, pady=4)
        self.status = root.Label(label="")
        self.status.configure(wraplength=0)
        self.status.pack(side="bottom", fill="x", pady=(4, 0))
        if root.backend != "tkinter":
            self.report(self.t("The video timeline requires Tkinter."))
            return

        self.undo_button, self.redo_button, *_ = self.buttons(
            root, ("Undo", self.undo), ("Redo", self.redo), ("Export MP4…", self.export),
        )
        upper = root.Frame()
        upper.pack(fill="both", expand=True, pady=3)
        assets, monitor = split_frames(upper)
        self.label(assets, self.t("Media"))
        self.bin = SelectionList(assets, height=5, width=190, on_files=self.add_assets)
        self.bin.widget.bind("<Double-1>", lambda event: self.play_source(), add="+")
        self.bin.widget.bind("<ButtonPress-1>", self.begin_bin_drag, add="+")
        self.bin.widget.bind("<ButtonRelease-1>", self.drop_from_bin, add="+")
        self.buttons(assets, ("Add Media…", self.pick_assets), ("Add to Timeline", self.add_selected_asset))
        self.label(monitor, self.t("Monitor"))
        surface = monitor.Frame()
        surface.pack(fill="both", expand=True)
        with use_language(self.locale):
            self.preview = Preview(surface, self.play_timeline, lambda: None, self.preview_error, self.follow_preview)
        self.buttons(monitor, ("Preview Source", self.play_source), ("Play Timeline", self.play_timeline))
        self.buttons(monitor, ("Pause / Resume", self.toggle_playback), ("Stop", self.stop))
        self.time_label = self.label(monitor, "")
        self.buttons(root, ("Split at Playhead", self.split), ("Delete Clip", self.delete_clip),
                     ("Mute / Unmute Clip", self.mute), ("Zoom Out", lambda: self.timeline.zoom(0.7)),
                     ("Zoom In", lambda: self.timeline.zoom(1.4)))
        track_area = root.Frame()
        track_area.pack(fill="x")
        self.timeline = Timeline(track_area, self)
        self.clip_label = self.label(root, "")
        self.refresh()

    def report(self, message):
        self.status.configure(label=message)

    def can_edit(self):
        if self.load_error:
            self.report(self.t("Could not open: {0}", self.load_error))
            return False
        return self.timeline is not None

    def refresh(self):
        if not self.timeline:
            return
        current_asset = self.bin.selected
        self.bin.replace([(key, self.asset_name(key)) for key in self.project["assets"]], current_asset)
        self.api.saved = bool(self.load_error) or self.project == self.saved_project
        for button, stack in ((self.undo_button, self.history.past), (self.redo_button, self.history.future)):
            button.configure(state="normal" if stack else "disabled")
        if self.clip is None:
            self.selected = None
        self.update_clip_label()
        self.timeline.draw()
        self.update_time()

    def update_time(self, *, follow=False):
        self.time_label.configure(label=f"{format_time(self.position)} / {format_time(duration(self.project))}")
        self.timeline.position(self.position)
        if follow:
            self.timeline.show_position(self.position)

    def update_clip_label(self):
        clip = self.clip
        if clip:
            details = self.t("{0} · Start {1} · Source {2}–{3}", self.asset_name(clip["asset"]),
                             format_time(clip["start"]), format_time(clip["in"]), format_time(clip["out"]))
        else:
            details = ""
        self.clip_label.configure(label=details)

    @property
    def clip(self):
        return next((clip for clip in self.project["clips"] if clip["id"] == self.selected), None)

    def select_clip(self, key, track=None):
        self.selected = key
        if track is not None:
            self.track = track
        self.update_clip_label()

    def asset_name(self, asset_id):
        return Path(self.project["assets"][asset_id]["path"]).name

    def register_asset(self, path):
        asset = inspect_asset(path)
        key = uuid4().hex
        self.project["assets"][key] = asset
        return key

    def pick_assets(self):
        if not self.can_edit():
            return
        paths = self.dialog.askfile(multi=True, title=self.t("Add Media…"),
                                    filetypes=[(self.t("Media Files"), "*.mp4 *.mov *.mkv *.webm *.avi *.gif "
                                                "*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff "
                                                "*.wav *.mp3 *.m4a *.flac *.ogg *.aac *.opus"),
                                               (self.t("All Files"), "*")])
        if paths:
            self.add_assets(paths)

    def add_assets(self, paths):
        if not self.can_edit():
            return False
        if isinstance(paths, str):
            paths = (paths,)
        previous = deepcopy(self.project)
        existing = {asset["path"]: key for key, asset in self.project["assets"].items()}
        added, failed = [], []
        for name in paths:
            if not name:
                continue
            path = Path(name)
            try:
                if not path.is_file():
                    raise FileNotFoundError(name)
                absolute = str(path.resolve())
                if absolute not in existing:
                    key = self.register_asset(path)
                    existing[absolute] = key
                    added.append(key)
            except (OSError, ValueError, TimeoutExpired):
                failed.append(path.name)
        if added:
            self.record(previous, affects_render=False)
            self.bin.select(added[-1])
        if failed:
            self.report(self.t("Could not add: {0}", ", ".join(failed)))
        elif added:
            self.report(self.t("Added {0} media files.", len(added)))
        return bool(added)

    def begin_bin_drag(self, event):
        self.drag_asset = self.bin.widget.identify_row(event.y)

    def drop_from_bin(self, event):
        asset, self.drag_asset = self.drag_asset, None
        location = self.timeline.pointer_location(event.x_root, event.y_root)
        if location and asset in self.project["assets"]:
            self.insert_asset(asset, *location)

    def add_selected_asset(self):
        if not self.can_edit() or not self.bin.selected:
            return
        asset = self.project["assets"][self.bin.selected]
        track = self.track
        if not accepts(asset, track):
            track = "V1" if asset["video"] is not None else "A1"
        self.insert_asset(self.bin.selected, track, self.position)

    def insert_asset(self, asset_id, track, position):
        if not self.can_edit():
            return
        previous = deepcopy(self.project)
        try:
            clip = add_clip(self.project, asset_id, track, position)
        except ValueError as exc:
            self.report(self.t(str(exc)))
            return
        self.selected, self.track = clip["id"], track
        self.position = end(clip)
        self.record(previous)
        self.timeline.show_position(self.position)

    def update_clip(self, updated):
        clip = self.clip
        if not self.can_edit() or not clip or updated == clip or updated["id"] != clip["id"]:
            return
        try:
            validate_clip(self.project, updated)
        except ValueError as exc:
            self.report(self.t(str(exc)))
            return
        previous = deepcopy(self.project)
        clip.update(updated)
        self.track = updated["track"]
        self.record(previous)

    def split(self):
        clip = self.clip
        if not self.can_edit() or not clip:
            self.report(self.t("Select a timeline clip first."))
            return
        previous = deepcopy(self.project)
        try:
            right = split_clip(self.project, clip, self.position)
        except ValueError as exc:
            self.report(self.t(str(exc)))
            return
        self.selected = right["id"]
        self.record(previous)

    def mute(self):
        clip = self.clip
        if clip:
            self.update_clip({**clip, "muted": not clip["muted"]})

    def delete_clip(self):
        clip = self.clip
        if not self.can_edit() or not clip:
            return
        previous = deepcopy(self.project)
        self.project["clips"].remove(clip)
        self.record(previous)

    def record(self, previous, *, affects_render=True):
        self.history.record(previous)
        if affects_render:
            self.invalidate_proxy()
        self.refresh()

    def undo(self):
        if self.history.past and self.can_edit():
            self.project = self.history.undo(self.project)
            self.invalidate_proxy()
            self.refresh()

    def redo(self):
        if self.history.future and self.can_edit():
            self.project = self.history.redo(self.project)
            self.invalidate_proxy()
            self.refresh()

    def invalidate_proxy(self):
        if self.proxy is not None:
            self.retired_proxies.add(self.proxy)
        self.proxy = None
        if self.playing == "timeline":
            self.stop()

    def preview_error(self, message):
        self.report(message)
        if self.preview.playback_state == "stopped":
            self.playing = None

    def play_source(self):
        if not self.can_edit() or not self.bin.selected:
            return
        asset = self.project["assets"][self.bin.selected]
        kind = "image" if asset["still"] else "video" if asset["video"] is not None else "audio"
        self.play_media(asset["path"], "source", kind=kind)

    def play_media(self, path, mode, milliseconds=0, *, kind="video", seek=False):
        try:
            with use_language(self.locale):
                self.preview.play({"media": str(path), "kind": kind}, milliseconds, seek=seek)
        except (OSError, RuntimeError, ValueError) as exc:
            self.report(str(exc))
            return
        self.playing = mode

    def play_timeline(self):
        if not self.can_edit() or not self.project["clips"]:
            self.report(self.t("Add a clip to the timeline first."))
            return
        if not self.preview.available:
            self.report(self.preview.reason)
            return
        if self.proxy is None:
            if self.workspace is None:
                self.workspace = TemporaryDirectory(prefix="maruvideo-preview-", ignore_cleanup_errors=True)
            target = Path(self.workspace.name) / (uuid4().hex + ".mp4")
            if not self.run_render(target, (640, 360), proxy=True):
                return
            self.proxy = target
        if self.position >= duration(self.project):
            self.position = 0
            self.update_time()
        self.play_media(self.proxy, "timeline", self.position)

    def follow_preview(self, milliseconds):
        if self.playing == "timeline":
            timeline_end = duration(self.project)
            self.position = min(timeline_end, milliseconds)
            self.update_time(follow=True)
            if milliseconds >= timeline_end:
                self.stop()

    def seek_to(self, milliseconds):
        self.position = milliseconds
        self.update_time()
        if self.playing == "timeline" and self.proxy:
            if milliseconds < duration(self.project):
                self.play_media(self.proxy, "timeline", milliseconds, seek=True)
            else:
                self.stop()

    def toggle_playback(self):
        if self.playing is None:
            self.play_timeline()
        elif self.preview.playback_state == "active":
            with use_language(self.locale):
                self.preview.pause_resume()

    def stop(self):
        self.playing = None
        if self.preview is not None:
            self.preview.close()

    def run_render(self, target, size, *, proxy=False):
        self.stop()
        host = getattr(getattr(self.api, "app", None), "ui", None) or self.api.ui
        completed = render_with_progress(host, self.t, self.project, target, size=size, proxy=proxy)
        for path in tuple(self.retired_proxies):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                continue
            self.retired_proxies.remove(path)
        return completed

    def export(self):
        if not self.can_edit():
            return
        if not self.project["clips"]:
            self.report(self.t("Add a clip to the timeline first."))
            return
        target = self.dialog.askfile(save=True, title=self.t("Export MP4…"), defaultextension=".mp4",
                                     filetypes=[("MP4", "*.mp4")])
        if not target:
            return
        target = Path(target)
        if not target.suffix:
            target = target.with_suffix(".mp4")
        if target.suffix.lower() != ".mp4":
            self.report(self.t("Use an .mp4 extension for exports."))
            return
        if self.run_render(target, (1280, 720)):
            self.report(self.t("Exported {0}", target))

    def save(self, file=None):
        if not self.can_edit():
            return
        path = Path(file or self.api.filepath) if file or self.api.filepath else None
        if file and path.suffix.lower() != EXTENSION:
            self.report(self.t("Use a .maruvideo extension for projects."))
            return
        if path is None or path.suffix.lower() != EXTENSION:
            selected = self.dialog.askfile(save=True, title=self.t("Save Video Project…"),
                                           defaultextension=EXTENSION,
                                           filetypes=[(self.t("Marutools Video Project"), "*" + EXTENSION)])
            if not selected:
                return
            path = Path(selected)
            if not path.suffix:
                path = path.with_suffix(EXTENSION)
            if path.suffix.lower() != EXTENSION:
                self.report(self.t("Use a .maruvideo extension for projects."))
                return
        path = path.absolute()
        try:
            save_project(path, self.project)
        except OSError as exc:
            self.dialog.error(title=self.t("Save Video Project…"), message=str(exc))
            return
        changed_path = str(path) != self.api.filepath
        was_saved = self.api.saved
        self.api.filepath = str(path)
        self.saved_project = deepcopy(self.project)
        self.api.saved = True
        if changed_path and was_saved:
            update = getattr(getattr(self.api, "app", None), "update_state", None)
            if update:
                update(self.api)
        self.report(self.t("Saved {0}", path.name))

    def new(self):
        self.stop()
        self.invalidate_proxy()
        self.project = empty_project()
        self.saved_project = None
        self.load_error = None
        self.history = History()
        self.selected = None
        self.position = 0
        self.refresh()

    def close(self):
        workspace, self.workspace = self.workspace, None
        worker = self.preview.worker if self.preview is not None else None
        if self.preview is not None:
            self.preview.dispose()
        if workspace is not None:
            if worker is None:
                workspace.cleanup()
            else:
                def clean():
                    worker.join()
                    workspace.cleanup()
                Thread(target=clean, daemon=True, name="Video preview cleanup").start()
