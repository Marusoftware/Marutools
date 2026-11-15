"""Resolve addon messages using the language of the Marutools editor."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache, wraps
import json
from pathlib import Path
import re

_language = ContextVar("bluray_language", default="ja")


def host_language(api):
    app = getattr(api, "app", None)
    language = getattr(getattr(app, "lang", None), "lang", None)
    if not language:
        config = getattr(app, "config", None)
        if config is not None and "lang" in config:
            language = config["lang"]
    return language or "ja"


@contextmanager
def use_language(locale):
    token = _language.set(locale)
    try:
        yield
    finally:
        _language.reset(token)


def localized(callback):
    """Preserve the current locale for Tk callbacks and export threads."""
    locale = _language.get()

    @wraps(callback)
    def run(*args, **kwargs):
        with use_language(locale):
            return callback(*args, **kwargs)

    return run


def editor_language(method):
    """Use the editor's locale at entry points called by the host."""
    @wraps(method)
    def run(editor, *args, **kwargs):
        with use_language(editor.locale):
            return method(editor, *args, **kwargs)

    return run


@lru_cache
def catalog(locale):
    if not re.fullmatch(r"[A-Za-z0-9_]+", locale):
        return {}
    path = Path(__file__).with_name(f"{locale}.json")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def tr(message, *args):
    locale = _language.get().replace("-", "_")
    base = locale.split("_", 1)[0].lower()
    if base != "ja":
        message = catalog(locale).get(message) or catalog(base).get(message) or catalog("en").get(message, message)
    return message.format(*args) if args else message
