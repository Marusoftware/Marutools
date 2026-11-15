"""Menu object labels, geometry and embedded video stills."""
from base64 import b64decode, b64encode
from functools import lru_cache
from io import BytesIO
import os
import re
import shutil
from pathlib import Path
import subprocess

from .l10n import tr
from .preview import playback_source

SHAPES = {"長方形": "rectangle", "楕円": "ellipse"}
OBJECT_LABELS = {"shape": "図形", "image": "画像", "text": "テキスト"}
SHOW_VIDEO_TITLE = "動画タイトルを表示"
VIDEO_TITLE_OPTIONS = ("表示しない", "表示する")


def object_caption(item):
    if item["kind"] == "image":
        return item.get("thumbnail_name") or Path(item["image"]).name
    if item["kind"] == "shape":
        return tr(next((name for name, kind in SHAPES.items() if kind == item.get("shape")), "長方形"))
    return item["text"]


def open_object_image(item):
    from PIL import Image

    if item.get("thumbnail"):
        return Image.open(BytesIO(b64decode(item["thumbnail"], validate=True)))
    return Image.open(item["image"])


def fit_object_image(item, size, *, scale=1):
    """Fit the image in editor coordinates, then render at the output scale."""
    from PIL import Image, ImageOps

    with open_object_image(item) as source:
        image = ImageOps.exif_transpose(source).convert("RGBA")
        width, height = image.size
        ratio = min(size[0] / width, size[1] / height)
        dimensions = tuple(max(1, round(length * ratio)) * scale for length in image.size)
        return image.resize(dimensions, Image.Resampling.LANCZOS)


def render_object_image(item, size, title_names=None, *, scale=1):
    if not (item.get("thumbnail") and item.get("show_video_title")) or size[1] < 2:
        return fit_object_image(item, size, scale=scale)

    from PIL import Image, ImageDraw

    saved_name = item.get("thumbnail_name", "").rsplit(" · ", 1)[0]
    title = (title_names or {}).get(item.get("thumbnail_source"), saved_name)
    title = " ".join(title.split())
    if not title:
        return fit_object_image(item, size, scale=scale)

    width, height = size
    strip = max(1, min(22, height // 3))
    picture = fit_object_image(item, (width, max(1, height - strip)), scale=scale)
    width *= scale
    strip *= scale
    result = Image.new("RGBA", (width, picture.height + strip))
    result.alpha_composite(picture, ((width - picture.width) // 2, 0))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, picture.height, width - 1, result.height - 1), fill="#252a33")
    font = menu_font(max(1, min(14, strip // scale - 3)) * scale)
    available = max(0, width - 8 * scale)
    if draw.textlength(title, font=font) > available:
        while title and draw.textlength(title + "…", font=font) > available:
            title = title[:-1]
        title = title + "…" if draw.textlength("…", font=font) <= available else ""
    draw.text((width // 2, picture.height + strip // 2), title, anchor="mm", font=font, fill="#ffffff")
    return result


def capture_thumbnail(title, milliseconds):
    path, seconds, segment = playback_source(title, milliseconds)
    if segment:
        import av

        with av.open(path) as container:
            stream = container.streams.video[0]
            seconds -= float((stream.start_time or 0) * stream.time_base)
    try:
        frame = subprocess.run(
            ["ffmpeg", "-v", "error", "-nostdin", "-ss", str(max(0, seconds)), "-i", path,
             "-map", "0:v:0", "-frames:v", "1", "-vf",
             "scale=392:220:force_original_aspect_ratio=decrease", "-c:v", "png",
             "-f", "image2pipe", "pipe:1"],
            capture_output=True, timeout=20, check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(tr("動画から画像を取り出せませんでした。FFmpeg と素材を確認してください。")) from exc
    if not frame:
        raise ValueError(tr("指定時刻にフレームがありません。時刻を少し前にしてください。"))
    return b64encode(frame).decode("ascii")


def valid_color(value):
    return re.fullmatch(r"#[0-9a-fA-F]{6}", value) is not None


@lru_cache(maxsize=32)
def menu_font(size, path=None):
    from PIL import ImageFont

    if path:
        return ImageFont.truetype(path, size)
    if shutil.which("fc-match"):
        result = subprocess.run(["fc-match", "-f", "%{file}", ":lang=ja"], capture_output=True)
        if result.returncode == 0 and result.stdout:
            return ImageFont.truetype(os.fsdecode(result.stdout), size)
    for path in ("YuGothM.ttc", "meiryo.ttc", "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def render_text(entry, size, *, scale=1, background="#252a33", foreground="#ffffff"):
    from PIL import Image, ImageDraw

    width, height = (value * scale for value in size)
    image = Image.new("RGBA", (width, height), entry.get("fill", background))
    draw = ImageDraw.Draw(image)
    pixels = entry.get("font_size", 12) * scale
    font = menu_font(pixels, entry.get("font_file"))
    left, top = 8 * scale, 6 * scale
    for paragraph in entry["text"].splitlines():
        line = ""
        for char in paragraph:
            if line and draw.textlength(line + char, font=font) > width - 2 * left:
                draw.text((left, top), line, font=font, fill=entry.get("foreground", foreground), anchor="lt")
                top += max(1, int(pixels * 1.25))
                line = ""
            if top >= height:
                return image
            line += char
        if top >= height:
            break
        draw.text((left, top), line, font=font, fill=entry.get("foreground", foreground), anchor="lt")
        top += max(1, int(pixels * 1.25))
    return image
