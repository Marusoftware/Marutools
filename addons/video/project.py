"""Non-destructive timeline and portable project files."""
from copy import deepcopy
import json
from math import isfinite
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile
from uuid import uuid4

FORMAT = "marutools-video"
EXTENSION = ".maruvideo"
TRACKS = ("V2", "V1", "A1", "A2")
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}
IMAGE_DURATION = 5000


def empty_project():
    return {"format": FORMAT, "version": 1, "assets": {}, "clips": []}


def length(clip):
    return clip["out"] - clip["in"]


def end(clip):
    return clip["start"] + length(clip)


def duration(project):
    return max((end(clip) for clip in project["clips"]), default=0)


def inspect_asset(path):
    path = str(Path(path).resolve(strict=True))
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path],
            capture_output=True, text=True, check=True, timeout=12,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError(exc.stderr.strip() or "Could not read the media.") from exc
    data = json.loads(probe.stdout)
    streams = data["streams"]
    video = next((stream["index"] for stream in streams
                  if stream["codec_type"] == "video" and not stream.get("disposition", {}).get("attached_pic")), None)
    audio = next((stream["index"] for stream in streams if stream["codec_type"] == "audio"), None)
    still = Path(path).suffix.lower() in IMAGE_TYPES and video is not None
    milliseconds = IMAGE_DURATION if still else 0
    if not still:
        # Use the container duration, with stream durations as a fallback.
        for item in (data.get("format", {}), *streams):
            try:
                seconds = float(item.get("duration", 0))
            except (TypeError, ValueError):
                continue
            if isfinite(seconds) and seconds > 0:
                milliseconds = max(1, round(seconds * 1000))
                break
    if (video is None and audio is None) or not milliseconds:
        raise ValueError("Could not determine a playable video, image or audio duration.")
    return {"path": path, "duration": milliseconds, "video": video, "audio": audio, "still": still}


def accepts(asset, track):
    if track not in TRACKS:
        return False
    stream = "video" if track.startswith("V") else "audio"
    return asset[stream] is not None


def validate_clip(project, clip):
    asset = project["assets"][clip["asset"]]
    track = clip["track"]
    if not accepts(asset, track):
        raise ValueError("This media does not have a stream for the selected track.")
    if not 0 <= clip["in"] < clip["out"] <= asset["duration"] or clip["start"] < 0:
        raise ValueError("The clip is outside the source or timeline range.")
    if any(other["track"] == track and other["id"] != clip["id"]
           and max(clip["start"], other["start"]) < min(end(clip), end(other)) for other in project["clips"]):
        raise ValueError("Clips cannot overlap on the same track.")


def add_clip(project, asset_id, track, start):
    asset = project["assets"][asset_id]
    clip = {"id": uuid4().hex, "asset": asset_id, "track": track,
            "start": start, "in": 0, "out": asset["duration"], "muted": False}
    validate_clip(project, clip)
    project["clips"].append(clip)
    return clip


def split_clip(project, clip, position):
    if not clip["start"] < position < end(clip):
        raise ValueError("Move the playhead inside the selected clip.")
    source_time = clip["in"] + position - clip["start"]
    right = {**clip, "id": uuid4().hex, "start": position, "in": source_time}
    clip["out"] = source_time
    project["clips"].append(right)
    return right


def load(path):
    project = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(project, dict) or project.get("format") != FORMAT or project.get("version") != 1:
        raise ValueError("This is not a supported Marutools Video project.")
    assets, clips = project["assets"], project["clips"]
    if not isinstance(assets, dict) or not isinstance(clips, list):
        raise ValueError("Invalid project structure.")
    parent = Path(path).resolve().parent
    for asset in assets.values():
        if (not isinstance(asset["path"], str) or not asset["path"] or type(asset["duration"]) is not int
                or asset["duration"] <= 0 or type(asset["still"]) is not bool
                or any(asset[key] is not None and (type(asset[key]) is not int or asset[key] < 0)
                       for key in ("video", "audio"))):
            raise ValueError("Invalid asset in project.")
        asset["path"] = os.path.abspath(parent / asset["path"])
    ids = set()
    for clip in clips:
        if (not isinstance(clip["id"], str) or not clip["id"] or clip["id"] in ids
                or any(type(clip[key]) is not int for key in ("start", "in", "out"))
                or type(clip["muted"]) is not bool):
            raise ValueError("Invalid clip in project.")
        ids.add(clip["id"])
        validate_clip(project, clip)
    return project


def save(path, project):
    path = Path(path).absolute()
    copy = deepcopy(project)
    for asset in copy["assets"].values():
        try:
            asset["path"] = os.path.relpath(asset["path"], path.parent)
        except ValueError:
            pass  # Different Windows drives require an absolute path.
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".tmp", prefix=".maruvideo-",
                                dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(copy, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
