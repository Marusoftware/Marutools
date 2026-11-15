"""Optional Tk video surface and tkmedia playback adapter."""
import os
from importlib import import_module
from inspect import signature
from math import ceil
from queue import Empty, SimpleQueue
from threading import Thread
from time import monotonic

from .l10n import localized, tr
from .assets import media_kind
from .bdmv import TICKS_PER_SECOND
from .ui_support import tk_theme_colors

PREVIEW_BORDER = 1


def preview_size(width, height):
    return max(1, width - 2 * PREVIEW_BORDER), max(1, height - 2 * PREVIEW_BORDER)


class AudioOutputUnavailable(RuntimeError):
    pass


def playback_source(title, milliseconds):
    """Map a title-relative time to its clip and playlist clock position."""
    segments = title.get("segments")
    if not segments:
        return title["media"], milliseconds / 1000, None
    tick = milliseconds * TICKS_PER_SECOND // 1000
    for segment in segments:
        offset = tick - segment["start_tick"]
        if 0 <= offset < segment["out_tick"] - segment["in_tick"]:
            return segment["media"], (segment["in_tick"] + offset) / TICKS_PER_SECOND, segment
    raise ValueError(tr("この時刻はタイトルの再生範囲外です。"))


class PlaybackSurface:
    """Scope tkmedia's scheduled draws to the playback that owns them."""

    def __init__(self, widget, is_current, on_closed_image):
        self.widget = widget
        self.is_current = is_current
        self.on_closed_image = on_closed_image
        self.active = True
        self.fit_frames = True
        self.fitted = None

    def __getattr__(self, name):
        return getattr(self.widget, name)

    def __str__(self):
        return str(self.widget)

    def configure(self, cnf=None, **options):
        if isinstance(cnf, dict):
            options = {**cnf, **options}
            cnf = None
        image = options.get("image")
        if self.fit_frames and image and hasattr(image, "width") and hasattr(image, "height"):
            width, height = preview_size(self.widget.winfo_width(), self.widget.winfo_height())
            if width > 1 and height > 1:
                step = max(ceil(image.width() / width), ceil(image.height() / height))
                if step > 1:
                    return self.configure_fitted(cnf, options, image, step)
        result = self.widget.configure(cnf, **options)
        if "image" in options:
            self.fitted = None
        return result

    config = configure

    def configure_fitted(self, cnf, options, image, step):
        from tkinter import PhotoImage

        # Copy within Tk. Avoid reading a full-size frame back into Pillow
        # and uploading a second image on every draw.
        previous = self.fitted
        if previous is None:
            self.fitted = PhotoImage(master=self.widget)
        self.widget.tk.call(str(self.fitted), "copy", str(image), "-subsample", step, step,
                            "-shrink", "-compositingrule", "set")
        if previous is not None and len(options) == 1 and cnf is None:
            return None
        options["image"] = self.fitted
        return self.widget.configure(cnf, **options)

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    def after(self, delay, callback=None, *args):
        if callback is None:
            return self.widget.after(delay)

        def draw():
            if not self.active or not self.is_current():
                return
            try:
                callback(*args)
            except ValueError as exc:
                if str(exc) != "Operation on closed image":
                    raise
                if self.active and self.is_current():
                    self.on_closed_image()

        return self.widget.after(delay, localized(draw))


