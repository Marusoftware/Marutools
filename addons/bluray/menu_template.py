"""Generate editable top, chapter and stream-selection menu pages."""
from queue import Empty, SimpleQueue
from subprocess import SubprocessError
from threading import Event, Thread

from .assets import media_kind
from .disc_tracks import source_audio_languages
from .l10n import localized, tr
from .menu_navigation import WIDTH
from .menu_objects import capture_thumbnail
from .project import format_time, parse_time

THUMBNAIL_COUNTS = tuple(range(2, 17, 2))


def text_button(text, page, target, x, y, width, height, font_size=16):
    return {"kind": "text", "text": text, "page": page, "target": target,
            "position": {"x": x, "y": y}, "size": [width, height], "font_size": font_size,
            "fill": "#252a33", "foreground": "#ffffff"}


def footer(page, previous, following):
    links = [(tr("トップメニュー"), 0, 240, 160)]
    if previous is not None:
        links.append(("←", previous, 32, 45))
    if following is not None:
        links.append(("→", following, WIDTH - 77, 45))
    return [text_button(label, page, {"page": target}, x, 322, width, 28)
            for label, target, x, width in links]


def standard_menu(menu, titles, per_page, cancelled=lambda: False):
    if per_page not in THUMBNAIL_COUNTS:
        raise ValueError(tr("1ページのサムネイル数は2〜16の偶数を選んでください。"))
    scenes = []
    for title in titles:
        if media_kind(title) != "video":
            continue
        target = {"title": title["id"]}
        scenes.append((title, 0, target))
        marks = {}
        for chapter in title["chapters"]:
            stamp = parse_time(chapter["time"])
            if stamp > 0:
                marks.setdefault(stamp, chapter["id"])
        scenes.extend((title, stamp, {**target, "chapter": marks[stamp]}) for stamp in sorted(marks))
    if not scenes:
        raise ValueError(tr("先に動画素材を追加してください。"))

    chapter_pages = (len(scenes) + per_page - 1) // per_page
    first_settings = chapter_pages + 1
    elements = [
        text_button(tr(label), 0, target, 344, 103 + index * 56, 264, 40, 20)
        for index, (label, target) in enumerate((
            ("すべて再生", {"play_all": True}),
            ("チャプター", {"page": 1}),
            ("音声・字幕設定", {"page": first_settings}),
        ))
    ]
    # Centre a fixed grid with room for the video title and footer.
    columns = 2 if per_page <= 4 else 3 if per_page == 6 else 4
    rows = (per_page + columns - 1) // columns
    cell_width = (WIDTH - 64) // columns
    cell_height = 288 // rows
    height = min(cell_height - 12, (cell_width - 12) * 9 // 16 + 22)
    width = min(cell_width - 12, (height - 22) * 16 // 9)
    for index, (title, stamp, target) in enumerate(scenes):
        if cancelled():
            return None
        page, slot = divmod(index, per_page)
        row, column = divmod(slot, columns)
        try:
            image = capture_thumbnail(title, stamp)
        except (ValueError, OSError, ImportError, IndexError) as exc:
            raise ValueError(f"{title['name']} · {format_time(stamp)}\n{exc}") from exc
        elements.append({
            "kind": "image", "page": page + 1, "target": target, "size": [width, height],
            "position": {"x": 32 + column * cell_width + (cell_width - width) // 2,
                         "y": 14 + row * cell_height + (cell_height - height) // 2},
            "thumbnail": image, "thumbnail_source": title["id"], "show_video_title": True,
            "thumbnail_name": f"{title['name']} · {format_time(stamp)}",
        })
    for page in range(1, first_settings):
        elements.extend(footer(page, page - 1 if page > 1 else None,
                               page + 1 if page < chapter_pages else None))

    settings = []
    for number, title in enumerate(titles, 1):
        if cancelled():
            return None
        try:
            internal = source_audio_languages(title)
        except (OSError, ValueError, SubprocessError) as exc:
            raise ValueError(tr("「{0}」の音声トラックを確認できませんでした。", title["name"])) from exc
        audio = internal + [track["language"] for track in title.get("audio_tracks", [])] or ["und"]
        subtitles = [tr("字幕を消す")] + [
            tr("字幕 {0} · {1}", i, track["language"]) for i, track in enumerate(title.get("subtitle_tracks", []), 1)
        ]
        name = " ".join(title["name"].split())
        if len(name) > 28:
            name = name[:27] + "…"
        for audio_index, language in enumerate(audio, 1):
            audio_label = tr("音声 {0} · {1}", audio_index, language)
            for subtitle_index, subtitle_label in enumerate(subtitles):
                label = f"{audio_label} / {subtitle_label}   {number}. {name}"
                settings.append((label, {"title": title["id"], "audio": audio_index, "subtitle": subtitle_index}))
    settings_page_size = 9
    count = first_settings + (len(settings) + settings_page_size - 1) // settings_page_size
    for index, (label, target) in enumerate(settings):
        page, slot = divmod(index, settings_page_size)
        elements.append(text_button(label, first_settings + page, target, 32, 14 + slot * 32, 576, 28, 14))
    for page in range(first_settings, count):
        elements.extend(footer(page, page - 1 if page > first_settings else None,
                               page + 1 if page + 1 < count else None))

    return {**menu, "buttons": [], "elements": elements, "page_count": count,
            "initial_focus": {}, "auto_page_buttons": False}


def generate_standard_menu(ui, menu, titles, per_page):
    """Keep the editor responsive while FFmpeg extracts the thumbnails."""
    from tkinter.ttk import Progressbar

    caption = tr("標準レイアウトを生成…")
    window = ui.makeSubWindow(dialog=True)
    window.changeTitle(caption)
    label = window.Label(label=tr("サムネイルとメニューページを作成中…"))
    label.configure(wraplength=0)
    label.pack(fill="x", padx=12, pady=(12, 4))
    bar = Progressbar(window.root, mode="indeterminate", length=350)
    bar.pack(fill="x", padx=12, pady=4)
    events = SimpleQueue()
    cancel = Event()
    result = None
    timer = None

    def close():
        cancel.set()
        if timer is not None:
            bar.after_cancel(timer)
        bar.stop()
        window.close()

    def worker():
        try:
            events.put((standard_menu(menu, titles, per_page, cancel.is_set), None))
        except Exception as exc:
            events.put((None, str(exc)))

    def poll():
        nonlocal result, timer
        timer = None
        try:
            result, error = events.get_nowait()
        except Empty:
            timer = bar.after(100, poll)
            return
        close()
        if error:
            ui.Dialog.error(title=caption, message=error)

    window.Input.Button(label=tr("中止"), command=close).pack(anchor="e", padx=12, pady=(4, 12))
    window.setcallback("close", close)
    bar.start(50)
    timer = bar.after(100, poll)
    Thread(target=localized(worker), name="Blu-ray menu template", daemon=True).start()
    window.wait()
    return result
