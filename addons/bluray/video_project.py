"""Reference a saved Video timeline and resolve its original media at export."""
from copy import deepcopy
from pathlib import Path

from .l10n import tr


def is_video_project(title):
    return Path(title["media"]).suffix.lower() == ".maruvideo"


def load_timeline(title):
    try:
        from addons.video.project import duration, load
    except ImportError as exc:
        raise ValueError(tr("この素材を使うには Video アドオンもインストールしてください。")) from exc

    project = title.get("_timeline")
    if project is None:
        project = load(title["media"])
    if not duration(project):
        raise ValueError(tr("Video プロジェクトのタイムラインにクリップがありません。"))
    return project


def timeline_duration(title):
    project = load_timeline(title)
    from addons.video.project import duration

    return duration(project)


def timeline_files(project):
    return sorted({project["assets"][clip["asset"]]["path"] for clip in project["clips"]})


def prepare_project(project):
    """Freeze the saved timelines for one authoring job without changing the editor."""
    result = deepcopy(project)
    for title in result["titles"]:
        if is_video_project(title):
            title["_timeline"] = load_timeline(title)
            title["duration_ms"] = timeline_duration(title)
    return result
