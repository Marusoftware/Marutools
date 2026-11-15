"""Reuse complete Blu-ray title encodes across export runs."""
import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .assets import media_kind

# Increment when title preprocessing, resolution, codecs or encoding options change.
CACHE_VERSION = 2


def file_stamp(path):
    source = Path(path).resolve()
    info = source.stat()
    return [str(source), info.st_size, info.st_mtime_ns, info.st_ctime_ns,
            info.st_dev, info.st_ino]


def clip_key(title, chapters, encoding="libx264"):
    segments = title.get("segments")
    if segments:
        source = [[file_stamp(part["media"]), part["in_tick"], part["out_tick"]] for part in segments]
    else:
        source = file_stamp(title["media"])
    identity = [CACHE_VERSION, media_kind(title), source, chapters]
    identity.extend([[file_stamp(track["path"]) for track in title.get(key, [])]
                     for key in ("audio_tracks", "subtitle_tracks")])
    if encoding != "libx264":
        identity.append(encoding)
    return hashlib.sha256(json.dumps(identity, ensure_ascii=True).encode("ascii")).hexdigest()


def copy_clip(source, destination, check):
    with open(source, "rb") as stream:
        while True:
            check()
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            destination.write(chunk)


def restore_clip(cached, clip, check):
    try:
        size = cached.stat().st_size
    except FileNotFoundError:
        return False
    # M2TS packets include a four-byte timestamp before the TS packet.
    if not size or size % 192:
        return False
    try:
        with clip.open("wb") as destination:
            copy_clip(cached, destination, check)
    except FileNotFoundError:
        clip.unlink(missing_ok=True)
        return False
    return True


def store_clip(clip, cached, check):
    cached.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with NamedTemporaryFile(dir=cached.parent, prefix=".partial-", delete=False) as destination:
            temp = Path(destination.name)
            copy_clip(clip, destination, check)
        check()
        os.replace(temp, cached)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