class Preview:
    def __init__(self, host, on_play, on_started, on_error, on_position=None):
        self.player = None
        self.source = None
        self.surface = None
        self.still_image = None
        self.still_path = None
        self.video_size = (276, 162)
        self.target = None
        self.media_class = None
        self.on_play = on_play
        self.on_started = on_started
        self.on_error = on_error
        self.on_position = on_position
        self.clock = None
        self.playback_state = "stopped"
        self.commands = SimpleQueue()
        self.results = SimpleQueue()
        self.worker = None
        self.generation = 0
        self.pending = 0
        self.poll_id = None
        self.wait_until = None
        self.reason = tr("動画プレビューには Tkinter が必要です。")
        if getattr(host, "backend", None) != "tkinter":
            return
        from tkinter import Label

        # Place the image surface over a fixed-size request so video frames
        # cannot resize the editor. The parent still expands with the window.
        host.widget.configure(height=162, width=276)
        self.target = Label(host.widget, text="▶", font=("TkDefaultFont", 18), highlightthickness=PREVIEW_BORDER,
                            borderwidth=0, padx=0, pady=0)
        self.update_theme()
        self.target.bind("<<ThemeChanged>>", self.update_theme, add="+")
        self.target.place(relwidth=1, relheight=1)
        self.target.bind("<Configure>", localized(self.resize), add="+")
        self.reason = tr("tkmedia3 を読み込めません。")
        for module in ("tkmedia3", "tkmedia", "media"):
            try:
                self.media_class = getattr(import_module(module), "Media")
            except Exception:
                # Optional native decoder/audio dependencies can also fail at import.
                continue
            self.reason = ""
            break
        self.target.bind("<Button-1>", localized(self.click_surface))

    def click_surface(self, event=None):
        if self.playback_state == "active":
            self.pause_resume()
        elif self.playback_state == "stopped":
            self.on_play()

    @property
    def available(self):
        return self.target is not None and self.media_class is not None

    def update_theme(self, event=None):
        background, foreground = tk_theme_colors(self.target)
        self.target.configure(bg=background, fg=foreground,
                              highlightbackground=foreground, highlightcolor=foreground)

    @staticmethod
    def audio_outputs():
        import sounddevice

        outputs = {}
        for host in sounddevice.query_hostapis():
            for index in host["devices"]:
                device = sounddevice.query_devices(index)
                if device["max_output_channels"] >= 2:
                    name = f'{device["name"]}, {host["name"]}'
                    outputs[f"{index}: {name}"] = [name, index]
        return outputs

    def play(self, title, milliseconds=0, audio_output=None, *, seek=False):
        kind = media_kind(title)
        if kind == "image" and self.target is not None:
            self.show_image(title["media"])
            return
        if not self.available:
            raise RuntimeError(self.reason)
        if kind == "audio" and audio_output == "mute":
            raise RuntimeError(tr("音声出力がミュートに設定されています。"))
        path, seconds, segment = playback_source(title, milliseconds)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        if not seek or self.clock is None:
            self.generation += 1
            seek = False
        self.still_path = None
        self.still_image = None
        self.target.configure(image="", text=tr("読み込み中…"))
        self.clock = None
        self.playback_state = "loading"
        self.submit(self.start_player, path, seconds, segment, self.generation, kind, milliseconds, audio_output, seek)

    def show_image(self, path):
        self.close()
        self.still_path = path
        try:
            self.render_still()
        except Exception:
            self.still_path = None
            raise

    def render_still(self):
        from PIL import Image, ImageOps, ImageTk

        with Image.open(self.still_path) as image:
            frame = ImageOps.exif_transpose(image)
            size = self.video_size
            frame.thumbnail(size, Image.Resampling.LANCZOS)
            self.still_image = ImageTk.PhotoImage(frame, master=self.target)
        self.target.configure(image=self.still_image, text="")

    def resize(self, event):
        self.video_size = preview_size(event.width, event.height)
        if self.still_path:
            try:
                self.render_still()
            except Exception as exc:
                self.close()
                self.on_error(str(exc))

    def handle_closed_image(self):
        # This callback runs on Tk's thread. Retire this playback before
        # asking the worker to close it so queued frames cannot draw again.
        self.close()
        self.on_error(tr("動画フレームを表示できなかったため、再生を停止しました。再生ボタンで再試行できます。"))

    def pause_resume(self):
        if not self.available:
            raise RuntimeError(self.reason)
        self.submit(self.toggle_player)

    def close(self):
        self.clock = None
        self.playback_state = "stopped"
        self.still_path = None
        self.still_image = None
        if self.target is not None:
            self.target.configure(image="", text="▶")
        if self.worker is not None:
            self.generation += 1
            self.submit(self.close_player)

    def dispose(self):
        if self.worker is None:
            return
        self.generation += 1
        self.commands.put(None)
        if self.poll_id is not None and self.target.winfo_exists():
            self.target.after_cancel(self.poll_id)
        self.poll_id = None

    def submit(self, operation, *args):
        if self.worker is None:
            self.worker = Thread(target=localized(self.run), daemon=True, name="Blu-ray preview")
            self.worker.start()
        self.pending += 1
        self.wait_until = monotonic() + 5
        self.commands.put((self.generation, operation, args))
        if self.poll_id is None:
            self.poll_id = self.target.after(40, localized(self.poll))

    def run(self):
        # Media may wait for a decoder or an in-flight Tk image update during
        # close(). Keep the Tk event loop free and serialize all player calls.
        while (command := self.commands.get()) is not None:
            generation, operation, args = command
            result = None
            try:
                if generation == self.generation:
                    result = operation(*args)
            except Exception as exc:
                result = exc
            self.results.put((generation, operation, result))
        try:
            self.close_player()
        except Exception:
            pass

    def poll(self):
        self.poll_id = None
        while True:
            try:
                generation, operation, result = self.results.get_nowait()
            except Empty:
                break
            self.pending -= 1
            if generation != self.generation:
                continue
            if isinstance(result, Exception):
                if operation != self.toggle_player:
                    self.playback_state = "stopped"
                    self.target.configure(image="", text="▶")
                self.on_error(str(result))
            elif result == "closed" and self.still_path is None:
                self.target.configure(image="", text="▶")
            elif operation == self.start_player:
                kind, self.clock, warning = result
                self.playback_state = "active"
                self.target.configure(text=tr("音声を再生中") if kind == "audio" else "")
                if warning:
                    self.on_error(warning)
                else:
                    self.on_started()
        if self.clock is not None and self.on_position:
            stopwatch, offset = self.clock
            self.on_position(max(0, int(stopwatch.getTime() * 1000 + offset)))
        if self.pending or self.clock is not None:
            if self.wait_until is not None and monotonic() >= self.wait_until:
                self.wait_until = None
                self.on_error(tr("動画処理の応答を待っています。編集と保存は引き続き使えます。"))
            self.poll_id = self.target.after(40, localized(self.poll))

    def start_player(self, path, seconds, segment, generation, kind, milliseconds=0, audio_output=None, seek=False):
        source = (path, segment, kind, audio_output)
        reuse = seek and self.source == source and self.player is not None
        if not reuse:
            self.close_player()
        if generation != self.generation:
            return
        player = self.player if reuse else self.media_class(path)
        self.player = player
        try:
            native_sizing = "video_size" in signature(player.play).parameters
        except (TypeError, ValueError):
            native_sizing = False
        def new_surface():
            self.surface = PlaybackSurface(
                self.target, lambda: generation == self.generation, self.handle_closed_image,
            )
            self.surface.fit_frames = not native_sizing
            return self.surface

        try:
            if segment:
                # MPLS uses the transport stream clock. Some clips start at
                # nonzero PTS, while the player seeks relative to media start.
                import av

                with av.open(path) as container:
                    stream = container.streams.video[0]
                    if stream.start_time is not None:
                        seconds -= float(stream.start_time * stream.time_base)
            if generation != self.generation:
                self.close_player()
                return
            options = {"video": None}
            if kind == "video":
                if not reuse:
                    options.update(videoFrame=new_surface(), video=0, frame_type="label")
                if native_sizing:
                    options["video_size"] = lambda: self.video_size
            has_audio = kind == "audio" or bool(
                getattr(player, "info", {}).get("streams", {}).get("audio", ()),
            )
            warning = None
            if reuse:
                if player.status == "pause":
                    player.resume()
            elif has_audio and audio_output != "mute":
                try:
                    device = self.resolve_audio_device(audio_output)
                    player.play(audio=0, audioDevice=device, **options)
                except Exception as exc:
                    from sounddevice import PortAudioError

                    if kind == "audio" or not isinstance(exc, (PortAudioError, AudioOutputUnavailable)):
                        raise
                    # Reopen because tkmedia may have loaded both streams
                    # before failing to open the output device.
                    self.close_player()
                    if generation != self.generation:
                        return
                    player = self.media_class(path)
                    self.player = player
                    options["videoFrame"] = new_surface()
                    player.play(audio=None, **options)
                    warning = tr("音声出力を開けなかったため、映像のみ再生します。 {0}", exc)
            else:
                player.play(audio=None, **options)
            seek_seconds = max(0.0, seconds)
            if reuse or seek_seconds:
                player.seek(seek_seconds)
            self.source = source
            stopwatch = getattr(player, "stopwatch", None)
            offset = milliseconds - seconds * 1000 if segment else 0
            clock = (stopwatch, offset) if stopwatch is not None else None
            return kind, clock, warning
        except Exception:
            try:
                self.close_player()
            except Exception:
                pass
            raise

    def resolve_audio_device(self, saved):
        if saved is None:
            return None
        outputs = list(self.audio_outputs().values())
        if saved in outputs:
            return saved[1]
        matches = [index for name, index in outputs if name == saved[0]]
        if len(matches) == 1:
            return matches[0]
        raise AudioOutputUnavailable(tr("設定された機器を確認してください。"))

    def toggle_player(self):
        if self.player is None:
            raise RuntimeError(tr("先にプレビューを再生してください。"))
        if self.player.status == "play":
            self.player.pause()
        elif self.player.status == "pause":
            self.player.resume()
        else:
            raise RuntimeError(tr("プレビューは停止しています。"))

    def close_player(self):
        self.source = None
        player, self.player = self.player, None
        surface, self.surface = self.surface, None
        if surface is not None:
            surface.active = False
        if player is not None:
            player.close()
        return "closed"
