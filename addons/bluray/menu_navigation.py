"""Geometry and remote-control navigation shared by authoring and preview."""
from dataclasses import dataclass

from .l10n import tr
from .menu_objects import object_caption

WIDTH, HEIGHT = 640, 360
BUTTONS_PER_PAGE = 4
UNLINKED = "リンク未設定"
DIRECTIONS = ("up", "down", "left", "right")


def clamp_position(x, y, size):
    return max(0, min(WIDTH - size[0], x)), max(0, min(HEIGHT - size[1], y))


def element_geometry(entry, index):
    return (350 + index % 4 * 16, 36 + index % 10 * 22), (
        tuple(entry.get("size", {"image": (196, 110), "shape": (130, 72), "text": (224, 56)}[entry["kind"]]))
    )


def button_geometry(entry, index):
    if entry.get("image"):
        return (32 + index * 148, 140), (140, 110)
    return (48, 129 + index * 48), (304, 46)


def position(entry, default, size):
    saved = entry.get("position")
    if isinstance(saved, dict):
        x, y = saved.get("x"), saved.get("y")
        if type(x) is int and type(y) is int:
            return clamp_position(x, y, size)
    return clamp_position(*default, size)


def button_caption(button):
    return button.get("label", button.get("name", tr("ボタン")))


def target_page(link):
    page = link.get("page") if isinstance(link, dict) else None
    return page if type(page) is int else None


@dataclass
class MenuItem:
    tag: str
    key: str
    entry: dict
    xy: tuple
    size: tuple
    target: dict = None
    next_page: int = None

    @property
    def caption(self):
        return object_caption(self.entry) if "kind" in self.entry else button_caption(self.entry)

    @property
    def centre(self):
        return tuple(start + length / 2 for start, length in zip(self.xy, self.size))

    @property
    def destination_page(self):
        return self.next_page if self.next_page is not None else target_page(self.target)


def page_count(menu):
    legacy_pages = (len(menu["buttons"]) + BUTTONS_PER_PAGE - 1) // BUTTONS_PER_PAGE
    return max(1, legacy_pages, menu.get("page_count", 1))


def page_elements(menu, page):
    # Older projects did not scope objects to a specific page.
    return [(index, item) for index, item in enumerate(menu.get("elements", []))
            if item.get("page") in (None, page)]


def remove_menu_page(menu, page):
    count = page_count(menu)
    if count <= 1 or not 0 <= page < count:
        return

    new_count = count - 1
    page_numbers = {str(index): index - (index > page) for index in range(count) if index != page}
    remapped_keys = {}
    for group, prefix in (("buttons", "legacy-"), ("elements", "element")):
        remaining = []
        for index, entry in enumerate(menu[group]):
            visible_page = index // BUTTONS_PER_PAGE if group == "buttons" else entry.get("page")
            key = entry.get("id", f"{prefix}{index}")
            if visible_page == page:
                remapped_keys[key] = None
                continue

            new_index = len(remaining)
            if group == "elements":
                if visible_page is not None and visible_page > page:
                    entry["page"] -= 1
                if new_index != index and "position" not in entry:
                    default, size = element_geometry(entry, index)
                    x, y = position(entry, default, size)
                    entry["position"] = {"x": x, "y": y}
            if "id" not in entry and new_index != index:
                remapped_keys[key] = f"{prefix}{new_index}"
            destination = target_page(entry.get("target"))
            if destination == page:
                entry["target"] = None
            elif destination is not None and page < destination < count:
                entry["target"] = {"page": destination - 1}
            remaining.append(entry)
        menu[group] = remaining

    menu["page_count"] = new_count

    def move_target(key, page):
        if (page == 0 and key == "previous-page") or (page == new_count - 1 and key == "next-page"):
            return None
        return remapped_keys.get(key, key)

    if "initial_focus" in menu:
        menu["initial_focus"] = {
            str(page_numbers[old]): key for old, target in menu["initial_focus"].items()
            if old in page_numbers and (key := move_target(target, page_numbers[old])) is not None
        }
    for entry in menu["buttons"] + menu["elements"]:
        if "navigation" not in entry:
            continue
        page_moves = {}
        for old, moves in entry["navigation"].items():
            if old not in page_numbers:
                continue
            new_page = page_numbers[old]
            updated = {direction: key for direction, target in moves.items()
                       if (key := move_target(target, new_page)) is not None}
            if updated:
                page_moves[str(new_page)] = updated
        entry["navigation"] = page_moves


def page_buttons(menu, page, first_title=None):
    items = []
    start = page * BUTTONS_PER_PAGE
    for index, entry in enumerate(menu["buttons"][start:start + BUTTONS_PER_PAGE]):
        default, size = button_geometry(entry, index)
        items.append(MenuItem(f"button{index}", entry.get("id", f"legacy-{start + index}"),
                              entry, position(entry, default, size), size, entry.get("target")))
    for index, entry in page_elements(menu, page):
        if entry.get("target"):
            tag = f"element{index}"
            default, size = element_geometry(entry, index)
            items.append(MenuItem(tag, entry.get("id", tag), entry, position(entry, default, size),
                                  size, entry["target"]))
    if not items and first_title and page == 0:
        entry = {"label": tr("再生")}
        xy, size = button_geometry(entry, 0)
        items.append(MenuItem("default-play", "default-play", entry, xy, size, {"title": first_title}))
    if not menu.get("auto_page_buttons", True):
        if page and not items:
            return [MenuItem("top-page", "top-page", {"label": tr("トップメニュー")}, (240, 322), (160, 28),
                             next_page=0)]
        return items
    if page:
        items.append(MenuItem("previous-page", "previous-page", {"label": tr("前へ")}, (2, 2), (65, 27),
                              next_page=page - 1))
    if page + 1 < page_count(menu):
        items.append(MenuItem("next-page", "next-page", {"label": tr("次へ")}, (WIDTH - 67, 2), (65, 27),
                              next_page=page + 1))
    return items


def initial_focus(menu, page, items):
    preferred = menu.get("initial_focus", {}).get(str(page))
    return next((item.key for item in items if item.key == preferred), items[0].key if items else None)


def navigation(items, page):
    keys = {item.key for item in items}
    output = {}
    for item in items:
        x, y = item.centre
        overrides = item.entry.get("navigation", {}).get(str(page), {})
        moves = {}
        for direction in DIRECTIONS:
            if overrides.get(direction) in keys:
                moves[direction] = overrides[direction]
                continue
            nearest, best = item.key, float("inf")
            for other in items:
                ox, oy = other.centre
                dx, dy = ox - x, oy - y
                along, across = {"up": (-dy, dx), "down": (dy, dx), "left": (-dx, dy), "right": (dx, dy)}[direction]
                score = along + 2 * abs(across)
                if along > 0 and score < best:
                    nearest, best = other.key, score
            moves[direction] = nearest
        output[item.key] = moves
    return output
