"""Menu layout editor embedded in the project tab."""
from copy import deepcopy
from functools import partial

from .assets import media_kind
from .l10n import localized, tr
from .menu_navigation import (
    BUTTONS_PER_PAGE, HEIGHT, UNLINKED, WIDTH, button_caption, button_geometry,
    clamp_position, element_geometry, page_count, page_elements, position, remove_menu_page, target_page,
)
from .menu_objects import capture_thumbnail, object_caption, open_object_image, render_object_image, render_text
from .menu_template import THUMBNAIL_COUNTS, generate_standard_menu
from .ui_support import SelectionList, tk_theme_colors


class MenuLayout:
    def __init__(self, parent, editor):
        self.editor = editor
        self.page = 0
        body = parent.Frame()
        body.pack(fill="both", expand=True, padx=8, pady=6)
        sidebar = body.Frame()
        sidebar.pack(side="left", fill="y", padx=(0, 8))
        stage = body.Frame()
        stage.pack(side="left", fill="both", expand=True)
        self.surface = MenuSurface(stage, self.select_item, self.commit)
        for caption, action in (
            (tr("標準レイアウトを生成…"), self.apply_standard_layout),
            (tr("背景・BGM…"), editor.edit_menu),
            (tr("画像を追加"), partial(self.change, "image")),
            (tr("テキストを追加"), partial(self.change, "text")),
            (tr("図形を追加"), partial(self.change, "shape")),
            (tr("動画サムネイルを追加"), partial(self.change, "thumbnail")),
            (tr("選択項目を編集"), self.change),
            (tr("削除"), self.remove),
            (tr("リモコン操作…"), self.remote_settings),
        ):
            sidebar.Input.Button(label=caption, command=localized(action)).pack(fill="x", pady=1)
        self.items = SelectionList(sidebar, height=6, width=155, on_select=self.highlight)

        row = parent.Frame()
        row.pack(fill="x", padx=8, pady=(0, 6))
        self.previous = row.Input.Button(label=tr("‹ 前へ"), command=localized(partial(self.go, -1)))
        self.page_label = row.Label(label="")
        self.page_label.configure(wraplength=0)
        self.following = row.Input.Button(label=tr("次へ ›"), command=localized(partial(self.go, 1)))
        for widget in (self.previous, self.page_label, self.following):
            widget.pack(side="left", padx=(0, 6))
        row.Input.Button(label=tr("ページを追加"), command=localized(self.add_page)).pack(side="left", padx=(0, 6))
        self.delete_page = row.Input.Button(label=tr("ページを削除"), command=localized(self.remove_page))
        self.delete_page.pack(side="left", padx=(0, 6))
        row.Input.Button(label=tr("初期配置に戻す"), command=localized(self.reset)).pack(side="right")
        self.background_status = row.Label(label="")
        self.background_status.pack(side="left", fill="x", expand=True, padx=6)

    def refresh(self, menu, selected=None):
        self.menu = deepcopy(menu)
        self.draw(selected)

    def draw(self, selected=None):
        count = page_count(self.menu)
        self.page = max(0, min(self.page, count - 1))
        start = self.page * BUTTONS_PER_PAGE
        entries = [(entry, index, self.editor.link_label(entry.get("target")))
                   for index, entry in enumerate(self.menu["buttons"][start:start + BUTTONS_PER_PAGE])]
        names = {title["id"]: title["name"] for title in self.editor.project["titles"]}
        elements = page_elements(self.menu, self.page)
        self.surface.draw(self.menu, elements, entries, names)
        rows = []
        for index, entry in elements:
            caption = object_caption(entry)
            target = entry.get("target")
            if target_page(target) is not None:
                caption = f"{caption} → {self.editor.link_label(target)}"
            rows.append((f"element{index}", caption))
        rows.extend((f"button{i}", button_caption(entry)) for entry, i, _ in entries)
        self.items.replace(rows, selected or self.items.selected)
        self.highlight()
        self.previous.configure(state="normal" if self.page else "disabled")
        self.following.configure(state="normal" if self.page + 1 < count else "disabled")
        self.delete_page.configure(state="normal" if count > 1 else "disabled")
        self.page_label.configure(label=f"{self.page + 1} / {count}")
        self.background_status.configure(label=self.surface.background_error)

    def select_item(self, tag):
        self.items.select(tag)
        self.surface.highlight(tag)

    def highlight(self):
        self.surface.highlight(self.items.selected)

    def go(self, offset):
        self.page += offset
        self.draw()

    def add_page(self):
        if self.editor.edit_allowed():
            self.page = page_count(self.menu)
            self.menu["page_count"] = self.page + 1
            self.commit()

    def apply_standard_layout(self):
        if not self.editor.edit_allowed():
            return
        titles = self.editor.project["titles"]
        if not any(media_kind(title) == "video" for title in titles):
            self.editor.report(tr("先に動画素材を追加してください。"))
            return
        caption = tr("標準レイアウトを生成…")
        field = tr("1ページのサムネイル数")
        result = self.editor.form(caption, [], choices=(field, "6", tuple(map(str, THUMBNAIL_COUNTS))),
                                  note=tr("既存のメニューページと項目を置き換えます。背景とBGMは引き継ぎます。"))
        if not result:
            return
        has_layout = bool(self.menu["elements"] or self.menu["buttons"] or page_count(self.menu) > 1)
        if has_layout and not self.editor.dialog.question(
            "yesno", caption, tr("現在のメニューページと項目を標準レイアウトで置き換えますか？"), default="no",
        ):
            return
        updated = generate_standard_menu(self.editor.api.ui, deepcopy(self.menu), deepcopy(titles), int(result[field]))
        if updated is not None:
            self.menu = updated
            self.page = 0
            self.commit()

    def remove_page(self):
        count = page_count(self.menu)
        if count <= 1 or not self.editor.edit_allowed():
            return
        message = tr("ページ {0} と、このページだけに表示される項目を削除しますか？", self.page + 1)
        message += "\n" + tr("このページへのリンクも解除されます。")
        if self.editor.dialog.question("yesno", tr("ページを削除"), message):
            remove_menu_page(self.menu, self.page)
            self.page = min(self.page, count - 2)
            self.commit()

    def commit(self, selected=None):
        self.editor.update_menu_layout(self.menu, selected)

    def selected_index(self):
        key = self.items.selected
        if key and key.startswith("button"):
            return "buttons", self.page * BUTTONS_PER_PAGE + int(key.removeprefix("button"))
        if key and key.startswith("element"):
            return "elements", int(key.removeprefix("element"))
        return None, None

    def change(self, kind=None):
        if not self.editor.edit_allowed():
            return
        group, index = self.selected_index()
        if kind is not None:
            added = self.editor.change_menu_element(kind, draft=self.menu, page=self.page)
            if added is not None:
                self.commit_element(added)
        elif group == "buttons":
            self.editor.change_button(index, draft=self.menu)
            self.commit(self.items.selected)
        elif group == "elements":
            changed = self.editor.change_menu_element(self.menu[group][index]["kind"], index,
                                                      draft=self.menu, page=self.page)
            if changed is not None:
                self.commit_element(changed)

    def commit_element(self, index):
        page = self.menu["elements"][index].get("page")
        if page is not None:
            self.page = page
        self.commit(f"element{index}")

    def remove(self):
        group, index = self.selected_index()
        if group and self.editor.edit_allowed():
            self.menu[group].pop(index)
            self.commit()

    def remote_settings(self):
        if self.editor.edit_allowed():
            self.editor.edit_remote_navigation(self.menu, self.page, self.items.selected)
            self.commit(self.items.selected)

    def reset(self):
        if self.editor.edit_allowed():
            start = self.page * BUTTONS_PER_PAGE
            buttons = self.menu["buttons"][start:start + BUTTONS_PER_PAGE]
            for entry in buttons + [entry for _, entry in page_elements(self.menu, self.page)]:
                entry.pop("position", None)
            self.commit()


