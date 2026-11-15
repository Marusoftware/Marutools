"""Settings and progress for the background disc export."""
from copy import deepcopy
from pathlib import Path
from queue import Empty, SimpleQueue
from threading import Thread

from .export import ExportCancellation, ExportCancelled, available_encoders, check_tools, export_disc
from .preflight import check_project, issue_message


def export_target(parent, name, *, iso=False):
    if not parent or not Path(parent).is_dir():
        raise ValueError("書き出し先の親フォルダを選んでください。")
    if not name or name in (".", "..") or any(char in name for char in '/\\:*?"<>|'):
        raise ValueError("出力名を確認してください。")
    if iso and not name.lower().endswith(".iso"):
        name += ".iso"
    target = Path(parent).absolute() / name
    if target.exists():
        raise ValueError("その名前のフォルダまたはファイルが既にあります。")
    return target


def show_export_dialog(ui, project, project_path, stop_preview, report):
    from tkinter import BooleanVar, StringVar
    from tkinter.ttk import Checkbutton, Combobox, Label, Progressbar

    window = ui.makeSubWindow(dialog=True)
    window.changeTitle("Blu-ray 書き出し設定")
    settings = window.Frame()
    settings.pack(fill="x", padx=12, pady=(12, 4))

    def field(label, default):
        row = settings.Frame()
        row.pack(fill="x", pady=(4, 2))
        # api.ui.Label derives its wrap width before the frame is mapped.
        Label(row.widget, text=label).pack(fill="x", pady=(0, 2))
        inputs = row.Frame()
        inputs.pack(fill="x")
        entry = inputs.Input.Form(width=46)
        entry.set(default)
        entry.pack(side="left", fill="x", expand=True)
        return inputs, entry

    path_row, parent = field("書き出し先の親フォルダ", str(Path(project_path).absolute().parent) if project_path else "")

    def browse():
        path = window.Dialog.askdir(title="書き出し先の親フォルダを選択")
        if path:
            parent.set(path)

    browse_button = path_row.Input.Button(label="参照…", command=browse, width=0)
    browse_button.pack(side="left", padx=(6, 0))
    _, name = field("出力名", "Blu-ray")
    formats = ("BDMV フォルダ", "Blu-ray ISO（UDF 2.50）")
    output_format = StringVar(master=settings.widget, value=formats[0])
    Label(settings.widget, text="出力形式").pack(fill="x", pady=(4, 2))
    format_picker = Combobox(settings.widget, state="readonly", textvariable=output_format, values=formats)
    format_picker.pack(fill="x")
    encoders = available_encoders()
    default_encoder = next(iter(encoders), "")
    encoder_var = StringVar(master=settings.widget, value=default_encoder)
    Label(settings.widget, text="映像エンコーダー").pack(fill="x", pady=(4, 2))
    encoder_picker = Combobox(settings.widget, state="readonly", textvariable=encoder_var, values=list(encoders))
    encoder_picker.pack(fill="x")
    _, device = field("VAAPI デバイス", "/dev/dri/renderD128")

    def show_device(event=None):
        device.configure(state="normal" if encoders.get(encoder_var.get()) == "h264_vaapi" else "disabled")

    encoder_picker.bind("<<ComboboxSelected>>", show_device)
    show_device()
    cache_enabled = BooleanVar(master=settings.widget, value=True)
    cache_button = Checkbutton(settings.widget, text="変換済み素材を再利用", variable=cache_enabled)
    cache_button.pack(anchor="w", pady=(6, 0))
    progress_area = window.Frame()
    progress_area.pack(fill="x", padx=12, pady=(4, 0))
    status = Label(progress_area.widget, text="", wraplength=380)
    status.pack(fill="x", pady=4)
    status.bind("<Configure>", lambda event: status.configure(wraplength=max(1, event.width)), add="+")
    bar = Progressbar(progress_area.widget, mode="determinate", maximum=100)
    bar.pack(fill="x", pady=(0, 6))
    actions = window.Frame()
    actions.pack(fill="x", padx=12, pady=(4, 12))
    events = SimpleQueue()
    running = False
    cancellation = None

    def display(message, percent):
        if percent is None:
            if str(bar.cget("mode")) != "indeterminate":
                bar.configure(mode="indeterminate")
                bar.start(50)
            status.configure(text=message)
        else:
            if str(bar.cget("mode")) != "determinate":
                bar.stop()
                bar.configure(mode="determinate")
            bar.configure(value=percent)
            status.configure(text=f"{message}  {percent}%")

    def poll():
        nonlocal running
        latest = None
        while True:
            try:
                event, message, percent = events.get_nowait()
            except Empty:
                break
            if event == "progress":
                if not cancellation.requested.is_set():
                    latest = (message, percent)
                continue
            running = False
            for widget in (parent, name, browse_button, cache_button, start_button, close_button):
                widget.configure(state="normal")
            format_picker.configure(state="readonly")
            encoder_picker.configure(state="readonly")
            show_device()
            cancel_button.configure(state="disabled")
            if event == "error":
                display("書き出しに失敗しました。", 0)
                report("BDMV の書き出しに失敗しました。")
                window.Dialog.error(title="BDMV の書き出し", message=message)
            elif event == "cancelled":
                display("書き出しを中止しました。", 0)
                report("BDMV の書き出しを中止しました。")
            else:
                display(f"書き出しが完了しました。\n{message}", 100)
                report(f"BDMV を書き出しました。 {message}")
            return
        if latest is not None:
            display(*latest)
        bar.after(100, poll)

    def start():
        nonlocal running, cancellation
        iso = output_format.get() == formats[1]
        encoder = encoders.get(encoder_var.get())
        vaapi_device = device.value.strip()
        try:
            target = export_target(parent.value.strip(), name.value.strip(), iso=iso)
            check_tools(iso=iso)
            if encoder is None:
                raise ValueError("使用できる H.264 エンコーダーがありません。")
            if encoder == "h264_vaapi" and not vaapi_device:
                raise ValueError("VAAPI デバイスを指定してください。")
        except (ValueError, RuntimeError) as exc:
            window.Dialog.error(title="書き出し設定", message=str(exc))
            return
        errors, warnings = check_project(project)
        if errors:
            window.Dialog.error(title="書き出し前チェック", message=issue_message(errors))
            return
        if warnings and not window.Dialog.question(
            "yesno", "書き出し前チェック", issue_message(warnings) + "\n\n書き出しを続けますか？",
        ):
            return
        snapshot = deepcopy(project)
        cancellation = ExportCancellation()
        cache_parent = Path(project_path).absolute().parent if project_path else target.parent
        cache_dir = cache_parent / ".marubd-cache" if cache_enabled.get() else None

        def run():
            try:
                export_disc(snapshot, target, lambda message, percent: events.put(("progress", message, percent)),
                            cancellation, cache_dir=cache_dir, iso=iso, encoder=encoder, vaapi_device=vaapi_device)
            except ExportCancelled:
                events.put(("cancelled", "", None))
            except Exception as exc:
                events.put(("error", str(exc), None))
            else:
                events.put(("done", str(target), 100))

        stop_preview()
        running = True
        for widget in (parent, name, browse_button, cache_button, start_button, close_button):
            widget.configure(state="disabled")
        format_picker.configure(state="disabled")
        encoder_picker.configure(state="disabled")
        device.configure(state="disabled")
        cancel_button.configure(state="normal")
        display("BDMV の書き出しを準備中…", None)
        Thread(target=run, name="Blu-ray export").start()
        bar.after(100, poll)

    def close():
        if not running:
            window.close()

    def cancel():
        if running and not cancellation.requested.is_set():
            cancel_button.configure(state="disabled")
            display("中止処理中…", None)
            cancellation.cancel()

    close_button = actions.Input.Button(label="閉じる", command=close)
    close_button.pack(side="right", padx=(4, 0))
    start_button = actions.Input.Button(label="書き出し", command=start)
    start_button.pack(side="right")
    cancel_button = actions.Input.Button(label="中止", command=cancel, state="disabled")
    cancel_button.pack(side="right", padx=(0, 4))
    window.setcallback("close", close)
    window.wait()
