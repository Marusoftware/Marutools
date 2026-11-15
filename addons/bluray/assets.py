"""Media types and metadata for the project asset list."""
from pathlib import Path

IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff")
AUDIO_TYPES = (".wav", ".mp3", ".flac", ".aac", ".m4a", ".ogg", ".opus", ".wma", ".aiff")
VIDEO_TYPES = (".mp4", ".mkv", ".mov", ".m2ts", ".mts", ".ts", ".avi", ".webm", ".mpg", ".mpeg", ".wmv", ".m4v")
MEDIA_LABELS = {"video": "動画", "audio": "音声", "image": "画像"}


def file_pattern(suffixes):
    return " ".join("*" + ext for ext in suffixes)


def media_kind(title):
    return title.get("kind", "video")


def path_kind(path):
    suffix = Path(path).suffix.lower()
    if suffix in IMAGE_TYPES:
        return "image"
    if suffix in AUDIO_TYPES:
        return "audio"
    return "video"


def media_duration(path):
    try:
        import av
        with av.open(path) as container:
            if container.duration:
                return container.duration * 1000 // av.time_base
    except (ImportError, OSError, RuntimeError, ValueError):
        pass
    return None