class MenuSurface:
    """Keep image rendering and drag bindings confined to the Tk surface."""

    def __init__(self, stage, select_item, on_change):
        from tkinter import Canvas
        from tkinter.ttk import Scrollbar

        self.stage = stage
        self.drag = None
        self.resizing = None
        self.elements = {}
        self.select_item = select_item
        self.on_change = on_change
        self.canvas = Canvas(stage.widget, width=WIDTH + 4, height=HEIGHT + 4, highlightthickness=0,
                             scrollregion=(-2, -2, WIDTH + 2, HEIGHT + 2))
        horizontal = Scrollbar(stage.widget, orient="horizontal", command=self.canvas.xview)
        vertical = Scrollbar(stage.widget, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        stage.widget.columnconfigure(0, weight=1)
        stage.widget.rowconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        horizontal.grid(row=1, column=0, sticky="ew")
        vertical.grid(row=0, column=1, sticky="ns")
        self.update_theme()
        self.canvas.bind("<<ThemeChanged>>", self.update_theme, add="+")
        self.canvas.bind("<B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", localized(self.end_drag))
        self.background_path = None
        self.background_error = ""
        self.image = None
        self.item_images = []
        self.controls = []

    def load_background(self, background, motion):
        key = (background, motion)
        if key == self.background_path:
            return
        self.background_path = key
        self.background_error = ""
        self.image = None
        if background or motion:
            try:
                from PIL import Image, ImageOps, ImageTk

                item = {"thumbnail": capture_thumbnail({"media": motion}, 0)} if motion else {"image": background}
                with open_object_image(item) as image:
                    frame = ImageOps.exif_transpose(image).convert("RGB")
                    frame = ImageOps.fit(frame, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
                    self.image = ImageTk.PhotoImage(frame, master=self.canvas)
            except ImportError:
                self.background_error = tr("背景の表示には Pillow が必要です。")
            except (OSError, ValueError, Image.DecompressionBombError):
                self.background_error = tr("メニュー背景を読み込めませんでした。")

    def update_theme(self, event=None):
        self.background, self.foreground = tk_theme_colors(self.canvas)
        self.canvas.configure(background=self.background)
        self.canvas.itemconfigure("theme-fill", fill=self.background)
        self.canvas.itemconfigure("theme-text", fill=self.foreground)
        self.canvas.itemconfigure("theme-outline", outline=self.foreground)

    def draw(self, menu, elements, entries, title_names):
        self.drag = None
        self.resizing = None
        self.elements.clear()
        for control in self.controls:
            control.destroy()
        self.controls.clear()
        self.canvas.delete("all")
        self.item_images.clear()
        self.load_background(menu["background"], menu.get("motion"))
        if self.image is not None:
            self.canvas.create_image(0, 0, image=self.image, anchor="nw")
        self.canvas.create_rectangle(-1, -1, WIDTH, HEIGHT, outline=self.foreground,
                                     tags=("theme-outline",))

        for index, entry in elements:
            self.draw_element(entry, index, title_names)
        for entry, index, destination in entries:
            self.draw_button(entry, index, destination)

    def draw_element(self, entry, index, title_names):
        default, size = element_geometry(entry, index)
        tag = f"element{index}"
        self.elements[tag] = (entry, default, size)
        x, y = position(entry, default, size)
        if entry["kind"] == "image":
            image = self.load_item_image(entry, size, title_names)
            if image is not None:
                self.canvas.create_image(x, y, image=image, anchor="nw", tags=(tag,))
            else:
                self.draw_backing(x, y, size, tag)
                self.canvas.create_text(x + 8, y + 8, text=tr("画像を表示できません"), anchor="nw",
                                        fill=self.foreground, tags=(tag, "theme-text"))
        elif entry["kind"] == "shape":
            shape = self.canvas.create_oval if entry.get("shape") == "ellipse" else self.canvas.create_rectangle
            tags = [tag]
            if "fill" not in entry:
                tags.append("theme-fill")
            if "outline" not in entry:
                tags.append("theme-outline")
            shape(x, y, x + size[0], y + size[1], fill=entry.get("fill", self.background),
                  outline=entry.get("outline", self.foreground), tags=tags)
        else:
            from tkinter import TclError

            try:
                from PIL import ImageTk

                background = self.pillow_color(self.background)
                foreground = self.pillow_color(self.foreground)
                pixels = render_text(entry, size, background=background, foreground=foreground)
                image = ImageTk.PhotoImage(pixels, master=self.canvas)
            except (ImportError, OSError, ValueError, TclError):
                self.draw_backing(x, y, size, tag)
                self.canvas.create_text(x + 8, y + 6, text=entry["text"], anchor="nw",
                                        width=size[0] - 16, fill=self.foreground, tags=(tag, "theme-text"))
            else:
                self.item_images.append(image)
                self.canvas.create_image(x, y, image=image, anchor="nw", tags=(tag,))
        self.canvas.tag_bind(tag, "<Button-1>", partial(self.begin_drag, tag, entry, default, size))

    def pillow_color(self, color):
        # ttk may return Tcl objects or Tk-specific system color names.
        return tuple(channel >> 8 for channel in self.canvas.winfo_rgb(str(color)))

    def draw_backing(self, x, y, size, tag):
        self.canvas.create_rectangle(x, y, x + size[0], y + size[1], fill=self.background,
                                     outline="", tags=(tag, "theme-fill"))

    def load_item_image(self, entry, size, title_names=None):
        try:
            from PIL import Image, ImageTk

            image = render_object_image(entry, size, title_names)
            result = ImageTk.PhotoImage(image, master=self.canvas)
        except ImportError:
            return None
        except (OSError, ValueError, Image.DecompressionBombError):
            return None
        self.item_images.append(result)
        return result

    def draw_button(self, entry, index, destination):
        has_image = bool(entry.get("image"))
        default, size = button_geometry(entry, index)
        x, y = position(entry, default, size)
        tag = f"button{index}"
        unlinked = destination == tr(UNLINKED)
        caption = shorten(button_caption(entry), 18)
        if unlinked:
            caption += tr(" （リンク未設定）")
        options = {}
        if has_image:
            image = self.load_item_image(entry, (size[0] - 12, size[1] - 37))
            if image is not None:
                options.update(image=image, compound="top")
            else:
                caption = tr("画像を表示できません")
        button = self.stage.Input.Button(label=caption, command=lambda: None, **options)
        self.controls.append(button)
        self.canvas.create_window(x, y, anchor="nw", width=size[0], height=size[1] if has_image else 27,
                                  window=button.widget, tags=(tag,))
        if destination and not unlinked and not has_image:
            self.canvas.create_rectangle(x, y + 28, x + size[0], y + size[1], fill=self.background,
                                         outline="", tags=(tag, "theme-fill"))
            self.canvas.create_text(x + 5, y + 29, text=shorten(destination, 24),
                                    fill=self.foreground, anchor="nw", tags=(tag, "theme-text"))
        begin = partial(self.begin_drag, tag, entry, default, size)
        self.canvas.tag_bind(tag, "<Button-1>", begin)
        button.widget.configure(cursor="fleur", takefocus=False)
        button.widget.bind("<Button-1>", begin)
        button.widget.bind("<B1-Motion>", self.move)
        button.widget.bind("<ButtonRelease-1>", localized(self.end_drag))

    def begin_drag(self, tag, entry, default, size, event):
        self.select_item(tag)
        self.drag_position = position(entry, default, size)
        self.drag = (tag, entry, default, size, self.drag_position, (event.x_root, event.y_root))
        return "break"

    def move(self, event):
        if self.resizing:
            tag, origin, initial, pointer = self.resizing
            size = resize_dimensions(origin, initial, (event.x_root - pointer[0], event.y_root - pointer[1]))
            self.show_outline(origin, size, handle=True)
            return "break"
        if self.drag:
            tag, entry, default, size, (x, y), (start_x, start_y) = self.drag
            old_x, old_y = self.drag_position
            new_x, new_y = clamp_position(x + event.x_root - start_x, y + event.y_root - start_y, size)
            if (new_x, new_y) != (old_x, old_y):
                self.canvas.move(tag, new_x - old_x, new_y - old_y)
                self.drag_position = (new_x, new_y)
                self.highlight(tag)
        return "break"

    def end_drag(self, event):
        if self.resizing:
            tag, origin, initial, pointer = self.resizing
            size = resize_dimensions(origin, initial, (event.x_root - pointer[0], event.y_root - pointer[1]))
            self.resizing = None
            if size != initial:
                entry, _, _ = self.elements[tag]
                entry["size"] = list(size)
                entry["position"] = dict(zip(("x", "y"), origin))
                self.on_change(tag)
            return "break"
        if self.drag:
            self.move(event)
            tag, entry, default, size, origin, _ = self.drag
            self.drag = None
            if self.drag_position != origin:
                entry["position"] = dict(zip(("x", "y"), self.drag_position))
                self.on_change(tag)
        return "break"

    def highlight(self, tag):
        if self.resizing:
            return
        self.canvas.delete("selection-outline")
        if tag in self.elements:
            entry, default, size = self.elements[tag]
            origin = self.drag_position if self.drag and self.drag[0] == tag else position(entry, default, size)
            self.show_outline(origin, size, handle=True)
            self.canvas.tag_bind("resize-handle", "<Button-1>", partial(self.begin_resize, tag))
            return
        bounds = self.canvas.bbox(tag) if tag else None
        if bounds:
            x0, y0, x1, y1 = bounds
            self.canvas.create_rectangle(x0 - 2, y0 - 2, x1 + 2, y1 + 2,
                                         outline=self.foreground, dash=(3, 2),
                                         tags=("selection-outline", "theme-outline"))

    def begin_resize(self, tag, event):
        entry, default, size = self.elements[tag]
        self.drag = None
        self.resizing = (tag, position(entry, default, size), size, (event.x_root, event.y_root))
        return "break"

    def show_outline(self, origin, size, *, handle):
        self.canvas.delete("selection-outline")
        x, y = origin
        right, bottom = x + size[0] - 1, y + size[1] - 1
        self.canvas.create_rectangle(x, y, right, bottom, outline=self.foreground, dash=(3, 2),
                                     tags=("selection-outline", "theme-outline"))
        if handle:
            self.canvas.create_rectangle(right - 9, bottom - 9, right, bottom, fill=self.foreground,
                                         outline=self.background, tags=("selection-outline", "resize-handle"))


def resize_dimensions(origin, size, delta):
    return tuple(max(min(24, limit - start), min(limit - start, length + change))
                 for start, length, change, limit in zip(origin, size, delta, (WIDTH, HEIGHT)))


def shorten(text, limit):
    return text if len(text) <= limit else text[:limit - 1] + "…"
