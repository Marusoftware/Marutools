"""Checks performed before any title encoding begins."""
from itertools import combinations
from pathlib import Path

from .menu_navigation import page_buttons, page_count
from .menu_objects import object_caption
from .project import parse_time


def issue_message(issues):
    visible = issues[:12]
    if len(issues) > len(visible):
        visible.append(f"ほか {len(issues) - len(visible)} 件")
    return "\n".join(visible)


def overlap(first, second):
    return all(max(a, b) < min(a + w, b + v)
               for a, b, w, v in zip(first.xy, second.xy, first.size, second.size))


def check_project(project):
    errors, warnings = [], []
    menu = project["menu"]
    titles = project["titles"]
    if not titles:
        errors.append("書き出す素材を追加してください。")
    targets = set()
    paths = set()
    for title in titles:
        targets.add((title["id"], None))
        paths.update(part["media"] for part in title.get("segments", []))
        paths.add(title["media"])
        for chapter in title["chapters"]:
            targets.add((title["id"], chapter["id"]))
            try:
                stamp = parse_time(chapter["time"])
                if title.get("duration_ms") is not None and stamp >= title["duration_ms"]:
                    raise ValueError("範囲外")
            except ValueError:
                errors.append(f"チャプター時刻を確認してください。 {title['name']} / {chapter['name']}")
    elements = menu.get("elements", [])
    items = menu["buttons"] + elements
    paths.update(item[field] for item in items for field in ("image", "font_file") if item.get(field))
    if menu.get("background"):
        paths.add(menu["background"])
    errors.extend(f"ファイルが見つかりません。 {path}" for path in sorted(paths) if not Path(path).is_file())
    for item in items:
        link = item.get("target")
        if "kind" in item and link is None:
            continue
        if not isinstance(link, dict) or (link.get("title"), link.get("chapter")) not in targets:
            name = object_caption(item) if "kind" in item else item.get("label", item.get("name", "ボタン"))
            errors.append(f"「{name}」のリンク先が未設定か、削除されています。")

    pages = [page_buttons(menu, page) for page in range(page_count(menu))]
    seen_overlaps = set()
    for page, buttons in enumerate(pages):
        if len(buttons) > 255:
            errors.append(f"{page + 1}ページ目のボタン数が上限の255個を超えています。")
        keys = {button.key for button in buttons}
        preferred = menu.get("initial_focus", {}).get(str(page))
        if preferred and preferred not in keys:
            warnings.append(f"{page + 1}ページ目の初期選択が見つかりません。先頭のボタンを使います。")
        for pair in combinations(buttons, 2):
            first, second = pair
            signature = (first.key, second.key)
            if signature not in seen_overlaps and overlap(first, second):
                seen_overlaps.add(signature)
                warnings.append(f"{page + 1}ページ目で操作範囲が重なっています。 「{first.caption}」 / 「{second.caption}」")
        for button in buttons:
            destinations = button.entry.get("navigation", {}).get(str(page), {})
            if any(value not in keys for value in destinations.values()):
                warnings.append(f"{page + 1}ページ目の「{button.caption}」の移動先が見つかりません。該当する方向は自動で選びます。")
    return errors, warnings
