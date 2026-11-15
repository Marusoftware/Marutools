"""Geometry and remote-control navigation shared by authoring and preview."""
from dataclasses import dataclass

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
    return button.get("label", button.get("name", "ボタン"))


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


def page_count(menu):
    return max(1, (len(menu["buttons"]) + BUTTONS_PER_PAGE - 1) // BUTTONS_PER_PAGE)


def page_buttons(menu, page, first_title=None):
    items = []
    start = page * BUTTONS_PER_PAGE
    for index, entry in enumerate(menu["buttons"][start:start + BUTTONS_PER_PAGE]):
        default, size = button_geometry(entry, index)
        items.append(MenuItem(f"button{index}", entry.get("id", f"legacy-{start + index}"),
                              entry, position(entry, default, size), size, entry.get("target")))
    for index, entry in enumerate(menu.get("elements", [])):
        if entry.get("target"):
            tag = f"element{index}"
            default, size = element_geometry(entry, index)
            items.append(MenuItem(tag, entry.get("id", tag), entry, position(entry, default, size),
                                  size, entry["target"]))
    if not items and first_title:
        entry = {"label": "再生"}
        xy, size = button_geometry(entry, 0)
        items.append(MenuItem("default-play", "default-play", entry, xy, size, {"title": first_title}))
    if page:
        items.append(MenuItem("previous-page", "previous-page", {"label": "前へ"}, (2, 2), (65, 27),
                              next_page=page - 1))
    if page + 1 < page_count(menu):
        items.append(MenuItem("next-page", "next-page", {"label": "次へ"}, (WIDTH - 67, 2), (65, 27),
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
