"""Checks performed before any title encoding begins."""
from itertools import combinations
from pathlib import Path

from .l10n import tr
from .disc_tracks import LANGUAGE, read_srt
from .menu_navigation import page_buttons, page_count, target_page
from .menu_objects import object_caption
from .project import parse_time


def issue_message(issues):
    visible = issues[:12]
    if len(issues) > len(visible):
        visible.append(tr("ほか {0} 件", len(issues) - len(visible)))
    return "\n".join(visible)


def overlap(first, second):
    return all(max(a, b) < min(a + w, b + v)
               for a, b, w, v in zip(first.xy, second.xy, first.size, second.size))


def check_project(project):
    errors, warnings = [], []
    menu = project["menu"]
    titles = project["titles"]
    if not titles:
        errors.append(tr("書き出す素材を追加してください。"))
    subtitle_counts = {title["id"]: len(title.get("subtitle_tracks", [])) for title in titles}
    targets = set()
    paths = set()
    subtitle_sources = set()
    for title in titles:
        targets.add((title["id"], None))
        paths.update(part["media"] for part in title.get("segments", []))
        paths.add(title["media"])
        for track in title.get("audio_tracks", []) + title.get("subtitle_tracks", []):
            paths.add(track["path"])
            if not LANGUAGE.fullmatch(track["language"]):
                errors.append(tr("トラックの言語コードを確認してください。 {0}", track['path']))
        subtitle_sources.update(track["path"] for track in title.get("subtitle_tracks", []))
        for chapter in title["chapters"]:
            targets.add((title["id"], chapter["id"]))
            try:
                stamp = parse_time(chapter["time"])
                if title.get("duration_ms") is not None and stamp >= title["duration_ms"]:
                    raise ValueError(tr("範囲外"))
            except ValueError:
                errors.append(tr("チャプター時刻を確認してください。 {0} / {1}", title['name'], chapter['name']))
    elements = menu.get("elements", [])
    items = menu["buttons"] + elements
    count = page_count(menu)
    paths.update(item[field] for item in items for field in ("image", "font_file") if item.get(field))
    paths.update(menu[key] for key in ("background", "motion", "music") if menu.get(key))
    errors.extend(tr("ファイルが見つかりません。 {0}", path) for path in sorted(paths) if not Path(path).is_file())
    for path in sorted(subtitle_sources):
        if Path(path).suffix.lower() == ".srt" and Path(path).is_file():
            try:
                read_srt(path)
            except (ValueError, OSError) as exc:
                errors.append(tr("字幕ファイルを確認してください。 {0}", exc))
    for item in items:
        link = item.get("target")
        if "kind" in item and link is None:
            continue
        if isinstance(link, dict) and "page" in link:
            page = target_page(link)
            valid = page is not None and 0 <= page < count
        elif isinstance(link, dict) and link.get("play_all") is True:
            valid = bool(titles)
        else:
            valid = isinstance(link, dict) and (link.get("title"), link.get("chapter")) in targets
            if valid and "audio" in link:
                audio, subtitle = link["audio"], link.get("subtitle")
                valid = (type(audio) is int and audio >= 1 and type(subtitle) is int
                         and 0 <= subtitle <= subtitle_counts[link["title"]])
        if not valid:
            name = object_caption(item) if "kind" in item else item.get("label", item.get("name", tr("ボタン")))
            errors.append(tr("「{0}」のリンク先が未設定か、削除されています。", name))

    first_title = titles[0]["id"] if titles else None
    pages = [page_buttons(menu, page, first_title) for page in range(count)]
    seen_overlaps = set()
    for page, buttons in enumerate(pages):
        if len(buttons) > 255:
            errors.append(tr("{0}ページ目のボタン数が上限の255個を超えています。", page + 1))
        keys = {button.key for button in buttons}
        preferred = menu.get("initial_focus", {}).get(str(page))
        if preferred and preferred not in keys:
            warnings.append(tr("{0}ページ目の初期選択が見つかりません。先頭のボタンを使います。", page + 1))
        for pair in combinations(buttons, 2):
            first, second = pair
            signature = (first.key, second.key)
            if signature not in seen_overlaps and overlap(first, second):
                seen_overlaps.add(signature)
                warnings.append(tr("{0}ページ目で操作範囲が重なっています。 「{1}」 / 「{2}」", page + 1, first.caption, second.caption))
        for button in buttons:
            destinations = button.entry.get("navigation", {}).get(str(page), {})
            if any(value not in keys for value in destinations.values()):
                warnings.append(tr("{0}ページ目の「{1}」の移動先が見つかりません。該当する方向は自動で選びます。", page + 1, button.caption))
    return errors, warnings
