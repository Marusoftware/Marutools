"""Run FFmpeg without blocking the editor's Tk event loop."""
from copy import deepcopy
from queue import Empty, SimpleQueue
from threading import Thread

from addons.bluray.export import ExportCancellation, ExportCancelled

from .render import render


def render_with_progress(parent, translate, project, target, *, size, proxy):
    from tkinter.ttk import Progressbar

    window = parent.makeSubWindow(dialog=True)
    caption = translate("Preparing Timeline Preview…" if proxy else "Export MP4…")
    window.changeTitle(caption)
    label = window.Label(label=caption)
    label.configure(wraplength=0)
    label.pack(fill="x", padx=12, pady=(12, 4))
    bar = Progressbar(window.root, maximum=100, length=360)
    bar.pack(fill="x", padx=12, pady=4)
    events = SimpleQueue()
    cancellation = ExportCancellation()
    snapshot = deepcopy(project)
    complete = False
    error = None

    def cancel():
        label.configure(label=translate("Cancelling…"))
        button.configure(state="disabled")
        cancellation.cancel()

    def worker():
        try:
            render(snapshot, target, size=size, proxy=proxy, progress=lambda value: events.put(("progress", value)),
                   cancellation=cancellation)
        except ExportCancelled:
            events.put(("cancelled", None))
        except Exception as exc:
            events.put(("error", translate(str(exc))))
        else:
            events.put(("done", None))

    def poll():
        nonlocal complete, error
        while True:
            try:
                event, value = events.get_nowait()
            except Empty:
                bar.after(60, poll)
                return
            if event == "progress":
                if value is not None:
                    bar.configure(value=value)
                continue
            complete = event == "done"
            if event == "error":
                error = value
            window.close()
            return

    button = window.Input.Button(label=translate("Cancel"), command=cancel)
    button.pack(anchor="e", padx=12, pady=(4, 12))
    window.setcallback("close", cancel)
    Thread(target=worker, daemon=True, name="Video render").start()
    bar.after(60, poll)
    window.wait()
    if error:
        parent.Dialog.error(title=caption, message=error)
    return complete
