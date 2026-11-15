"""Read the primary playback path and entry marks of BDMV playlists."""
import struct
from pathlib import Path

from .l10n import tr
from .project import empty_project, make_chapter, make_title

TICKS_PER_SECOND = 45_000
TICKS_PER_MILLISECOND = TICKS_PER_SECOND // 1000


def milliseconds_at_or_after(tick):
    return (tick + TICKS_PER_MILLISECOND - 1) // TICKS_PER_MILLISECOND


def locate(path):
    folder = Path(path).expanduser().resolve()
    if folder.name.upper() == "BDMV" and folder.is_dir():
        return folder
    if folder.is_dir():
        for child in folder.iterdir():
            if child.name.upper() == "BDMV" and child.is_dir():
                return child
    raise ValueError(tr("BDMV フォルダか、その親フォルダを選択してください。"))


def inspect(path):
    root = locate(path)

    def listing(folder, extension):
        directory = root / folder
        if not directory.is_dir():
            directory = root / folder.lower()
        return sorted(str(p) for p in directory.iterdir()
                      if p.is_file() and p.suffix.lower() == extension) if directory.is_dir() else []

    playlists = listing("PLAYLIST", ".mpls")
    streams = listing("STREAM", ".m2ts")
    clpis = listing("CLIPINF", ".clpi")
    warnings = []
    if not any(p.name.lower() == "index.bdmv" for p in root.iterdir()):
        warnings.append(tr("index.bdmv が見つかりません。"))
    if not playlists:
        warnings.append(tr("MPLS が見つかりません。"))
    if not streams:
        warnings.append(tr("M2TS が見つかりません。"))
    return {"root": str(root), "playlists": playlists, "streams": streams,
            "clpi": clpis, "warnings": warnings}


def section(data, offset):
    if offset < 20 or offset + 4 > len(data):
        raise ValueError(tr("MPLS セクションの位置が不正です。"))
    length, = struct.unpack_from(">I", data, offset)
    start = offset + 4
    if start + length > len(data):
        raise ValueError(tr("MPLS セクションが途中で切れています。"))
    return data[start:start + length]


def read_playlist(path, streams, stream_folder):
    data = Path(path).read_bytes()
    if len(data) < 20 or data[:4] != b"MPLS":
        raise ValueError(tr("MPLS ヘッダーが不正です。"))
    playlist_offset, marks_offset = struct.unpack_from(">II", data, 8)
    playlist = section(data, playlist_offset)
    count, = struct.unpack_from(">H", playlist, 2)
    offset = 6
    segments = []
    elapsed = 0
    for _ in range(count):
        length, = struct.unpack_from(">H", playlist, offset)
        start = offset + 2
        offset = start + length
        if length < 20 or offset > len(playlist):
            raise ValueError(tr("MPLS の再生区間が不正です。"))
        clip = playlist[start:start + 5].decode("ascii")
        if len(clip) != 5 or not clip.isalnum() or playlist[start + 5:start + 9] != b"M2TS":
            raise ValueError(tr("MPLS のクリップ参照が不正です。"))
        in_tick, out_tick = struct.unpack_from(">II", playlist, start + 12)
        if out_tick <= in_tick:
            raise ValueError(tr("MPLS の区間終了時刻が不正です。"))
        segments.append({
            "media": streams.get(clip.upper(), str(stream_folder / (clip + ".m2ts"))),
            "in_tick": in_tick, "out_tick": out_tick, "start_tick": elapsed,
        })
        elapsed += out_tick - in_tick

    if not segments:
        raise ValueError(tr("再生区間がありません。"))

    timestamps = set()
    if marks_offset:
        marks = section(data, marks_offset)
        count, = struct.unpack_from(">H", marks)
        if len(marks) < 2 + 14 * count:
            raise ValueError(tr("MPLS のマークが途中で切れています。"))
        for offset in range(2, 2 + count * 14, 14):
            kind, index, tick = struct.unpack_from(">BHI", marks, offset + 1)
            if kind != 1 or index >= len(segments):
                continue
            segment = segments[index]
            if segment["in_tick"] <= tick < segment["out_tick"]:
                title_tick = segment["start_tick"] + tick - segment["in_tick"]
                timestamps.add(milliseconds_at_or_after(title_tick))

    chapters = [make_chapter(tr("チャプター {0}", i), time)
                for i, time in enumerate(sorted(timestamps or {0}), 1)]
    title = make_title(Path(path).stem, segments[0]["media"], chapters)
    title.update(playlist=path, segments=segments, duration_ms=milliseconds_at_or_after(elapsed))
    return title


def import_as_project(path):
    inventory = inspect(path)
    root = Path(inventory["root"])
    streams = {Path(path).stem.upper(): path for path in inventory["streams"]}
    stream_folder = Path(inventory["streams"][0]).parent if streams else root / "STREAM"
    project = empty_project()
    project["name"] = root.parent.name
    project["source_bdmv"] = str(root)
    project["bdmv_inventory"] = inventory
    for path in inventory["playlists"]:
        try:
            title = read_playlist(path, streams, stream_folder)
        except (OSError, ValueError, struct.error) as exc:
            inventory["warnings"].append(f"{Path(path).name}: {exc}")
            continue
        missing = {Path(segment["media"]).name for segment in title["segments"]
                   if not Path(segment["media"]).is_file()}
        if missing:
            inventory["warnings"].append(tr("{0}: 素材なし ({1})", Path(path).name, ', '.join(sorted(missing))))
        project["titles"].append(title)
    return project
