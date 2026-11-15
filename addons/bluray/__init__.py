"""Marutools Blu-ray project editor."""
import copy
import os
from pathlib import Path
from uuid import uuid4

from . import bdmv
from .assets import AUDIO_TYPES, IMAGE_TYPES, MEDIA_LABELS, VIDEO_TYPES
from .assets import file_pattern, media_duration, media_kind, path_kind
from .export_dialog import show_export_dialog
from .menu_objects import OBJECT_LABELS, SHAPES, capture_thumbnail, object_caption, menu_font, valid_color
from .menu_objects import SHOW_VIDEO_TITLE, VIDEO_TITLE_OPTIONS
from .menu_navigation import UNLINKED, page_buttons
from .menu_layout import MenuLayout
from .preflight import check_project, issue_message
from .preview import Preview
from .project import History, empty_project, format_time, load, make_chapter, make_title, parse_time
from .project import save as save_project
from .ui_support import SeekBar, SelectionList, install_history_menu, project_tabs, split_frames

__version__ = "0.5"


class Edit:
    name = "Blu-ray"
    description = "Blu-ray project editor v" + __version__
    file_types = ["marubd"]

    def __init__(self, api):
        self.api = api
        self.dialog = api.ui.Dialog
        self.project = empty_project()
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
        if api.filepath and os.path.isfile(api.filepath):
            try:
                self.project = load(api.filepath)
            except (OSError, ValueError, TypeError, AttributeError, KeyError) as exc:
                self.load_error = str(exc)
            else:
                self.saved_project = copy.deepcopy(self.project)
        self.build_ui()
        self.refresh()
        if self.load_error:
            self.report("プロジェクトを開けませんでした。 " + self.load_error)
        elif self.project["titles"]:
            self.report("タイトルを選択して編集できます。")
        else:
            self.report("素材または BDMV を追加してください。")

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
            widget = row.Input.Button(label=caption, command=command, width=0)
            widget.pack(side="left", padx=2)
            buttons.append(widget)
        return buttons

    def build_ui(self):
        root = self.api.ui.Frame()
        root.pack(fill="both", expand=True)
        self.buttons(root, ("書き出し", self.export_bdmv))
        self.history_buttons = []
        self.history_menu = install_history_menu(self.api, Edit)
        if self.history_menu is None:
            self.history_buttons = self.buttons(root, ("元に戻す", self.undo), ("やり直す", self.redo))
        else:
            # The host attaches the addon context to the tab after construction.
            root.widget.after_idle(self.history_menu.refresh)
        footer = self.frame(root, side="bottom", fill="x", padx=8, pady=4)
        details = footer.Input.Button(label="詳細設定 ›", command=self.properties, width=0)
        details.pack(side="right", padx=2)
        audio_settings = footer.Input.Button(label="音声出力", command=self.configure_audio, width=0)
        audio_settings.pack(side="right", padx=2)
        check = footer.Input.Button(label="チェック", command=self.validate, width=0)
        check.pack(side="right", padx=2)
        self.status = footer.Label(label="")
        self.status.pack(side="left", fill="x", expand=True, padx=4)

        media_tab, menu_tab = project_tabs(root)
        self.menu_layout = None
        if getattr(menu_tab, "backend", None) == "tkinter":
            self.menu_layout = MenuLayout(menu_tab, self)

        self.buttons(media_tab, ("＋ 素材を追加", self.add_asset), ("BDMVを開く", self.import_bdmv))
        body = self.frame(media_tab, fill="both", expand=True, padx=8, pady=(2, 0))
        left, right = split_frames(body)
        self.label(left, "素材")
        self.titles = SelectionList(left, 3, 245, self.title_selected)
        self.buttons(left, ("名前変更", self.rename_title), ("削除", self.delete_title),
                     ("↑", lambda: self.move_title(-1)), ("↓", lambda: self.move_title(1)))
        self.preview = Preview(
            self.frame(right, fill="both", expand=True), self.play,
            lambda: self.report("プレビューを開始しました。"),
            lambda message: self.report(f"プレビュー: {message}"),
            self.follow_playback,
        )
        self.buttons(right, ("再生", self.play), ("一時停止／再開", self.pause), ("停止", self.stop))
        self.seek_bar = SeekBar(right, self.set_position, self.seek_from_bar)
        self.buttons(right, ("この位置にチャプターを追加", self.add_chapter),
                     ("チャプター一覧", self.show_chapters))
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
                        path = window.Dialog.askfile(title=f"{field}を選択",
                                                     filetypes=[("フォント", "*.ttf *.otf *.ttc")])
                        if path:
                            inputs[field].set(os.path.abspath(path))

                caption = "色を選択…" if label in color_fields else "参照…"
                for caption, command in ((caption, choose), ("解除", lambda field=label: inputs[field].set(""))):
                    row.Input.Button(label=caption, command=command).pack(side="left", padx=2)
        selectors = (*extra_choices, choices) if choices else extra_choices
        for label, default, values in selectors:
            choice_label = window.Label(label=label)
            choice_label.configure(wraplength=0)
            choice_label.pack(fill="x", padx=12, pady=(8, 2))
            inputs[label] = window.Input.Select(default=default, command=lambda: None, values=values, inline=True)
            inputs[label].pack(fill="x", padx=12)

        def accept():
            nonlocal result
            result = {label: field.value.strip() for label, field in inputs.items()}
            window.close()

        row = window.Frame()
        row.pack(fill="x", padx=10, pady=12)
        row.Input.Button(label="適用", command=accept).pack(side="right", padx=2)
        row.Input.Button(label="キャンセル", command=window.close).pack(side="right", padx=2)
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
        for number, title in enumerate(self.project["titles"], 1):
            prefix = f"{number}. {title['name']}"
            if link == {"title": title["id"]}:
                return f"{prefix}（タイトル先頭）"
            for chapter in title["chapters"]:
                if link == {"title": title["id"], "chapter": chapter["id"]}:
                    return f"{prefix} / {chapter['name']} ({chapter['time']})"
        return UNLINKED

    def refresh(self, title_id=None, chapter_id=None, menu_selection=None):
        self.api.saved = self.load_error is not None or self.project == self.saved_project
        if self.history_menu is not None:
            self.history_menu.refresh()
        for button, entries in zip(self.history_buttons, (self.history.past, self.history.future)):
            button.configure(state="normal" if entries else "disabled")
        self.titles.replace(
            [(title["id"], f"{MEDIA_LABELS[media_kind(title)]}  ·  {title['name']}")
             for title in self.project["titles"]], title_id or self.titles.selected)
        self.title_selected(chapter_id, force=True)
        if self.menu_layout is not None:
            self.menu_layout.refresh(self.project["menu"], menu_selection)

    def title_selected(self, chapter_id=None, force=False):
        title = self.title
        title_id = title["id"] if title else None
        if not force and title_id == self.active_title:
            return
        if title_id != self.active_title:
            self.stop_preview()
            self.duration = None
            self.chapter_id = None
            if title and media_kind(title) != "image":
                self.duration = title.get("duration_ms")
                if self.duration is None and os.path.isfile(title["media"]):
                    self.duration = media_duration(title["media"])
        self.active_title = title_id
        if chapter_id:
            self.chapter_id = chapter_id
        self.refresh_chapters()
        self.source_label.configure(label=os.path.basename(title["media"]) if title else "素材を追加してください")
        self.update_time()

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
            return self.report("動画か音声を選択してください。")
        window = self.api.ui.makeSubWindow(dialog=True)
        window.changeTitle("チャプター一覧")
        self.chapter_window = window
        self.chapters = SelectionList(window, 8, 340)
        self.refresh_chapters()
        self.buttons(window, ("追加", self.add_chapter), ("編集", self.edit_chapter),
                     ("削除", self.delete_chapter), ("移動", self.seek), ("閉じる", window.close))
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
            self.report("プロジェクトを開けなかったため、編集と保存を利用できません。")
            return False
        return True

    def changed(self, message, **selection):
        self.refresh(**selection)
        self.report(message)

    def add_asset(self):
        if not self.edit_allowed():
            return
        path = self.dialog.askfile(title="素材を選択", filetypes=[
            ("画像・音声・動画", file_pattern(IMAGE_TYPES + AUDIO_TYPES + VIDEO_TYPES)),
            ("すべてのファイル", "*"),
        ])
        if not path:
            return
        if not os.path.isfile(path):
            self.report("選択した素材が見つかりません。")
            return
        kind = path_kind(path)
        chapters = [] if kind == "image" else [make_chapter("チャプター 1", 0)]
        title = make_title(Path(path).stem, os.path.abspath(path), chapters)
        title["kind"] = kind
        self.history.record(self.project)
        self.project["titles"].append(title)
        self.changed("素材を追加しました。", title_id=title["id"])

    def import_bdmv(self):
        if not self.edit_allowed():
            return
        path = self.dialog.askdir(title="BDMV フォルダか、その親フォルダを選択")
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
            self.dialog.warn(title="BDMV", message="取り込めるタイトルがありません。\n"
                             + "\n".join(inventory["warnings"]))
            return
        self.history.record(self.project)
        if not self.project.get("source_bdmv"):
            self.project["source_bdmv"] = incoming["source_bdmv"]
            self.project["bdmv_inventory"] = inventory
        else:
            self.project.setdefault("bdmv_imports", []).append(inventory)
        self.project["titles"].extend(titles)
        self.changed(f"BDMV から {len(titles)} 件のタイトルを追加しました。"
                     f" 警告 {len(inventory['warnings'])} 件", title_id=titles[0]["id"])

    def rename_title(self):
        title = self.title
        if not title:
            return self.report("タイトルを選択してください。")
        result = self.form("タイトル名", [("名前", title["name"])])
        if result and result["名前"] and result["名前"] != title["name"]:
            self.history.record(self.project)
            title["name"] = result["名前"]
            self.changed("タイトル名を変更しました。")

    def delete_title(self):
        title = self.title
        if not title:
            return self.report("タイトルを選択してください。")
        if not self.dialog.question("yesno", "タイトルの削除", f"「{title['name']}」をプロジェクトから削除しますか？"):
            return
        titles = self.project["titles"]
        index = titles.index(title)
        self.history.record(self.project)
        titles.remove(title)
        self.clear_links(title["id"])
        next_id = titles[min(index, len(titles) - 1)]["id"] if titles else None
        self.changed("タイトルを削除しました。", title_id=next_id)

    def move_title(self, step):
        title = self.title
        if not title:
            return self.report("タイトルを選択してください。")
        titles = self.project["titles"]
        index = titles.index(title)
        if 0 <= index + step < len(titles):
            self.history.record(self.project)
            titles.insert(index + step, titles.pop(index))
            self.changed("タイトルを並べ替えました。")

    def add_chapter(self):
        self.change_chapter(None)

    def edit_chapter(self):
        if not self.chapter:
            return self.report("チャプターを選択してください。")
        self.change_chapter(self.chapter)

    def change_chapter(self, chapter):
        title = self.title
        if not title or media_kind(title) == "image":
            return self.report("動画か音声を選択してください。")
        chapters = title["chapters"]
        name = chapter["name"] if chapter else f"チャプター {len(chapters) + 1}"
        time = chapter["time"] if chapter else format_time(self.position)
        values = self.form("チャプター", [("名前", name), ("時刻 (HH:MM:SS.mmm)", time)])
        if not values:
            return
        try:
            milliseconds = parse_time(values["時刻 (HH:MM:SS.mmm)"])
            if not values["名前"]:
                raise ValueError("チャプター名を入力してください。")
            if self.duration is not None and milliseconds >= self.duration:
                raise ValueError("タイトルの終了時刻より前の時刻を指定してください。")
        except ValueError as exc:
            self.report(str(exc))
            return
        name, time = values["名前"], format_time(milliseconds)
        if chapter and (chapter["name"], chapter["time"]) == (name, time):
            return
        self.history.record(self.project)
        if chapter:
            chapter.update(name=name, time=time)
        else:
            chapter = make_chapter(name, milliseconds)
            chapters.append(chapter)
        chapters.sort(key=self.chapter_order)
        self.changed("チャプターを更新しました。", chapter_id=chapter["id"])

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
            return self.report("チャプターを選択してください。")
        self.history.record(self.project)
        title["chapters"].remove(chapter)
        self.clear_links(title["id"], chapter["id"])
        self.changed("チャプターを削除しました。")

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
            self.changed("メニューの配置を更新しました。", menu_selection=selected)

    def edit_remote_navigation(self, menu, page, selected_tag):
        items = [item for item in page_buttons(menu, page)
                 if item.next_page is not None or self.link_label(item.target) != UNLINKED]
        if not items:
            self.dialog.info(title="リモコン操作", message="リンク付きの項目を配置してください。")
            return
        automatic = "自動"
        labels = {automatic: None}
        for number, item in enumerate(items, 1):
            labels[f"{number}. {item.caption}"] = item

        def choice(name, preferred):
            current = next((label for label, item in labels.items() if item and item.key == preferred), automatic)
            return name, current, list(labels)

        page_key = str(page)
        first = "初期選択"
        selectors = [choice(first, menu.get("initial_focus", {}).get(page_key))]
        item = next((item for item in items if item.tag == selected_tag), None)
        directions = {"up": "上", "down": "下", "left": "左", "right": "右"}
        if item:
            current_moves = item.entry.get("navigation", {}).get(page_key, {})
            selectors.extend(choice(label, current_moves.get(direction))
                             for direction, label in directions.items())
        note = (f"{page + 1}ページ目 · 「{item.caption}」からの移動" if item
                else "上下左右の移動先を変更するには、リンク付きの項目を選んでください。")
        values = self.form("リモコン操作", [], extra_choices=selectors, note=note)
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
        images, default = self.menu_image_choices(menu["background"], empty="背景なし")
        values = self.form("メニュー背景", [], choices=("背景画像", default, list(images)),
                           note="画像は「素材を追加」で登録できます。")
        if not values:
            return
        background = images[values["背景画像"]]
        if background == menu["background"]:
            return
        try:
            background = self.menu_image_path(background)
        except ValueError as exc:
            return self.report(str(exc))
        self.history.record(self.project)
        menu["background"] = background
        self.changed("メニュー背景を更新しました。")

    def menu_links(self):
        links = {UNLINKED: None}
        for number, title in enumerate(self.project["titles"], 1):
            prefix = f"{number}. {title['name']}"
            links[f"{prefix}（タイトル先頭）"] = {"title": title["id"]}
            for chapter_no, chapter in enumerate(title["chapters"], 1):
                links[f"{prefix} / {chapter_no}. {chapter['name']} ({chapter['time']})"] = {
                    "title": title["id"], "chapter": chapter["id"],
                }
        return links

    def menu_image_path(self, value):
        if not value:
            return ""
        path = os.path.abspath(os.path.join(os.path.dirname(self.api.filepath or ""), value))
        if not os.path.isfile(path):
            raise ValueError("画像ファイルが見つかりません。")
        return path

    def menu_image_choices(self, current="", *, empty=None, embedded=False):
        images = {empty: ""} if empty else {}
        for index, title in enumerate(self.project["titles"], 1):
            if media_kind(title) == "image":
                images[f"{index}. {title['name']}"] = title["media"]
        if embedded:
            images["現在の動画サムネイル"] = None
            return images, "現在の動画サムネイル"
        if current and current not in images.values():
            images[f"設定済み画像 · {Path(current).name}"] = current
        default = next((label for label, path in images.items() if path == current), next(iter(images), ""))
        return images, default

    def change_menu_element(self, kind, index=None, *, draft):
        if not self.edit_allowed():
            return
        elements = draft["elements"]
        existing = elements[index] if index is not None else {}
        dialog = self.dialog
        if kind == "thumbnail":
            videos = {f"{i}. {title['name']}": title for i, title in enumerate(self.project["titles"], 1)
                      if media_kind(title) == "video"}
            if not videos:
                dialog.error(title="動画サムネイル", message="先に動画素材を追加してください。")
                return
            default = next((label for label, title in videos.items() if title is self.title), next(iter(videos)))
            initial_time = self.position if videos[default] is self.title else 0
            values = self.form("動画サムネイル", [("時刻 (HH:MM:SS.mmm)", format_time(initial_time))],
                               extra_choices=(("動画素材", default, list(videos)),
                                              (SHOW_VIDEO_TITLE, VIDEO_TITLE_OPTIONS[0], VIDEO_TITLE_OPTIONS)))
            if not values:
                return
            source = videos[values["動画素材"]]
            try:
                stamp = parse_time(values["時刻 (HH:MM:SS.mmm)"])
                image = capture_thumbnail(source, stamp)
            except (ValueError, OSError, ImportError) as exc:
                dialog.error(title="動画サムネイル", message=str(exc))
                return
            updated = {"kind": "image", "thumbnail": image,
                       "thumbnail_name": f"{source['name']} · {format_time(stamp)}",
                       "thumbnail_source": source["id"],
                       "show_video_title": values[SHOW_VIDEO_TITLE] == VIDEO_TITLE_OPTIONS[1],
                       "target": {"title": source["id"]}}
        else:
            links = self.menu_links()
            default = next((label for label, target in links.items() if existing.get("target") == target), UNLINKED)
            caption = OBJECT_LABELS[kind]
            key = {"shape": "shape", "image": "image", "text": "text"}[kind]
            current = existing.get(key, "")
            if kind == "shape":
                current = object_caption(existing) if existing else "長方形"
            embedded = kind == "image" and bool(existing.get("thumbnail"))
            fields = [(caption, current)] if kind == "text" else []
            extra = (("図形の種類", current, list(SHAPES)),) if kind == "shape" else ()
            if kind == "image":
                images, selected = self.menu_image_choices(current, embedded=embedded)
                if not images:
                    dialog.info(title="画像素材", message="先に「素材を追加」で画像を登録してください。")
                    return
                extra = (("画像素材", selected, list(images)),)
                if embedded:
                    current_title = VIDEO_TITLE_OPTIONS[bool(existing.get("show_video_title"))]
                    extra += ((SHOW_VIDEO_TITLE, current_title, VIDEO_TITLE_OPTIONS),)
            colors = ()
            if kind == "shape":
                colors = ("塗り色", "線の色")
                fields.extend([(colors[0], existing.get("fill", "")), (colors[1], existing.get("outline", ""))])
            elif kind == "text":
                colors = ("文字色", "背景色")
                fields.extend([("フォントファイル", existing.get("font_file", "")),
                               ("文字サイズ (px)", str(existing.get("font_size", 12))),
                               (colors[0], existing.get("foreground", "")), (colors[1], existing.get("fill", ""))])
            values = self.form(caption, fields, choices=("リンク先", default, list(links)),
                               extra_choices=extra, color_fields=colors,
                               font_field="フォントファイル" if kind == "text" else None)
            if not values:
                return
            updated = {**existing, "kind": kind, "target": links[values["リンク先"]]}
            if kind != "image" or images[values["画像素材"]] is not None:
                try:
                    if kind == "image":
                        image = images[values["画像素材"]]
                        value = current if image == current else self.menu_image_path(image)
                        updated.pop("thumbnail", None)
                        updated.pop("thumbnail_name", None)
                        updated.pop("thumbnail_source", None)
                        updated.pop("show_video_title", None)
                    elif kind == "shape":
                        value = SHAPES[values["図形の種類"]]
                    else:
                        value = values[caption]
                    if not value:
                        raise ValueError(f"{caption}を指定してください。")
                except ValueError as exc:
                    dialog.error(title=caption, message=str(exc))
                    return
                updated[key] = value
            elif embedded:
                if values[SHOW_VIDEO_TITLE] == VIDEO_TITLE_OPTIONS[1]:
                    updated["show_video_title"] = True
                elif "show_video_title" in updated:
                    updated["show_video_title"] = False
            try:
                for field, style in zip(colors, ("fill", "outline") if kind == "shape" else ("foreground", "fill")):
                    color = values[field]
                    if color and not valid_color(color):
                        raise ValueError(f"{field}は #RRGGBB 形式で指定してください。")
                    if color:
                        updated[style] = color
                    else:
                        updated.pop(style, None)
                if kind == "text":
                    size = values["文字サイズ (px)"]
                    if not size.isdecimal() or not 6 <= int(size) <= 120:
                        raise ValueError("文字サイズは 6〜120 px で指定してください。")
                    updated["font_size"] = int(size)
                    font = values["フォントファイル"]
                    if font:
                        font = os.path.abspath(os.path.join(os.path.dirname(self.api.filepath or ""), font))
                        menu_font(int(size), font)
                        updated["font_file"] = font
                    else:
                        updated.pop("font_file", None)
            except (ValueError, OSError, ImportError) as exc:
                dialog.error(title=caption, message=str(exc))
                return
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
        links = self.menu_links()
        default = next((label for label, target in links.items() if existing.get("target") == target), UNLINKED)
        name = existing.get("label", existing.get("name", Path(image_path).stem or f"ボタン {len(buttons) + 1}"))
        images, selected = self.menu_image_choices(image_path, empty="画像なし")
        values = self.form("メニューボタン", [("表示名", name)],
                           extra_choices=(("サムネイル画像", selected, list(images)),),
                           choices=("リンク先", default, list(links)))
        if not values:
            return
        if not values["表示名"]:
            return self.report("ボタンの表示名を入力してください。")
        target = links[values["リンク先"]]
        try:
            image = images[values["サムネイル画像"]]
            if image != image_path:
                image = self.menu_image_path(image)
        except ValueError as exc:
            self.dialog.error(title="サムネイル画像", message=str(exc))
            return None
        if image and image != image_path:
            try:
                from PIL import Image
            except ImportError:
                self.dialog.error(title="サムネイル画像", message="Pillow が必要です。")
                return None
            try:
                with Image.open(image) as picture:
                    picture.verify()
            except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
                self.dialog.error(title="サムネイル画像", message=f"画像を読み込めません。 {exc}")
                return None
        if (existing.get("label"), existing.get("target"), existing.get("image", "")) == (values["表示名"], target, image):
            return
        if index is None:
            index = len(buttons)
            buttons.append({})
        buttons[index].update(label=values["表示名"], target=target)
        if image:
            buttons[index]["image"] = image
        else:
            buttons[index].pop("image", None)
        return index

    def undo(self):
        if self.history.past:
            self.project = self.history.undo(self.project)
            self.changed("元に戻しました。")

    def redo(self):
        if self.history.future:
            self.project = self.history.redo(self.project)
            self.changed("やり直しました。")

    def inventories(self):
        initial = self.project.get("bdmv_inventory")
        return ([initial] if initial else []) + self.project.get("bdmv_imports", [])

    def properties(self):
        if not self.edit_allowed():
            return
        title = self.title
        info = [f"保存先　{self.api.filepath or '未保存'}"]
        if title:
            info.append(f"タイトル　{title['name']}\n素材　{title['media']}")
            if title.get("segments"):
                info.append(f"再生区間　{len(title['segments'])} 件 / {format_time(title['duration_ms'])}")
        for inventory in self.inventories():
            info.append(f"BDMV　{inventory['root']}")
            warnings = inventory.get("warnings", [])
            info.extend(warnings[:5])
            if len(warnings) > 5:
                info.append(f"ほか {len(warnings) - 5} 件の警告")
        values = self.form("詳細設定", [("プロジェクト名", self.project["name"])], note="\n".join(info))
        if values and values["プロジェクト名"] and values["プロジェクト名"] != self.project["name"]:
            self.history.record(self.project)
            self.project["name"] = values["プロジェクト名"]
            self.changed("プロジェクト名を変更しました。")

    def validate(self):
        if not self.edit_allowed():
            return
        errors, warnings = check_project(self.project)
        if errors or warnings:
            self.report(f"書き出し前チェック　エラー {len(errors)} 件・警告 {len(warnings)} 件")
            details = []
            if errors:
                details.append("エラー\n" + issue_message(errors))
            if warnings:
                details.append("警告\n" + issue_message(warnings))
            self.dialog.warn(title="書き出し前チェック", message="\n\n".join(details))
        else:
            self.report("書き出し前チェックに問題はありません。")

    def export_bdmv(self):
        if not self.edit_allowed():
            return
        if not self.project["titles"]:
            return self.report("書き出す素材を追加してください。")
        show_export_dialog(self.api.ui, self.project, self.api.filepath, self.stop, self.report)

    def audio_settings(self):
        host = getattr(self.api, "app", None)
        settings = getattr(host, "_bluray_audio_settings", None)
        if settings is None:
            settings = self.audio_preferences
        if settings is None:
            settings = {"audio_output": None}
            if getattr(self.api, "appinfo", {}).get("conf"):
                from libmarusoftware import Config

                settings = Config(appname=self.name, module="preview",
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
            return self.report(f"音声出力の設定を開けませんでした。 {exc}")
        choices = {"システム既定": None, "ミュート": "mute", **outputs}
        current = settings["audio_output"]
        default = next((label for label, device in choices.items() if device == current), "システム既定")
        values = self.form("Blu-ray プレビューの音声出力", [],
                           choices=("出力先", default, list(choices)),
                           note="変更は次回の再生から適用されます。")
        if values:
            try:
                settings.update(audio_output=choices[values["出力先"]])
            except OSError as exc:
                return self.report(f"音声出力設定を保存できませんでした。 {exc}")
            self.report(f"次回のプレビューの音声出力: {values['出力先']}")

    def play_at(self, milliseconds, *, seek=False):
        if not self.title:
            return self.report("素材を選択してください。")
        try:
            self.preview.play(self.title, milliseconds, self.audio_settings()["audio_output"], seek=seek)
        except Exception as exc:
            self.report(f"プレビュー: {exc}")
            return
        self.position = milliseconds
        self.update_time()
        self.report("画像を表示しました。" if media_kind(self.title) == "image" else "プレビューを読み込んでいます。")

    def play(self):
        self.play_at(self.position)

    def pause(self):
        try:
            self.preview.pause_resume()
        except Exception as exc:
            self.report(f"プレビュー: {exc}")

    def seek(self):
        if not self.chapter:
            return self.report("チャプターを選択してください。")
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
            self.report(f"プレビュー: {exc}")
        self.position = 0

    def stop(self):
        self.stop_preview()
        self.update_time()

    def choose_save_path(self):
        if not self.edit_allowed():
            return
        path = self.dialog.askfile(save=True, title="プロジェクトを保存", defaultextension=".marubd",
                                   filetypes=[("Blu-ray プロジェクト", "*.marubd")])
        return path

    def save(self, file=None):
        if not self.edit_allowed():
            return
        path = file or self.api.filepath or self.choose_save_path()
        if not path:
            return
        path = os.path.abspath(path)
        if not path.lower().endswith(".marubd"):
            raise ValueError("保存先の拡張子に .marubd を指定してください。")
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
        self.report(f"保存しました。 {os.path.basename(path)}")

    def new(self):
        self.stop_preview()
        self.project = empty_project()
        self.saved_project = None
        self.history = History()
        self.load_error = None
        self.changed("新しいプロジェクトを作成しました。")

    def close(self):
        if self.history_menu is not None:
            self.history_menu.refresh()
        self.preview.dispose()
