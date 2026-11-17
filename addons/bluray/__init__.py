"""Marutools Blu-ray and DVD project editor."""
import copy
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from uuid import uuid4

from .l10n import editor_language, host_language, localized, tr
from . import bdmv
from .assets import AUDIO_TYPES, IMAGE_TYPES, MEDIA_LABELS, VIDEO_TYPES
from .assets import file_pattern, media_duration, media_kind, path_kind
from .export_dialog import show_export_dialog
from .disc_tracks import LANGUAGE
from .menu_objects import OBJECT_LABELS, SHAPES, capture_thumbnail, object_caption, menu_font, valid_color
from .menu_objects import SHOW_VIDEO_TITLE, VIDEO_TITLE_OPTIONS
from .menu_navigation import UNLINKED, page_buttons, page_count, target_page
from .menu_layout import MenuLayout
from .preflight import check_project, issue_message
from .preview import Preview
from .project import (PROJECT_EXTENSIONS, History, convert_project, empty_project, format_time, load,
                      make_chapter, make_title, parse_time)
from .project import save as save_project
from .ui_support import SeekBar, SelectionList, form_choice, install_history_menu, project_tabs, split_frames
from .video_project import is_video_project, load_timeline, timeline_duration

__version__ = "0.5"


class Edit:
    name = "Blu-ray and DVD"
    description = "Blu-ray and DVD project editor v" + __version__
    file_types = [extension[1:] for extension in PROJECT_EXTENSIONS.values()]

    def __init__(self, api):
        self.locale = host_language(api)
        self.initialize(api)

    @editor_language
    def initialize(self, api):
        self.api = api
        self.dialog = api.ui.Dialog
        self.disc_kind = "dvd" if api.ext.lower() == "marudvd" else "bluray"
        self.project = empty_project(self.disc_kind)
        self.saved_project = None
        self.history = History()
        self.active_title = None
        self.position = 0
        self.duration = None
        self.chapters = None
        self.chapter_window = None
        self.audio_preferences = None
        self.chapter_id = None
        self.load_error = None
        self.video_workspace = None
        self.video_proxies = {}
        self.host_tab_binding = None
        if api.filepath and os.path.isfile(api.filepath):
            try:
                self.project = load(api.filepath, self.disc_kind)
            except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
                self.load_error = str(exc)
            else:
                self.saved_project = copy.deepcopy(self.project)
        self.build_ui()
        notebook = getattr(getattr(getattr(api, "app", None), "ui", None), "notebook", None)
        if getattr(notebook, "backend", None) == "tkinter":
            binding = notebook.widget.bind("<<NotebookTabChanged>>", localized(self.return_to_disc), add="+")
            self.host_tab_binding = (notebook.widget, binding)
        self.refresh()
        if self.load_error:
            self.report(tr("プロジェクトを開けませんでした。 ") + self.load_error)
        elif self.project["titles"]:
            self.report(tr("タイトルを選択して編集できます。"))
        else:
            self.report(tr("素材または BDMV を追加してください。"))

    def frame(self, parent, **placement):
        widget = parent.Frame()
        widget.pack(**placement)
        return widget

    def label(self, parent, text, **options):
        widget = parent.Label(label=text, **options)
        widget.configure(wraplength=0)
        widget.pack(fill="x", padx=8, pady=3)
        return widget

    def buttons(self, parent, *actions, side="top"):
        row = self.frame(parent, side=side, fill="x", padx=4, pady=3)
        buttons = []
        for caption, command in actions:
            widget = row.Input.Button(label=caption, command=localized(command), width=0)
            widget.pack(side="left", padx=2)
            buttons.append(widget)
        return buttons

    def build_ui(self):
        root = self.api.ui.Frame()
        root.pack(fill="both", expand=True)
        convert_label = tr("Blu-ray プロジェクトに変換…") if self.disc_kind == "dvd" else tr("DVD プロジェクトに変換…")
        self.buttons(root, (tr("書き出し"), self.export_disc), (convert_label, self.save_converted_copy))
        self.history_buttons = []
        self.history_menu = install_history_menu(self.api, Edit)
        if self.history_menu is None:
            self.history_buttons = self.buttons(root, (tr("元に戻す"), self.undo), (tr("やり直す"), self.redo))
        else:
            # The host attaches the addon context to the tab after construction.
            root.widget.after_idle(self.history_menu.refresh)
        footer = self.frame(root, side="bottom", fill="x", padx=8, pady=4)
        details = footer.Input.Button(label=tr("詳細設定 ›"), command=localized(self.properties), width=0)
        details.pack(side="right", padx=2)
        audio_settings = footer.Input.Button(label=tr("音声出力"), command=localized(self.configure_audio), width=0)
        audio_settings.pack(side="right", padx=2)
        check = footer.Input.Button(label=tr("チェック"), command=localized(self.validate), width=0)
        check.pack(side="right", padx=2)
        self.status = footer.Label(label="")
        self.status.pack(side="left", fill="x", expand=True, padx=4)

        media_tab, menu_tab = project_tabs(root)
        self.menu_layout = None
        if getattr(menu_tab, "backend", None) == "tkinter":
            self.menu_layout = MenuLayout(menu_tab, self)

        self.buttons(media_tab, (tr("＋ 素材を追加"), self.add_asset), (tr("BDMVを開く"), self.import_bdmv))
        body = self.frame(media_tab, fill="both", expand=True, padx=8, pady=(2, 0))
        left, right = split_frames(body)
        self.label(left, tr("素材"))
        self.titles = SelectionList(left, 3, 245, self.title_selected, on_files=self.add_assets)
        self.buttons(left, (tr("名前変更"), self.rename_title), (tr("削除"), self.delete_title),
                     ("↑", lambda: self.move_title(-1)), ("↓", lambda: self.move_title(1)))
        self.edit_video_button = self.buttons(left, (tr("Video で編集"), self.edit_video_project))[0]
        track_settings = tr("音声・字幕…") if self.disc_kind == "dvd" else tr("音声・字幕・ポップアップ…")
        self.buttons(left, (track_settings, self.edit_disc_tracks),
                     (tr("再生後の動作…"), self.edit_playback_end))
        self.preview = Preview(
            self.frame(right, fill="both", expand=True), self.play,
            lambda: self.report(tr("プレビューを開始しました。")),
            lambda message: self.report(tr("プレビュー: {0}", message)),
            self.follow_playback,
        )
        self.buttons(right, (tr("再生"), self.play), (tr("一時停止／再開"), self.pause), (tr("停止"), self.stop))
        self.seek_bar = SeekBar(right, self.set_position, self.seek_from_bar)
        self.buttons(right, (tr("この位置にチャプターを追加"), self.add_chapter),
                     (tr("チャプター一覧"), self.show_chapters))
        self.time_label = self.label(right, "", anchor="center")
        self.source_label = self.label(right, "", anchor="center")

    def report(self, message):
        self.status.configure(label=message)

    def form(self, title, fields, choices=None, note=None,
             extra_choices=(), color_fields=(), font_field=None):
        parent = self.chapter_window or self.api.ui
        window = parent.makeSubWindow(dialog=True)
        window.changeTitle(title)
        result = None
        inputs = {}
        if note:
            note_label = window.Label(label=note)
            note_label.configure(wraplength=500)
            note_label.pack(fill="x", padx=12, pady=(8, 2))
        for label, value in fields:
            field_label = window.Label(label=label)
            field_label.configure(wraplength=0)
            field_label.pack(fill="x", padx=12, pady=(8, 2))
            inputs[label] = window.Input.Form(width=46)
            inputs[label].set(value)
            inputs[label].pack(fill="x", padx=12)
            if label == font_field or label in color_fields:
                row = window.Frame()
                row.pack(fill="x", padx=10, pady=4)

                def choose(field=label, chooser_parent=row):
                    if field in color_fields:
                        from tkinter.colorchooser import askcolor

                        current = inputs[field].value
                        _, color = askcolor(color=current if valid_color(current) else None,
                                            parent=chooser_parent.widget, title=field)
                        if color:
                            inputs[field].set(color)
                    else:
                        path = window.Dialog.askfile(title=tr("{0}を選択", field),
                                                     filetypes=[(tr("フォント"), "*.ttf *.otf *.ttc")])
                        if path:
                            inputs[field].set(os.path.abspath(path))

                caption = tr("色を選択…") if label in color_fields else tr("参照…")
                for caption, command in ((caption, choose), (tr("解除"), lambda field=label: inputs[field].set(""))):
                    row.Input.Button(label=caption, command=localized(command)).pack(side="left", padx=2)
        selections = {}
        selectors = (*extra_choices, choices) if choices else extra_choices
        for label, default, values in selectors:
            choice_label = window.Label(label=label)
            choice_label.configure(wraplength=0)
            choice_label.pack(fill="x", padx=12, pady=(8, 2))
            selections[label] = form_choice(window, default, values)

        def accept():
            nonlocal result
            result = {label: field.value.strip() for label, field in inputs.items()}
            result.update((label, get_value()) for label, get_value in selections.items())
            window.close()

        row = window.Frame()
        row.pack(fill="x", padx=10, pady=12)
        row.Input.Button(label=tr("適用"), command=accept).pack(side="right", padx=2)
        row.Input.Button(label=tr("キャンセル"), command=window.close).pack(side="right", padx=2)
        try:
            window.wait()
        finally:
            if parent is not self.api.ui and parent.backend == "tkinter" and parent.exist():
                parent.root.grab_set()
        return result

    @property
    def title(self):
        return next((title for title in self.project["titles"] if title["id"] == self.titles.selected), None)

    @property
    def chapter(self):
        title = self.title
        if title:
            selected = self.chapters.selected if self.chapters else self.chapter_id
            return next((chapter for chapter in title["chapters"] if chapter["id"] == selected), None)
        return None

    def link_label(self, link):
        if isinstance(link, dict) and link.get("play_all") is True:
            return tr("すべて再生")
        page = target_page(link)
        if page is not None and 0 <= page < page_count(self.project["menu"]):
            return tr("メニューページ {0}", page + 1)
        for number, title in enumerate(self.project["titles"], 1):
            prefix = f"{number}. {title['name']}"
            if link == {"title": title["id"]}:
                return tr("{0}（タイトル先頭）", prefix)
            if isinstance(link, dict) and link.get("title") == title["id"] and "audio" in link:
                return tr("{0}（音声・字幕設定）", prefix)
            for chapter in title["chapters"]:
                if link == {"title": title["id"], "chapter": chapter["id"]}:
                    return f"{prefix} / {chapter['name']} ({chapter['time']})"
        return tr(UNLINKED)

    def refresh(self, title_id=None, chapter_id=None, menu_selection=None):
        self.api.saved = self.load_error is not None or self.project == self.saved_project
        if self.history_menu is not None:
            self.history_menu.refresh()
        for button, entries in zip(self.history_buttons, (self.history.past, self.history.future)):
            button.configure(state="normal" if entries else "disabled")
        self.titles.replace(
            [(title["id"], f"{tr(MEDIA_LABELS[media_kind(title)])}  ·  {title['name']}")
             for title in self.project["titles"]], title_id or self.titles.selected)
        self.title_selected(chapter_id, force=True)
        if self.menu_layout is not None:
            self.menu_layout.refresh(self.project["menu"], menu_selection)

    def title_selected(self, chapter_id=None, force=False):
        title = self.title
        title_id = title["id"] if title else None
        self.edit_video_button.configure(state="normal" if title and is_video_project(title) else "disabled")
        if not force and title_id == self.active_title:
            return
        if title_id != self.active_title:
            self.stop_preview()
            self.duration = None
            self.chapter_id = None
            if title and media_kind(title) != "image":
                if not is_video_project(title):
                    self.duration = title.get("duration_ms")
                    if self.duration is None and os.path.isfile(title["media"]):
                        self.duration = media_duration(title["media"])
        if title and is_video_project(title):
            try:
                self.duration = timeline_duration(title)
                self.position = min(self.position, max(0, self.duration - 1))
            except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
                self.duration = None
                self.report(str(exc))
        self.active_title = title_id
        if chapter_id:
            self.chapter_id = chapter_id
        self.refresh_chapters()
        self.source_label.configure(label=os.path.basename(title["media"]) if title else tr("素材を追加してください"))
        self.update_time()

    def edit_video_project(self):
        title = self.title
        if not title or not is_video_project(title):
            return
        path = os.path.abspath(title["media"])
        if not os.path.isfile(path):
            self.report(tr("素材ファイルが見つかりません。 {0}", path))
            return
        host = getattr(self.api, "app", None)
        notebook = getattr(getattr(host, "ui", None), "notebook", None)
        if notebook is None or not callable(getattr(host, "open", None)):
            self.report(tr("この環境では Video の編集タブを開けません。"))
            return
        self.stop_preview()
        for tab in notebook.list_tab():
            context = getattr(tab, "addon", None)
            opened_path = getattr(context, "filepath", None)
            if (opened_path and getattr(context, "ext", "").lower() == "maruvideo"
                    and os.path.normcase(os.path.realpath(opened_path)) == os.path.normcase(os.path.realpath(path))):
                notebook.select_tab(tab)
                return
        extensions = getattr(getattr(host, "addon", None), "extdict", {})
        if Path(path).suffix[1:] not in extensions:
            self.report(tr("この素材を使うには Video アドオンもインストールしてください。"))
            return
        host.open(file=path)

    def return_to_disc(self, event=None):
        notebook = self.api.app.ui.notebook
        selected = notebook.widget.select()
        if any(tab.id == selected and getattr(tab, "addon", None) is self.api for tab in notebook.list_tab()):
            if self.title and is_video_project(self.title):
                self.title_selected(force=True)

    def refresh_chapters(self):
        if self.chapters is None:
            return
        title = self.title
        self.chapters.replace(
            [(chapter["id"], f"{chapter['time']}   {chapter['name']}") for chapter in title["chapters"]]
            if title else [], self.chapter_id or self.chapters.selected)
        self.chapter_id = self.chapters.selected

    def show_chapters(self):
        if not self.title or media_kind(self.title) == "image":
            return self.report(tr("動画か音声を選択してください。"))
        window = self.api.ui.makeSubWindow(dialog=True)
        window.changeTitle(tr("チャプター一覧"))
        self.chapter_window = window
        self.chapters = SelectionList(window, 8, 340)
        self.refresh_chapters()
        self.buttons(window, (tr("追加"), self.add_chapter), (tr("編集"), self.edit_chapter),
                     (tr("削除"), self.delete_chapter), (tr("移動"), self.seek), (tr("閉じる"), window.close))
        try:
            window.wait()
        finally:
            self.chapter_id = self.chapters.selected
            self.chapters = None
            self.chapter_window = None

    def set_position(self, milliseconds):
        self.position = milliseconds
        self.update_time(update_slider=False)

    def follow_playback(self, milliseconds):
        if self.seek_bar.dragging:
            return
        if self.duration:
            milliseconds = min(milliseconds, self.duration - 1)
        if self.position != milliseconds:
            self.position = milliseconds
            self.update_time()

    def seek_from_bar(self):
        if self.duration:
            self.play_at(self.position, seek=True)

    def update_time(self, update_slider=True):
        total = format_time(self.duration) if self.duration else "—"
        self.time_label.configure(label=f"{format_time(self.position)} / {total}")
        if update_slider:
            self.seek_bar.update(self.position, self.duration)

    def edit_allowed(self):
        if self.load_error:
            self.report(tr("プロジェクトを開けなかったため、編集と保存を利用できません。"))
            return False
        return True

    def changed(self, message, **selection):
        self.refresh(**selection)
        self.report(message)

    def add_asset(self):
        if not self.edit_allowed():
            return
        paths = self.dialog.askfile(multi=True, title=tr("素材を選択"), filetypes=[
            (tr("画像・音声・動画"), file_pattern(IMAGE_TYPES + AUDIO_TYPES + VIDEO_TYPES)),
            (tr("すべてのファイル"), "*"),
        ])
        if paths:
            self.add_assets(paths)

    def add_assets(self, paths):
        if not self.edit_allowed():
            return False
        if isinstance(paths, (str, os.PathLike)):
            paths = (paths,)
        titles = []
        skipped = 0
        failures = []
        for path in paths:
            if not path:
                continue
            if not os.path.isfile(path):
                skipped += 1
                continue
            kind = path_kind(path)
            chapters = [] if kind == "image" else [make_chapter(tr("チャプター 1"), 0)]
            title = make_title(Path(path).stem, os.path.abspath(path), chapters)
            title["kind"] = kind
            if is_video_project(title):
                try:
                    timeline_duration(title)
                except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
                    failures.append(f"{path}\n{exc}")
                    continue
            titles.append(title)
        if not titles:
            self.report(tr("Video プロジェクトを読み込めません。 {0}\n{1}", "", failures[0]) if failures
                        else tr("選択した素材が見つかりません。"))
            return False
        self.history.record(self.project)
        self.project["titles"].extend(titles)
        message = tr("素材を {0} 件追加しました。", len(titles))
        if skipped:
            message += " " + tr("見つからないファイルやフォルダを {0} 件スキップしました。", skipped)
        self.changed(message, title_id=titles[-1]["id"])
        if failures:
            self.dialog.warn(title=tr("素材を選択"), message="\n\n".join(failures))
        return True

    def import_bdmv(self):
        if not self.edit_allowed():
            return
        path = self.dialog.askdir(title=tr("BDMV フォルダか、その親フォルダを選択"))
        if not path:
            return
        try:
            incoming = bdmv.import_as_project(path)
        except (OSError, ValueError) as exc:
            self.report(str(exc))
            return
        titles = incoming["titles"]
        inventory = incoming["bdmv_inventory"]
        if not titles:
            self.dialog.warn(title="BDMV", message=tr("取り込めるタイトルがありません。\n")
                             + "\n".join(inventory["warnings"]))
            return
        self.history.record(self.project)
        if not self.project.get("source_bdmv"):
            self.project["source_bdmv"] = incoming["source_bdmv"]
            self.project["bdmv_inventory"] = inventory
        else:
            self.project.setdefault("bdmv_imports", []).append(inventory)
        self.project["titles"].extend(titles)
        self.changed(tr("BDMV から {0} 件のタイトルを追加しました。 警告 {1} 件", len(titles), len(inventory['warnings'])), title_id=titles[0]["id"])

    def rename_title(self):
        title = self.title
        if not title:
            return self.report(tr("タイトルを選択してください。"))
        result = self.form(tr("タイトル名"), [(tr("名前"), title["name"])])
        if result and result[tr("名前")] and result[tr("名前")] != title["name"]:
            self.history.record(self.project)
            title["name"] = result[tr("名前")]
            self.changed(tr("タイトル名を変更しました。"))

    def delete_title(self):
        title = self.title
        if not title:
            return self.report(tr("タイトルを選択してください。"))
        if not self.dialog.question("yesno", tr("タイトルの削除"), tr("「{0}」をプロジェクトから削除しますか？", title['name'])):
            return
        titles = self.project["titles"]
        index = titles.index(title)
        self.history.record(self.project)
        titles.remove(title)
        self.clear_links(title["id"])
        next_id = titles[min(index, len(titles) - 1)]["id"] if titles else None
        self.changed(tr("タイトルを削除しました。"), title_id=next_id)

    def move_title(self, step):
        title = self.title
        if not title:
            return self.report(tr("タイトルを選択してください。"))
        titles = self.project["titles"]
        index = titles.index(title)
        if 0 <= index + step < len(titles):
            self.history.record(self.project)
            titles.insert(index + step, titles.pop(index))
            self.changed(tr("タイトルを並べ替えました。"))

    def add_chapter(self):
        self.change_chapter(None)

    def edit_chapter(self):
        if not self.chapter:
            return self.report(tr("チャプターを選択してください。"))
        self.change_chapter(self.chapter)

    def change_chapter(self, chapter):
        title = self.title
        if not title or media_kind(title) == "image":
            return self.report(tr("動画か音声を選択してください。"))
        chapters = title["chapters"]
        name = chapter["name"] if chapter else tr("チャプター {0}", len(chapters) + 1)
        time = chapter["time"] if chapter else format_time(self.position)
        values = self.form(tr("チャプター"), [(tr("名前"), name), (tr("時刻 (HH:MM:SS.mmm)"), time)])
        if not values:
            return
        try:
            milliseconds = parse_time(values[tr("時刻 (HH:MM:SS.mmm)")])
            if not values[tr("名前")]:
                raise ValueError(tr("チャプター名を入力してください。"))
            if self.duration is not None and milliseconds >= self.duration:
                raise ValueError(tr("タイトルの終了時刻より前の時刻を指定してください。"))
        except ValueError as exc:
            self.report(str(exc))
            return
        name, time = values[tr("名前")], format_time(milliseconds)
        if chapter and (chapter["name"], chapter["time"]) == (name, time):
            return
        self.history.record(self.project)
        if chapter:
            chapter.update(name=name, time=time)
        else:
            chapter = make_chapter(name, milliseconds)
            chapters.append(chapter)
        chapters.sort(key=self.chapter_order)
        self.changed(tr("チャプターを更新しました。"), chapter_id=chapter["id"])

    @staticmethod
    def chapter_order(chapter):
        try:
            return parse_time(chapter["time"])
        except ValueError:
            # The v0.4 editor accepted out-of-range minute/second fields.
            return float("inf")

    def delete_chapter(self):
        title, chapter = self.title, self.chapter
        if not chapter:
            return self.report(tr("チャプターを選択してください。"))
        self.history.record(self.project)
        title["chapters"].remove(chapter)
        self.clear_links(title["id"], chapter["id"])
        self.changed(tr("チャプターを削除しました。"))

    def clear_links(self, title_id, chapter_id=None):
        for button in self.project["menu"]["buttons"] + self.project["menu"]["elements"]:
            target = button.get("target")
            if isinstance(target, dict) and target.get("title") == title_id:
                if chapter_id is None or target.get("chapter") == chapter_id:
                    button["target"] = None

    def update_menu_layout(self, menu, selected=None):
        if self.edit_allowed() and menu != self.project["menu"]:
            self.history.record(self.project)
            self.project["menu"] = menu
            self.changed(tr("メニューの配置を更新しました。"), menu_selection=selected)

    def edit_remote_navigation(self, menu, page, selected_tag):
        items = [item for item in page_buttons(menu, page)
                 if item.next_page is not None or self.link_label(item.target) != tr(UNLINKED)]
        if not items:
            self.dialog.info(title=tr("リモコン操作"), message=tr("リンク付きの項目を配置してください。"))
            return
        automatic = tr("自動")
        labels = {automatic: None}
        for number, item in enumerate(items, 1):
            labels[f"{number}. {item.caption}"] = item

        def choice(name, preferred):
            current = next((label for label, item in labels.items() if item and item.key == preferred), automatic)
            return name, current, list(labels)

        page_key = str(page)
        first = tr("初期選択")
        selectors = [choice(first, menu.get("initial_focus", {}).get(page_key))]
        item = next((item for item in items if item.tag == selected_tag), None)
        directions = {"up": tr("上"), "down": tr("下"), "left": tr("左"), "right": tr("右")}
        if item:
            current_moves = item.entry.get("navigation", {}).get(page_key, {})
            selectors.extend(choice(label, current_moves.get(direction))
                             for direction, label in directions.items())
        note = (tr("{0}ページ目 · 「{1}」からの移動", page + 1, item.caption) if item
                else tr("上下左右の移動先を変更するには、リンク付きの項目を選んでください。"))
        values = self.form(tr("リモコン操作"), [], extra_choices=selectors, note=note)
        if not values:
            return

        def key_for(target):
            if target.next_page is not None:
                return target.key
            if not target.entry.get("id"):
                target.entry["id"] = uuid4().hex
            return target.entry["id"]

        preferred = labels[values[first]]
        if preferred:
            menu.setdefault("initial_focus", {})[page_key] = key_for(preferred)
        elif "initial_focus" in menu:
            menu["initial_focus"].pop(page_key, None)
        if item:
            moves = {}
            for direction, label in directions.items():
                target = labels[values[label]]
                if target:
                    moves[direction] = key_for(target)
            if moves:
                item.entry.setdefault("navigation", {})[page_key] = moves
            elif "navigation" in item.entry:
                item.entry["navigation"].pop(page_key, None)

    def edit_menu(self):
        if not self.edit_allowed():
            return
        menu = self.project["menu"]
        backgrounds, default = self.menu_image_choices(menu["background"], empty=tr("背景なし"))
        videos = {tr("動画 {0}. {1}", index, title["name"]): title["media"]
                  for index, title in enumerate(self.project["titles"], 1)
                  if media_kind(title) == "video" and not is_video_project(title)}
        motion = menu.get("motion", "")
        music = menu.get("music", "")
        if motion:
            default = next((label for label, path in videos.items() if path == motion),
                           tr("動画 · {0}", Path(motion).name))
            videos.setdefault(default, motion)
        backgrounds.update(videos)
        sounds = {tr("BGM なし"): ""}
        for index, title in enumerate(self.project["titles"], 1):
            if media_kind(title) == "audio":
                sounds[f"{index}. {title['name']}"] = title["media"]
        if music and music not in sounds.values():
            sounds[tr("設定済み BGM · {0}", Path(music).name)] = music
        audio_default = next(label for label, path in sounds.items() if path == music)
        values = self.form(tr("メニュー背景と BGM"), [], extra_choices=(
            (tr("背景"), default, list(backgrounds)), ("BGM", audio_default, list(sounds)),
        ), note=tr("素材一覧に登録した画像・動画・音声を使えます。背景動画の音声は BGM 欄で設定します。"))
        if not values:
            return
        background = backgrounds[values[tr("背景")]]
        if values[tr("背景")] in videos:
            background, motion = "", background
        else:
            motion = ""
        music = sounds[values["BGM"]]
        try:
            background, motion, music = (self.menu_media_path(path) for path in (background, motion, music))
        except ValueError as exc:
            return self.report(str(exc))
        updated = {**menu, "background": background}
        for key, path in (("motion", motion), ("music", music)):
            if path:
                updated[key] = path
            else:
                updated.pop(key, None)
        self.update_menu_layout(updated)

    def edit_playback_end(self):
        title = self.title
        if not self.edit_allowed():
            return
        if not title:
            return self.report(tr("タイトルを選択してください。"))
        label = tr("再生後の動作")
        return_to_menu = tr("メニューに戻る")
        play_next = tr("次のタイトルを再生")
        was_play_next = title.get("playback_end") == "next"
        default = play_next if was_play_next else return_to_menu
        result = self.form(tr("再生後の動作 · {0}", title["name"]), [],
                           choices=(label, default, (return_to_menu, play_next)),
                           note=tr("次のタイトルは素材一覧の順番で決まります。最後のタイトルの後はメニューに戻ります。"))
        if not result:
            return
        should_play_next = result[label] == play_next
        if should_play_next != was_play_next:
            self.history.record(self.project)
            if should_play_next:
                title["playback_end"] = "next"
            else:
                title.pop("playback_end", None)
            self.changed(tr("再生後の動作を更新しました。"), title_id=title["id"])

    def edit_disc_tracks(self):
        title = self.title
        if not self.edit_allowed() or not title:
            return
        audio = copy.deepcopy(title.get("audio_tracks", []))
        subtitles = copy.deepcopy(title.get("subtitle_tracks", []))
        window = self.api.ui.makeSubWindow(dialog=True)
        window.changeTitle(tr("ディスクのトラック · {0}", title['name']))
        self.label(window, tr("素材に含まれる音声を収録します。ここでは外部音声と字幕を追加できます。"))
        rows = SelectionList(window, 7, 335)
        dvd = self.disc_kind == "dvd"
        popup = None
        if not dvd:
            popup_default = bool(title.get("popup_menu"))
            popup = window.Input.CheckButton(label=tr("再生中のポップアップメニューを付ける"), default=popup_default)
            popup.pack(anchor="w", padx=8, pady=3)
            self.label(window, tr("ポップアップではチャプター、音声・字幕を切り替えられます。"))

        def redraw(selected=None):
            rows.replace([(f"{kind}:{i}", f"{name} · {track['language']} · {Path(track['path']).name}")
                          for kind, name, tracks in (("audio", tr("音声"), audio), ("subtitle", tr("字幕"), subtitles))
                          for i, track in enumerate(tracks)], selected)

        def configure_track(kind, index=None):
            is_audio = kind == "audio"
            tracks = audio if is_audio else subtitles
            caption = tr("追加音声") if is_audio else tr("字幕")
            allowed = (".srt",) if dvd else (".srt", ".sup")
            extensions = file_pattern(AUDIO_TYPES if is_audio else allowed)
            path = (tracks[index]["path"] if index is not None else
                    window.Dialog.askfile(title=tr("{0}ファイルを選択", caption), filetypes=[(caption, extensions)]))
            if not path:
                return
            if not is_audio and Path(path).suffix.lower() not in allowed:
                message = tr("UTF-8 の SRT を選んでください。") if dvd else tr("UTF-8 の SRT または PGS の SUP を選んでください。")
                window.Dialog.error(title=caption, message=message)
                return
            language = window.Dialog.question("text", caption, tr("言語コード（例: jpn、eng、und）"),
                                              initialvalue=tracks[index]["language"] if index is not None else "und")
            if language is None:
                return
            language = language.strip().lower()
            if not LANGUAGE.fullmatch(language):
                window.Dialog.error(title=caption, message=tr("言語コードは半角英小文字3文字で入力してください。"))
                return
            track = {"path": os.path.abspath(path), "language": language}
            if index is None:
                index = len(tracks)
                tracks.append(track)
            else:
                tracks[index] = track
            redraw(f"{kind}:{index}")

        def selected_track():
            if rows.selected:
                kind, index = rows.selected.split(":")
                return kind, int(index)
            return None, None

        def edit():
            kind, index = selected_track()
            if kind:
                configure_track(kind, index)

        def remove():
            kind, index = selected_track()
            if kind:
                (audio if kind == "audio" else subtitles).pop(index)
                redraw()

        def apply():
            updated = dict(title)
            values = {"audio_tracks": audio, "subtitle_tracks": subtitles}
            if popup is not None:
                values["popup_menu"] = popup_default if popup.value == "" else bool(popup.value)
            for key, value in values.items():
                if value:
                    updated[key] = value
                else:
                    updated.pop(key, None)
            window.close()
            if updated != title:
                self.history.record(self.project)
                title.clear()
                title.update(updated)
                self.changed(tr("ディスクのトラック設定を更新しました。"))

        self.buttons(window, (tr("音声を追加…"), lambda: configure_track("audio")),
                     (tr("字幕を追加…"), lambda: configure_track("subtitle")), (tr("言語を変更"), edit), (tr("削除"), remove))
        self.buttons(window, (tr("適用"), apply), (tr("キャンセル"), window.close))
        redraw()
        window.wait()

    def menu_links(self, menu, current=None):
        links = {tr(UNLINKED): None, tr("すべて再生"): {"play_all": True}}
        if isinstance(current, dict) and "audio" in current:
            label = self.link_label(current)
            if label != tr(UNLINKED):
                links[label] = current
        links.update((tr("メニューページ {0}", page + 1), {"page": page})
                     for page in range(page_count(menu)))
        for number, title in enumerate(self.project["titles"], 1):
            prefix = f"{number}. {title['name']}"
            links[tr("{0}（タイトル先頭）", prefix)] = {"title": title["id"]}
            for chapter_no, chapter in enumerate(title["chapters"], 1):
                links[f"{prefix} / {chapter_no}. {chapter['name']} ({chapter['time']})"] = {
                    "title": title["id"], "chapter": chapter["id"],
                }
        return links

    def menu_media_path(self, value):
        if not value:
            return ""
        path = os.path.abspath(os.path.join(os.path.dirname(self.api.filepath or ""), value))
        if not os.path.isfile(path):
            raise ValueError(tr("素材ファイルが見つかりません。 {0}", path))
        return path

    def menu_image_choices(self, current="", *, empty=None, embedded=False):
        images = {empty: ""} if empty else {}
        for index, title in enumerate(self.project["titles"], 1):
            if media_kind(title) == "image":
                images[f"{index}. {title['name']}"] = title["media"]
        if embedded:
            images[tr("現在の動画サムネイル")] = None
            return images, tr("現在の動画サムネイル")
        if current and current not in images.values():
            images[tr("設定済み画像 · {0}", Path(current).name)] = current
        default = next((label for label, path in images.items() if path == current), next(iter(images), ""))
        return images, default

    def change_menu_element(self, kind, index=None, *, draft, page=0):
        if not self.edit_allowed():
            return
        elements = draft["elements"]
        existing = elements[index] if index is not None else {}
        all_pages = tr("全ページ")
        page_field = tr("表示ページ")
        pages = {all_pages: None}
        pages.update((tr("ページ {0}", number + 1), number) for number in range(page_count(draft)))
        default_page = page if index is None else existing.get("page")
        current_page = next((label for label, value in pages.items() if value == default_page), all_pages)
        page_choice = (page_field, current_page, list(pages))
        dialog = self.dialog
        title_label = tr(SHOW_VIDEO_TITLE)
        title_options = tuple(map(tr, VIDEO_TITLE_OPTIONS))
        if kind == "thumbnail":
            videos = {f"{i}. {title['name']}": title for i, title in enumerate(self.project["titles"], 1)
                      if media_kind(title) == "video"}
            if not videos:
                dialog.error(title=tr("動画サムネイル"), message=tr("先に動画素材を追加してください。"))
                return
            default = next((label for label, title in videos.items() if title is self.title), next(iter(videos)))
            initial_time = self.position if videos[default] is self.title else 0
            values = self.form(tr("動画サムネイル"), [(tr("時刻 (HH:MM:SS.mmm)"), format_time(initial_time))],
                               extra_choices=((tr("動画素材"), default, list(videos)),
                                              (title_label, title_options[0], title_options), page_choice))
            if not values:
                return
            source = videos[values[tr("動画素材")]]
            try:
                stamp = parse_time(values[tr("時刻 (HH:MM:SS.mmm)")])
                image = capture_thumbnail(source, stamp)
            except (ValueError, OSError, ImportError) as exc:
                dialog.error(title=tr("動画サムネイル"), message=str(exc))
                return
            updated = {"kind": "image", "thumbnail": image,
                       "thumbnail_name": f"{source['name']} · {format_time(stamp)}",
                       "thumbnail_source": source["id"],
                       "show_video_title": values[title_label] == title_options[1],
                       "target": {"title": source["id"]}}
        else:
            links = self.menu_links(draft, existing.get("target"))
            default = next((label for label, target in links.items() if existing.get("target") == target), tr(UNLINKED))
            caption = tr(OBJECT_LABELS[kind])
            key = {"shape": "shape", "image": "image", "text": "text"}[kind]
            current = existing.get(key, "")
            if kind == "shape":
                current = object_caption(existing) if existing else tr("長方形")
            embedded = kind == "image" and bool(existing.get("thumbnail"))
            fields = [(caption, current)] if kind == "text" else []
            shapes = {tr(label): shape for label, shape in SHAPES.items()}
            extra = ((tr("図形の種類"), current, list(shapes)),) if kind == "shape" else ()
            if kind == "image":
                images, selected = self.menu_image_choices(current, embedded=embedded)
                if not images:
                    dialog.info(title=tr("画像素材"), message=tr("先に「素材を追加」で画像を登録してください。"))
                    return
                extra = ((tr("画像素材"), selected, list(images)),)
                if embedded:
                    current_title = title_options[bool(existing.get("show_video_title"))]
                    extra += ((title_label, current_title, title_options),)
            colors = ()
            if kind == "shape":
                colors = (tr("塗り色"), tr("線の色"))
                fields.extend([(colors[0], existing.get("fill", "")), (colors[1], existing.get("outline", ""))])
            elif kind == "text":
                colors = (tr("文字色"), tr("背景色"))
                fields.extend([(tr("フォントファイル"), existing.get("font_file", "")),
                               (tr("文字サイズ (px)"), str(existing.get("font_size", 12))),
                               (colors[0], existing.get("foreground", "")), (colors[1], existing.get("fill", ""))])
            values = self.form(caption, fields, choices=(tr("リンク先"), default, list(links)),
                               extra_choices=(*extra, page_choice), color_fields=colors,
                               font_field=tr("フォントファイル") if kind == "text" else None)
            if not values:
                return
            updated = {**existing, "kind": kind, "target": links[values[tr("リンク先")]]}
            if kind != "image" or images[values[tr("画像素材")]] is not None:
                try:
                    if kind == "image":
                        image = images[values[tr("画像素材")]]
                        value = current if image == current else self.menu_media_path(image)
                        updated.pop("thumbnail", None)
                        updated.pop("thumbnail_name", None)
                        updated.pop("thumbnail_source", None)
                        updated.pop("show_video_title", None)
                    elif kind == "shape":
                        value = shapes[values[tr("図形の種類")]]
                    else:
                        value = values[caption]
                    if not value:
                        raise ValueError(tr("{0}を指定してください。", caption))
                except ValueError as exc:
                    dialog.error(title=caption, message=str(exc))
                    return
                updated[key] = value
            elif embedded:
                if values[title_label] == title_options[1]:
                    updated["show_video_title"] = True
                elif "show_video_title" in updated:
                    updated["show_video_title"] = False
            try:
                for field, style in zip(colors, ("fill", "outline") if kind == "shape" else ("foreground", "fill")):
                    color = values[field]
                    if color and not valid_color(color):
                        raise ValueError(tr("{0}は #RRGGBB 形式で指定してください。", field))
                    if color:
                        updated[style] = color
                    else:
                        updated.pop(style, None)
                if kind == "text":
                    size = values[tr("文字サイズ (px)")]
                    if not size.isdecimal() or not 6 <= int(size) <= 120:
                        raise ValueError(tr("文字サイズは 6〜120 px で指定してください。"))
                    updated["font_size"] = int(size)
                    font = values[tr("フォントファイル")]
                    if font:
                        font = os.path.abspath(os.path.join(os.path.dirname(self.api.filepath or ""), font))
                        menu_font(int(size), font)
                        updated["font_file"] = font
                    else:
                        updated.pop("font_file", None)
            except (ValueError, OSError, ImportError) as exc:
                dialog.error(title=caption, message=str(exc))
                return
        placed_page = pages[values[page_field]]
        if placed_page is None:
            updated.pop("page", None)
        else:
            updated["page"] = placed_page
        if updated == existing:
            return index
        if index is None:
            index = len(elements)
            elements.append(updated)
        else:
            elements[index] = updated
        return index

    def change_button(self, index, *, draft):
        buttons = draft["buttons"]
        existing = buttons[index] if index is not None else {}
        image_path = existing.get("image", "")
        links = self.menu_links(draft, existing.get("target"))
        default = next((label for label, target in links.items() if existing.get("target") == target), tr(UNLINKED))
        name = existing.get("label", existing.get("name", Path(image_path).stem or tr("ボタン {0}", len(buttons) + 1)))
        images, selected = self.menu_image_choices(image_path, empty=tr("画像なし"))
        values = self.form(tr("メニューボタン"), [(tr("表示名"), name)],
                           extra_choices=((tr("サムネイル画像"), selected, list(images)),),
                           choices=(tr("リンク先"), default, list(links)))
        if not values:
            return
        if not values[tr("表示名")]:
            return self.report(tr("ボタンの表示名を入力してください。"))
        target = links[values[tr("リンク先")]]
        try:
            image = images[values[tr("サムネイル画像")]]
            if image != image_path:
                image = self.menu_media_path(image)
        except ValueError as exc:
            self.dialog.error(title=tr("サムネイル画像"), message=str(exc))
            return None
        if image and image != image_path:
            try:
                from PIL import Image
            except ImportError:
                self.dialog.error(title=tr("サムネイル画像"), message=tr("Pillow が必要です。"))
                return None
            try:
                with Image.open(image) as picture:
                    picture.verify()
            except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
                self.dialog.error(title=tr("サムネイル画像"), message=tr("画像を読み込めません。 {0}", exc))
                return None
        if (existing.get("label"), existing.get("target"), existing.get("image", "")) == (values[tr("表示名")], target, image):
            return
        if index is None:
            index = len(buttons)
            buttons.append({})
        buttons[index].update(label=values[tr("表示名")], target=target)
        if image:
            buttons[index]["image"] = image
        else:
            buttons[index].pop("image", None)
        return index

    def undo(self):
        if self.history.past:
            self.project = self.history.undo(self.project)
            self.changed(tr("元に戻しました。"))

    def redo(self):
        if self.history.future:
            self.project = self.history.redo(self.project)
            self.changed(tr("やり直しました。"))

    def inventories(self):
        initial = self.project.get("bdmv_inventory")
        return ([initial] if initial else []) + self.project.get("bdmv_imports", [])

    def properties(self):
        if not self.edit_allowed():
            return
        title = self.title
        info = [tr("保存先　{0}", self.api.filepath or tr("未保存"))]
        if title:
            info.append(tr("タイトル　{0}\n素材　{1}", title['name'], title['media']))
            if title.get("segments"):
                info.append(tr("再生区間　{0} 件 / {1}", len(title['segments']), format_time(title['duration_ms'])))
        for inventory in self.inventories():
            info.append(f"BDMV　{inventory['root']}")
            warnings = inventory.get("warnings", [])
            info.extend(warnings[:5])
            if len(warnings) > 5:
                info.append(tr("ほか {0} 件の警告", len(warnings) - 5))
        values = self.form(tr("詳細設定"), [(tr("プロジェクト名"), self.project["name"])], note="\n".join(info))
        if values and values[tr("プロジェクト名")] and values[tr("プロジェクト名")] != self.project["name"]:
            self.history.record(self.project)
            self.project["name"] = values[tr("プロジェクト名")]
            self.changed(tr("プロジェクト名を変更しました。"))

    def validate(self):
        if not self.edit_allowed():
            return
        if self.disc_kind == "dvd":
            from .dvd_export import check_dvd_project

            errors, warnings = check_dvd_project(self.project)
        else:
            errors, warnings = check_project(self.project)
        if errors or warnings:
            self.report(tr("書き出し前チェック　エラー {0} 件・警告 {1} 件", len(errors), len(warnings)))
            details = []
            if errors:
                details.append(tr("エラー\n") + issue_message(errors))
            if warnings:
                details.append(tr("警告\n") + issue_message(warnings))
            self.dialog.warn(title=tr("書き出し前チェック"), message="\n\n".join(details))
        else:
            self.report(tr("書き出し前チェックに問題はありません。"))

    def export_disc(self):
        if not self.edit_allowed():
            return
        if not self.project["titles"]:
            return self.report(tr("書き出す素材を追加してください。"))
        show_export_dialog(self.api.ui, self.project, self.api.filepath, self.stop, self.report,
                           dvd=self.disc_kind == "dvd")

    def audio_settings(self):
        host = getattr(self.api, "app", None)
        settings = getattr(host, "_bluray_audio_settings", None)
        if settings is None:
            settings = self.audio_preferences
        if settings is None:
            settings = {"audio_output": None}
            if getattr(self.api, "appinfo", {}).get("conf"):
                from libmarusoftware import Config

                settings = Config(appname="Blu-ray", module="preview",
                                  default_conf=settings, addon=dict(self.api.appinfo))
            self.audio_preferences = settings
            if host is not None:
                host._bluray_audio_settings = settings
        return settings

    def configure_audio(self):
        try:
            outputs = self.preview.audio_outputs()
            settings = self.audio_settings()
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            return self.report(tr("音声出力の設定を開けませんでした。 {0}", exc))
        choices = {tr("システム既定"): None, tr("ミュート"): "mute", **outputs}
        current = settings["audio_output"]
        default = next((label for label, device in choices.items() if device == current), tr("システム既定"))
        caption = tr("DVD プレビューの音声出力") if self.disc_kind == "dvd" else tr("Blu-ray プレビューの音声出力")
        values = self.form(caption, [],
                           choices=(tr("出力先"), default, list(choices)),
                           note=tr("変更は次回の再生から適用されます。"))
        if values:
            try:
                settings.update(audio_output=choices[values[tr("出力先")]])
            except OSError as exc:
                return self.report(tr("音声出力設定を保存できませんでした。 {0}", exc))
            self.report(tr("次回のプレビューの音声出力: {0}", values[tr("出力先")]))

    def play_at(self, milliseconds, *, seek=False):
        if not self.title:
            return self.report(tr("素材を選択してください。"))
        try:
            title = self.title
            if is_video_project(title):
                from addons.video.jobs import render_with_progress
                from .export_cache import clip_key
                from uuid import uuid4

                timeline = load_timeline(title)
                self.duration = timeline_duration({**title, "_timeline": timeline})
                key = clip_key({**title, "_timeline": timeline}, [], "preview-360")
                proxy = self.video_proxies.get(title["id"])
                if proxy is None or proxy[0] != key:
                    if self.video_workspace is None:
                        self.video_workspace = TemporaryDirectory(prefix="marubd-video-preview-", ignore_cleanup_errors=True)
                    self.stop_preview()
                    path = Path(self.video_workspace.name) / (uuid4().hex + ".mp4")
                    host = getattr(getattr(self.api, "app", None), "ui", None) or self.api.ui
                    captions = {"Preparing Timeline Preview…": tr("タイムラインのプレビューを準備中…"),
                                "Cancel": tr("中止"), "Cancelling…": tr("中止処理中…")}
                    translate = lambda message: captions.get(message, message)
                    if not render_with_progress(host, translate, timeline, path, size=(640, 360), proxy=True):
                        return
                    self.video_proxies[title["id"]] = (key, path)
                    seek = False
                title = {**title, "media": str(self.video_proxies[title["id"]][1])}
            self.preview.play(title, milliseconds, self.audio_settings()["audio_output"], seek=seek)
        except Exception as exc:
            self.report(tr("プレビュー: {0}", exc))
            return
        self.position = milliseconds
        self.update_time()
        self.report(tr("画像を表示しました。") if media_kind(self.title) == "image" else tr("プレビューを読み込んでいます。"))

    def play(self):
        self.play_at(self.position)

    def pause(self):
        try:
            self.preview.pause_resume()
        except Exception as exc:
            self.report(tr("プレビュー: {0}", exc))

    def seek(self):
        if not self.chapter:
            return self.report(tr("チャプターを選択してください。"))
        try:
            milliseconds = parse_time(self.chapter["time"])
        except ValueError as exc:
            return self.report(str(exc))
        self.play_at(milliseconds, seek=True)
        if self.chapter_window:
            self.chapter_window.close()

    def stop_preview(self):
        try:
            self.preview.close()
        except Exception as exc:
            self.report(tr("プレビュー: {0}", exc))
        self.position = 0

    def stop(self):
        self.stop_preview()
        self.update_time()

    def choose_save_path(self, kind=None):
        if not self.edit_allowed():
            return
        kind = kind or self.disc_kind
        extension = PROJECT_EXTENSIONS[kind]
        description = tr("DVD プロジェクト") if kind == "dvd" else tr("Blu-ray プロジェクト")
        options = {}
        if kind != self.disc_kind and self.api.filepath:
            source = Path(self.api.filepath)
            options = {"initialdir": str(source.parent), "initialfile": source.stem + extension}
        return self.dialog.askfile(save=True, title=tr("プロジェクトを保存"), defaultextension=extension,
                                   filetypes=[(description, "*" + extension)], **options)

    def save_converted_copy(self):
        kind = "bluray" if self.disc_kind == "dvd" else "dvd"
        path = self.choose_save_path(kind)
        if not path:
            return
        extension = PROJECT_EXTENSIONS[kind]
        destination = Path(path)
        if not destination.suffix:
            destination = destination.with_suffix(extension)
        try:
            if destination.suffix.lower() != extension:
                raise ValueError(tr("保存先の拡張子に {0} を指定してください。", extension))
            if self.api.filepath and destination.resolve() == Path(self.api.filepath).resolve():
                raise ValueError(tr("変換先に別のファイルを指定してください。"))
            save_project(destination, convert_project(self.project, kind))
        except (OSError, ValueError) as exc:
            self.dialog.error(title=tr("プロジェクトを保存"), message=str(exc))
            return
        self.report(tr("変換したプロジェクトを保存しました。 {0}", destination))
        if kind == "dvd" and any(
            Path(track["path"]).suffix.lower() != ".srt"
            for title in self.project["titles"] for track in title.get("subtitle_tracks", [])
        ):
            self.dialog.warn(title=tr("DVD プロジェクトに変換…"),
                             message=tr("字幕の参照は引き継ぎました。DVD に書き出すには SUP 字幕を SRT に置き換えてください。"))

    @editor_language
    def save(self, file=None):
        if not self.edit_allowed():
            return
        path = file or self.api.filepath or self.choose_save_path()
        if not path:
            return
        path = os.path.abspath(path)
        extension = PROJECT_EXTENSIONS[self.disc_kind]
        if not path.lower().endswith(extension):
            raise ValueError(tr("保存先の拡張子に {0} を指定してください。", extension))
        save_project(path, self.project)
        changed_path = path != self.api.filepath
        was_saved = self.api.saved
        self.api.filepath = path
        self.saved_project = copy.deepcopy(self.project)
        self.api.saved = True
        if changed_path and was_saved:
            update = getattr(getattr(self.api, "app", None), "update_state", None)
            if update:
                update(self.api)
        self.report(tr("保存しました。 {0}", os.path.basename(path)))

    @editor_language
    def new(self):
        self.stop_preview()
        self.project = empty_project(self.disc_kind)
        self.saved_project = None
        self.history = History()
        self.load_error = None
        self.changed(tr("新しいプロジェクトを作成しました。"))

    def close(self):
        if self.host_tab_binding is not None:
            widget, binding = self.host_tab_binding
            widget.unbind("<<NotebookTabChanged>>", binding)
            self.host_tab_binding = None
        if self.history_menu is not None:
            self.history_menu.refresh()
        self.preview.dispose()
        if self.video_workspace is not None:
            workspace, self.video_workspace = self.video_workspace, None
            worker = self.preview.worker
            def cleanup():
                if worker is not None:
                    worker.join()
                workspace.cleanup()
            Thread(target=cleanup, daemon=True, name="Disc timeline preview cleanup").start()
