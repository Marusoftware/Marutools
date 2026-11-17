"""Version 1 disc projects and path-independent editing history."""
import copy
import json
import os
import re
import tempfile
from pathlib import Path
from uuid import uuid4

from .l10n import tr

VERSION = 1
PROJECT_EXTENSIONS = {"bluray": ".marubd", "dvd": ".marudvd"}
PROJECT_FORMATS = {"bluray": "marutools-bluray", "dvd": "marutools-dvd"}


def empty_project(kind="bluray"):
    settings = {"resolution": "1920x1080", "mode": "hdmv"} if kind == "bluray" else {"standard": "NTSC"}
    return {
        "format": PROJECT_FORMATS[kind], "version": VERSION,
        "name": "New Blu-ray" if kind == "bluray" else "New DVD", "source_bdmv": None, "titles": [],
        "menu": {"background": "", "buttons": [], "elements": []},
        "settings": settings,
    }


def convert_project(project, kind):
    converted = copy.deepcopy(project)
    defaults = empty_project(kind)
    converted["format"] = defaults["format"]
    converted["version"] = defaults["version"]
    converted["settings"] = defaults["settings"]
    return converted


def make_chapter(name, milliseconds):
    return {"id": uuid4().hex, "name": name, "time": format_time(milliseconds)}


def make_title(name, media, chapters):
    return {"id": uuid4().hex, "name": name, "media": media, "chapters": chapters}


def parse_time(value):
    match = re.fullmatch(r"([0-9]{2,}):([0-5][0-9]):([0-5][0-9])(?:\.([0-9]{1,3}))?", value.strip())
    if match is None:
        raise ValueError(tr("時刻は HH:MM:SS または HH:MM:SS.mmm で入力してください。"))
    hours, minutes, seconds, fraction = match.groups()
    return (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int((fraction or "0").ljust(3, "0"))


def format_time(milliseconds):
    seconds, fraction = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    stamp = f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{stamp}.{fraction:03}" if fraction else stamp


def load(path, kind=None):
    with open(path, encoding="utf-8") as stream:
        data = json.load(stream)
    kind = kind or next((name for name, extension in PROJECT_EXTENSIONS.items()
                         if Path(path).suffix.lower() == extension), "bluray")
    if not isinstance(data, dict) or data.get("format") != PROJECT_FORMATS[kind]:
        raise ValueError(tr("ファイルの内容が {0} プロジェクト形式と一致しません。", PROJECT_EXTENSIONS[kind]))
    if data.get("version") != VERSION:
        raise ValueError("Unsupported project version: %r" % data.get("version"))

    defaults = empty_project(kind)
    for key, value in defaults.items():
        data.setdefault(key, value)
    for key, value in defaults["menu"].items():
        data["menu"].setdefault(key, value)
    menu = data["menu"]
    title_text = menu.pop("title", "")
    title_position = menu.pop("position", {"x": 48, "y": 48})
    if title_text:
        menu["elements"].insert(0, {"kind": "text", "text": title_text, "position": title_position,
                                     "size": [300, 70]})
    for title in data["titles"]:
        title.setdefault("id", uuid4().hex)
        for chapter in title.setdefault("chapters", []):
            chapter.setdefault("id", uuid4().hex)
    return map_paths(data, lambda value: resolve_media(path, value))


def save(path, data):
    target = Path(path)
    data = map_paths(data, lambda value: store_media(target, value))
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f"{target.suffix}-", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def map_paths(project, convert):
    result = copy.deepcopy(project)

    def update(item, key):
        if item.get(key):
            item[key] = convert(item[key])

    update(result, "source_bdmv")
    update(result["menu"], "background")
    update(result["menu"], "motion")
    update(result["menu"], "music")
    for item in result["menu"].get("elements", []) + result["menu"]["buttons"]:
        update(item, "image")
        update(item, "font_file")
    for title in result["titles"]:
        update(title, "media")
        update(title, "playlist")
        for track in title.get("audio_tracks", []) + title.get("subtitle_tracks", []):
            update(track, "path")
        for segment in title.get("segments", []):
            update(segment, "media")
    for inventory in [result.get("bdmv_inventory") or {}, *result.get("bdmv_imports", [])]:
        update(inventory, "root")
        for key in ("playlists", "streams", "clpi"):
            if key in inventory:
                inventory[key] = [convert(path) for path in inventory[key]]
    return result


def resolve_media(project_path, media_path):
    if not media_path:
        return ""
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(project_path)), media_path))


def store_media(project_path, media_path):
    try:
        return os.path.relpath(media_path, os.path.dirname(os.path.abspath(project_path)))
    except ValueError:
        return os.path.abspath(media_path)


class History:
    def __init__(self):
        self.past = []
        self.future = []

    def record(self, project):
        self.past.append(copy.deepcopy(project))
        del self.past[:-50]
        self.future.clear()

    def undo(self, project):
        self.future.append(project)
        return self.past.pop()

    def redo(self, project):
        self.past.append(project)
        return self.future.pop()
