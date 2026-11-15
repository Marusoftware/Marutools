"""Inspect source tracks and turn SRT captions into Blu-ray PGS."""
import json
import re
import subprocess
from pathlib import Path
from types import SimpleNamespace
from itertools import zip_longest

from .l10n import tr
from .assets import media_kind
from .menu_objects import menu_font
from .project import parse_time

# Blu-ray playlist language fields are ISO 639-2 codes.
LANGUAGE = re.compile(r"[a-z]{3}")
SRT_TIME = re.compile(r"(\d{2,}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2,}:\d{2}:\d{2}[,.]\d{3})")


def audio_languages(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                             "-show_entries", "stream_tags=language", "-of", "json", str(path)],
                            capture_output=True, text=True, check=True)
    languages = []
    for stream in json.loads(result.stdout)["streams"]:
        language = stream.get("tags", {}).get("language", "und").lower()
        languages.append(language if LANGUAGE.fullmatch(language) else "und")
    return languages


def source_audio_languages(title):
    if media_kind(title) == "image":
        return []
    if title.get("segments"):
        tracks = [audio_languages(path) for path in dict.fromkeys(part["media"] for part in title["segments"])]
        languages = [set(group) - {None} for group in zip_longest(*tracks)]
        return [next(iter(group)) if len(group) == 1 else "und" for group in languages]
    return audio_languages(title["media"])


def read_srt(path):
    text = Path(path).read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError(tr("SRT に字幕がありません。 {0}", path))
    cues = []
    for block in re.split(r"\n[ \t]*\n", text):
        lines = block.splitlines()
        line = 1 if lines and lines[0].strip().isdigit() else 0
        timing = SRT_TIME.match(lines[line].strip()) if len(lines) > line else None
        if not timing or len(lines) <= line + 1:
            raise ValueError(tr("SRT の時刻または本文を確認してください。 {0}", path))
        start, end = (parse_time(value.replace(",", ".")) / 1000 for value in timing.groups())
        if end <= start:
            raise ValueError(tr("SRT の終了時刻を確認してください。 {0}", path))
        caption = "\n".join(lines[line + 1:])
        cues.append(SimpleNamespace(start=start, end=end, text=re.sub(r"</?(?:i|b|u)>", "", caption)))
    return sorted(cues, key=lambda cue: cue.start)


def write_subtitle(source, target, duration, check):
    from bdmvkit import pgs
    from PIL import Image, ImageDraw

    if Path(source).suffix.lower() == ".sup":
        return source
    cues = [cue for cue in read_srt(source) if cue.start < duration]
    if not cues:
        raise ValueError(tr("再生範囲内に字幕がありません。 {0}", source))
    size = (1920, 1080)
    font = menu_font(48)
    palette = pgs.palette("#ffffff", "#000000")

    def pictures():
        for cue, timing in zip(cues, pgs.timeline(cues)):
            check()
            if timing is None:
                continue
            image = Image.new("RGBA", size)
            ImageDraw.Draw(image).multiline_text(
                (960, 998), cue.text, font=font, anchor="md", align="center",
                fill="white", stroke_width=3, stroke_fill="black", spacing=8,
            )
            yield timing[0], min(timing[1], duration), pgs.indexed(image.tobytes(), *size), palette

    return pgs.write_sup(str(target), pictures(), size)


def popup_entries(number, chapters, audio, subtitles):
    buttons = [(tr("トップメニュー"), "menu:page0")]
    if len(chapters) > 1:
        buttons.extend((tr("チャプター {0}", i), f"chapter:{number}:{i}") for i in range(1, len(chapters) + 1))
    if len(audio) > 1:
        buttons.extend((tr("音声 {0} · {1}", i, lang), f"audio:{i}") for i, lang in enumerate(audio, 1))
    if subtitles:
        buttons.append((tr("字幕を消す"), "subtitle:off"))
        buttons.extend((tr("字幕 {0} · {1}", i, lang), f"subtitle:{i}") for i, lang in enumerate(subtitles, 1))
    return buttons
