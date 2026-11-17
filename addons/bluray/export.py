"""Author an HDMV disc folder from a saved or in-memory .marubd project."""
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory, TemporaryFile
from threading import Event, Lock, Timer

from .l10n import tr
from .assets import media_kind
from .bdmv import TICKS_PER_SECOND
from .disc_tracks import popup_entries, source_audio_languages, write_subtitle
from .export_cache import clip_key, restore_clip, store_clip
from .menu_navigation import HEIGHT, WIDTH, button_caption, element_geometry, initial_focus, navigation
from .menu_navigation import page_buttons, page_count, page_elements, position
from .menu_objects import fit_object_image, menu_font, render_object_image, render_text
from .preflight import check_project
from .project import parse_time

SCALE = 3
ENCODERS = {
    "CPU（libx264）": "libx264",
    "NVIDIA NVENC": "h264_nvenc",
    "Intel Quick Sync": "h264_qsv",
    "Apple VideoToolbox": "h264_videotoolbox",
    "VAAPI": "h264_vaapi",
    "AMD AMF": "h264_amf",
}


def available_encoders():
    try:
        listing = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True,
                                 text=True, timeout=5, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return {tr("CPU（libx264）"): "libx264"}
    names = {parts[1] for line in listing.splitlines() if len(parts := line.split()) > 1}
    return {tr(label): encoder for label, encoder in ENCODERS.items() if encoder in names}


class ExportCancelled(Exception):
    pass


class ExportCancellation:
    def __init__(self):
        self.requested = Event()
        self.lock = Lock()
        self.process = None

    def check(self):
        if self.requested.is_set():
            raise ExportCancelled()

    def cancel(self):
        self.requested.set()
        with self.lock:
            process = self.process
            if process is not None and process.poll() is None:
                try:
                    process.terminate()
                except ProcessLookupError:
                    return
                timeout = Timer(2, self.kill_if_running, (process,))
                timeout.daemon = True
                timeout.start()

    def kill_if_running(self, process):
        with self.lock:
            if self.process is process and process.poll() is None:
                process.kill()

    def attach(self, process):
        with self.lock:
            self.process = process
            if self.requested.is_set() and process.poll() is None:
                process.kill()

    def detach(self):
        with self.lock:
            self.process = None


def check_tools(*, iso=False):
    try:
        from bdmvkit import Disc, MenuButton
        from bdmvkit.encode import encode_clip
        from PIL import Image, ImageFont
    except ImportError as exc:
        raise RuntimeError(tr("書き出しには bdmvkit 0.7 と Pillow が必要です。README の導入手順を確認してください。")) from exc
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(tr("{0} が見つかりません。", tool))
    if iso:
        try:
            from udfkit.bluray import write_image
        except ImportError as exc:
            raise RuntimeError(tr("ISO 出力には udfkit 0.2.0 が必要です。README の導入手順を確認してください。")) from exc


def run_ffmpeg(*args, duration=None, on_progress=None, cancellation=None):
    command = ["ffmpeg", "-v", "error", "-nostdin", "-nostats"]
    if on_progress is not None:
        command += ["-progress", "pipe:1"]
    if cancellation is not None:
        cancellation.check()
    with TemporaryFile() as errors, subprocess.Popen(
        [*command, *map(str, args)], stdout=subprocess.PIPE, stderr=errors,
    ) as process:
        if cancellation is not None:
            cancellation.attach(process)
        try:
            if on_progress is not None:
                on_progress(0 if duration else None)
            previous = 0
            for line in process.stdout:
                if duration and on_progress is not None and line.startswith(b"out_time_us="):
                    try:
                        seconds = int(line.partition(b"=")[2]) / 1_000_000
                    except ValueError:
                        continue
                    percent = min(99, int(seconds / duration * 100))
                    if percent > previous:
                        previous = percent
                        on_progress(percent)
            result = process.wait()
        finally:
            if cancellation is not None:
                cancellation.detach()
        if cancellation is not None:
            cancellation.check()
        if result:
            errors.seek(max(0, errors.tell() - 8192))
            raise RuntimeError(errors.read().decode(errors="replace").strip() or tr("FFmpeg の変換に失敗しました。"))
    if on_progress is not None and duration:
        on_progress(100)


def probe_duration(source):
    for selector in (("-select_streams", "v:0", "-show_entries", "stream=duration"),
                     ("-show_entries", "format=duration")):
        probe = subprocess.run(["ffprobe", "-v", "error", *selector, "-of", "csv=p=0", str(source)],
                               capture_output=True, text=True)
        try:
            duration = float(probe.stdout.splitlines()[0])
        except (IndexError, ValueError):
            continue
        if duration > 0:
            return duration
    raise ValueError(tr("素材の再生時間を取得できません。 {0}", source))


def title_encoder(encoder, fps, chapters, vaapi_device):
    from bdmvkit.encode import fit_filter, video_args
    from bdmvkit.formats import MAX_VIDEO_BPS, VBV_BUFFER

    keys = [time for time in chapters if time > 0]
    filters = fit_filter(fps)
    if encoder == "libx264":
        return [], filters, video_args(fps, keys=keys)
    if encoder not in ENCODERS.values():
        raise ValueError(tr("映像エンコーダーを確認してください。"))
    common = ["-c:v", encoder, "-profile:v", "high", "-level:v", "4.1",
              "-g", "24", "-bf", "0", "-b:v", "12000k", "-maxrate", str(MAX_VIDEO_BPS),
              "-bufsize", str(VBV_BUFFER), "-color_primaries", "bt709", "-color_trc", "bt709",
              "-colorspace", "bt709"]
    extras = {
        "h264_nvenc": ["-bluray-compat", "1", "-aud", "1", "-forced-idr", "1"],
        "h264_qsv": ["-forced_idr", "1"],
        "h264_vaapi": ["-idr_interval", "0", "-aud", "1"],
        "h264_videotoolbox": ["-allow_sw", "0"],
        "h264_amf": [],
    }
    device_args = []
    if encoder == "h264_vaapi":
        device_args = ["-vaapi_device", vaapi_device]
        filters += ",format=nv12,hwupload"
    else:
        filters += ",format=nv12"
    if keys:
        common += ["-force_key_frames", ",".join(f"{time:.6f}" for time in keys)]
    return device_args, filters, common + extras[encoder]


def encode_title(source, clip, chapters, progress, cancellation, *, encoder="libx264",
                 vaapi_device="/dev/dri/renderD128", internal_audio=1, audio_tracks=(), subtitle_tracks=()):
    from bdmvkit.encode import audio_args
    from bdmvkit.formats import AUDIO_PID, PG_PID, PMT_PID, VIDEO_PID

    fps = (24000, 1001)
    timeline = isinstance(source, dict)
    if timeline:
        from addons.video.render import timeline_inputs

        args, graph, video, sound_label, duration = timeline_inputs(source, (1920, 1080), "24000/1001")
        maps = ["-map", "[discvideo]"]
        inputs = sum(option == "-i" for option in args)
        audio = [f"[{sound_label}]"]
    else:
        duration = probe_duration(source)
        args = ["-i", source]
        maps = ["-map", "0:v:0"]
        inputs = 1
        audio = [f"0:a:{index}" for index in range(internal_audio)]
    if any(chapter >= duration for chapter in chapters):
        raise ValueError(tr("チャプターが素材の再生範囲外です。"))
    for track in audio_tracks:
        args += ["-i", track["path"]]
        audio.append(f"{inputs}:a:0")
        inputs += 1
    if not audio:
        args += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        audio.append(f"{inputs}:a:0")
        inputs += 1
    streams = ["-streamid", f"0:{VIDEO_PID}"]
    for index, audio_map in enumerate(audio):
        maps += ["-map", audio_map]
        streams += ["-streamid", f"{index + 1}:{AUDIO_PID + index}"]
    for index, track in enumerate(subtitle_tracks):
        sup = write_subtitle(track["path"], clip.with_suffix(f".{index}.sup"), duration, cancellation.check)
        args += ["-f", "sup", "-i", sup]
        maps += ["-map", f"{inputs}:s:0"]
        streams += ["-streamid", f"{1 + len(audio) + index}:{PG_PID + index}"]
        inputs += 1
    sound = [] if timeline else ["-af", "apad"]
    for index in range(len(audio)):
        sound += audio_args(k=index)
        if timeline and index > 0:
            sound += [f"-filter:a:{index}", "apad"]
    device_args, filters, video_options = title_encoder(encoder, fps, chapters, vaapi_device)
    if timeline:
        graph.append(f"[{video}]{filters}[discvideo]")
        graph_path = clip.with_suffix(".filters.txt")
        graph_path.write_text(";\n".join(graph), encoding="ascii")
        filtering = ["-filter_complex_threads", "1", "-filter_complex_script", graph_path]
    else:
        filtering = ["-vf", filters]
    run_ffmpeg(*device_args, *args, *maps, *filtering, *video_options, *sound,
               "-c:s", "copy", *streams,
               "-t", f"{duration:.6f}", "-f", "mpegts", "-mpegts_m2ts_mode", 1,
               "-mpegts_pmt_start_pid", PMT_PID, clip, duration=duration, on_progress=progress,
               cancellation=cancellation)


def import_segments(segments, work, number, progress, cancellation, internal_audio):
    import av

    files = []
    for index, segment in enumerate(segments):
        cancellation.check()
        source = segment["media"]
        with av.open(source) as container:
            video = container.streams.video[0]
            start = float((video.start_time or 0) * video.time_base)
            available_audio = len(container.streams.audio)
        offset = max(0, segment["in_tick"] / TICKS_PER_SECOND - start)
        length = (segment["out_tick"] - segment["in_tick"]) / TICKS_PER_SECOND
        piece = work / f"{number}-{index}.mkv"
        message = tr("区間を変換中 {0}/{1}", index + 1, len(segments))
        audio = ["-map", "1:a:0"]
        if internal_audio:
            audio = [part for track in range(internal_audio)
                     for part in ("-map", f"0:a:{track}" if track < available_audio else "1:a:0")]
        run_ffmpeg("-ss", f"{offset:.6f}", "-i", source, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                   "-t", f"{length:.6f}", "-map", "0:v:0", *audio,
                   "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1",
                   "-r", "24000/1001", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                   "-c:a", "ac3", "-ac", "2", "-ar", "48000", "-af", "apad", piece,
                   duration=length, on_progress=lambda value: progress(message, value), cancellation=cancellation)
        files.append(piece)
    concat = work / f"{number}.txt"
    concat.write_text("".join(f"file '{piece.name}'\n" for piece in files), encoding="ascii")
    source = work / f"{number}-assembled.mkv"
    length = sum((part["out_tick"] - part["in_tick"]) / TICKS_PER_SECOND for part in segments)
    run_ffmpeg("-f", "concat", "-safe", "1", "-i", concat, "-c", "copy", source,
               duration=length, on_progress=lambda value: progress(tr("区間を結合中"), value), cancellation=cancellation)
    return source


def title_source(title, work, number, progress, cancellation, internal_audio):
    from .video_project import is_video_project, load_timeline

    if is_video_project(title):
        return load_timeline(title)
    kind = media_kind(title)
    if title.get("segments"):
        return import_segments(title["segments"], work, number, progress, cancellation, internal_audio)
    if kind == "video":
        return title["media"]
    source = work / f"{number}-source.mkv"
    if kind == "image":
        from PIL import Image, ImageOps

        still = work / f"{number}.png"
        with Image.open(title["media"]) as image:
            ImageOps.exif_transpose(image).convert("RGB").save(still)
        run_ffmpeg("-loop", "1", "-i", still, "-t", "5", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", source, duration=5,
                   on_progress=lambda value: progress(tr("静止画を動画に変換中"), value), cancellation=cancellation)
    else:
        run_ffmpeg("-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=24000/1001",
                   "-i", title["media"], "-map", "0:v", "-map", "1:a", "-shortest",
                   "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "ac3", "-ac", "2", source,
                   duration=probe_duration(title["media"]),
                   on_progress=lambda value: progress(tr("音声素材の映像を生成中"), value), cancellation=cancellation)
    return source


def chapter_times(title):
    times = {chapter["id"]: parse_time(chapter["time"]) / 1000 for chapter in title["chapters"]}
    ordered = sorted({0.0, *times.values()})
    indices = {time: number for number, time in enumerate(ordered, 1)}
    return ordered, {chapter_id: indices[time] for chapter_id, time in times.items()}


def menu_actions(project):
    targets = {}
    for number, title in enumerate(project["titles"], 1):
        targets[(title["id"], None)] = f"title:{number}"
        _, chapters = chapter_times(title)
        for chapter, index in chapters.items():
            targets[(title["id"], chapter)] = f"chapter:{number}:{index}"
    return targets


def scaled(size):
    return tuple(value * SCALE for value in size)


def fit_background(path, size):
    from PIL import Image, ImageOps

    with Image.open(path) as source:
        return ImageOps.fit(ImageOps.exif_transpose(source).convert("RGBA"), size,
                            method=Image.Resampling.LANCZOS)


def label(draw, text, area, font, centered=False):
    x, y, width = area
    # Wrap CJK and Latin captions with the same width available for drawing.
    lines = [""]
    for char in text:
        if char == "\n" or draw.textlength(lines[-1] + char, font=font) > width:
            if len(lines) == (1 if centered else 2):
                break
            lines.append("")
        if char != "\n":
            lines[-1] += char
    for index, line in enumerate(lines):
        draw.text((x, y + index * font.size * 1.25), line, font=font, fill="#ffffff",
                  anchor="mt" if centered else "lt")


def render_background(menu, work, title_names=None, *, page=0):
    from PIL import Image

    size = scaled((WIDTH, HEIGHT))
    if menu.get("motion"):
        background = Image.new("RGBA", size)
    else:
        background = (fit_background(menu["background"], size) if menu["background"]
                      else Image.new("RGBA", size, "#20242b"))
    for index, item in page_elements(menu, page):
        default, size = element_geometry(item, index)
        x, y = scaled(position(item, default, size))
        background.alpha_composite(render_object(item, size, title_names), (x, y))
    path = work / f"menu-background-{page}.png"
    (background if menu.get("motion") else background.convert("RGB")).save(path)
    return str(path)


def render_object(entry, size, title_names=None):
    from PIL import Image, ImageDraw

    width, height = scaled(size)
    result = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(result)
    bounds = (0, 0, width - 1, height - 1)
    if entry["kind"] == "image":
        result.alpha_composite(render_object_image(entry, size, title_names, scale=SCALE))
    elif entry["kind"] == "shape":
        shape = draw.ellipse if entry.get("shape") == "ellipse" else draw.rectangle
        shape(bounds, fill=entry.get("fill", "#252a33"), outline=entry.get("outline", "#a8b0bd"), width=3)
    else:
        return render_text(entry, size, scale=SCALE)
    return result


def render_button(work, key, entry, size, selected):
    from PIL import Image, ImageDraw

    width, height = scaled(size)
    path = work / f"{key}-{'selected' if selected else 'normal'}.png"
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(result)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=12, fill="#224478" if selected else "#252a33",
                           outline="#f9d775" if selected else "#a8b0bd", width=6 if selected else 3)
    if entry.get("image"):
        picture = fit_object_image(entry, (size[0] - 12, size[1] - 37), scale=SCALE)
        result.alpha_composite(picture, ((width - picture.width) // 2, 18))
    label(draw, button_caption(entry), (width // 2, height - 60, width - 36), menu_font(33), centered=True)
    result.save(path)
    return str(path)


def render_focus(work, key, entry, size):
    from PIL import Image, ImageDraw

    width, height = scaled(size)
    image = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(image)
    outline = draw.ellipse if entry.get("shape") == "ellipse" else draw.rectangle
    outline((0, 0, width - 1, height - 1), outline="#f9d775", width=6)
    path = work / f"{key}-focus.png"
    image.save(path)
    return str(path)


def menu_background(menu, page, work, names, cancellation, progress):
    background = render_background(menu, work, names, page=page)
    if menu.get("motion"):
        motion = work / f"menu-motion-{page}.mkv"
        duration = probe_duration(menu["motion"])
        graph = ("[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
                 "setsar=1,fps=24000/1001[base];[base][1:v]overlay")
        run_ffmpeg("-i", menu["motion"], "-i", background, "-filter_complex", graph,
                   "-an", "-t", f"{duration:.6f}", "-c:v", "libx264", "-preset", "fast",
                   "-crf", "16", motion, duration=duration, cancellation=cancellation,
                   on_progress=lambda percent: progress(tr("メニュー背景動画を変換中…"), percent))
        background = str(motion)
    return background


def add_menus(disc, project, actions, work, cancellation, progress):
    from bdmvkit import MenuButton

    menu = project["menu"]
    names = {title["id"]: title["name"] for title in project["titles"]}
    backgrounds = {}
    for page in range(page_count(menu)):
        cancellation.check()
        visible = tuple(index for index, _ in page_elements(menu, page))
        if visible not in backgrounds:
            backgrounds[visible] = menu_background(menu, page, work, names, cancellation, progress)
        items = page_buttons(menu, page, project["titles"][0]["id"])
        moves = navigation(items, page)
        keys = {item.key: f"page{page}-button{index}" for index, item in enumerate(items)}
        buttons = []
        for item in items:
            key = keys[item.key]
            entry = item.entry
            x, y = scaled(item.xy)
            if "kind" in entry:
                selected = render_focus(work, key, entry, item.size)
                normal = None
            else:
                selected = render_button(work, key, entry, item.size, True)
                normal = render_button(work, key, entry, item.size, False)
            destination = item.destination_page
            streams = {}
            if destination is not None:
                action = f"menu:page{destination}"
            elif item.target.get("play_all") is True:
                action = "playall"
            else:
                action = actions[(item.target["title"], item.target.get("chapter"))]
                if "audio" in item.target:
                    streams = {"audio": item.target["audio"], "subtitle": item.target["subtitle"]}
            nav = {direction: keys[destination] for direction, destination in moves[item.key].items()}
            buttons.append(MenuButton(key, x, y, selected, normal=normal, action=action, nav=nav, **streams))
        disc.add_menu(f"page{page}", backgrounds[visible], buttons, default=keys[initial_focus(menu, page, items)],
                      music=menu.get("music") or None)


def add_popup(disc, number, entries, work, cancellation):
    from bdmvkit import MenuButton

    buttons = []
    for index, (caption, action) in enumerate(entries):
        cancellation.check()
        row, col = divmod(index, 4)
        key = f"popup{number}-{index}"
        entry = {"label": caption}
        size = (150, 26)
        selected = render_button(work, key, entry, size, True)
        normal = render_button(work, key, entry, size, False)
        buttons.append(MenuButton(key, *scaled((12 + col * 155, 12 + row * 28)),
                                  selected, normal=normal, action=action))
    disc.add_popup(number, buttons)


def write_iso(disc_folder, target, progress, cancellation):
    from udfkit.bluray import write_image

    def update(fraction):
        cancellation.check()
        progress(tr("Blu-ray ISO を生成中…"), min(99, int(fraction * 100)))

    image = disc_folder.parent / "disc.iso"
    update(0)
    write_image(str(disc_folder), str(image), "BLU_RAY", on_progress=update)
    cancellation.check()
    # Claim the target exclusively, then publish the already-written image.
    with target.open("xb"):
        pass
    try:
        cancellation.check()
        image.replace(target)
    except (OSError, ExportCancelled):
        target.unlink()
        raise
    progress(tr("Blu-ray ISO を生成しました。"), 100)


def export_disc(project, target, progress, cancellation=None, *, cache_dir=None, iso=False,
                encoder="libx264", vaapi_device="/dev/dri/renderD128"):
    cancellation = cancellation or ExportCancellation()
    cancellation.check()
    from .video_project import prepare_project

    project = prepare_project(project)
    check_tools(iso=iso)
    from bdmvkit import Disc

    target = Path(target)
    if target.exists():
        raise FileExistsError(tr("書き出し先が既にあります。 {0}", target))
    if not project["titles"]:
        raise ValueError(tr("書き出す素材を追加してください。"))
    errors, _ = check_project(project)
    if errors:
        raise ValueError("\n".join(errors))
    actions = menu_actions(project)
    with TemporaryDirectory(prefix=".marubd-export-", dir=target.parent) as directory:
        work = Path(directory)
        disc = Disc()
        chapter_counts = []
        plans = []
        for index, title in enumerate(project["titles"], 1):
            cancellation.check()
            internal = source_audio_languages(title)
            audio_tracks = title.get("audio_tracks", [])
            subtitles = title.get("subtitle_tracks", [])
            audio = internal + [track["language"] for track in audio_tracks] or ["und"]
            languages = [track["language"] for track in subtitles]
            chapters, _ = chapter_times(title)
            popup = popup_entries(index, chapters, audio, languages) if title.get("popup_menu") else []
            if len(popup) > 48:
                raise ValueError(tr("「{0}」のポップアップ項目が48個を超えています。", title['name']))
            plans.append((internal, audio_tracks, subtitles, audio, languages, chapters, popup))
        audio_counts = {title["id"]: len(plan[3]) for title, plan in zip(project["titles"], plans)}
        menu = project["menu"]
        for entry in menu["buttons"] + menu["elements"]:
            link = entry.get("target") or {}
            if "audio" in link and link["audio"] > audio_counts[link["title"]]:
                raise ValueError(tr("メニューの音声トラックが見つかりません。音声・字幕設定を作り直してください。"))
        for index, (title, plan) in enumerate(zip(project["titles"], plans), 1):
            internal, audio_tracks, subtitles, audio, languages, chapters, popup = plan
            cancellation.check()
            prefix = tr("素材 {0}/{1}　{2}", index, len(project['titles']), title['name'])

            def update(stage, percent):
                progress(f"{prefix}\n{stage}", percent)

            update(tr("準備中…"), None)
            clip = work / f"{index}.m2ts"
            encoding = encoder if encoder != "h264_vaapi" else (encoder, vaapi_device)
            cached = Path(cache_dir) / (clip_key(title, chapters, encoding) + ".m2ts") if cache_dir is not None else None
            if cached is not None:
                update(tr("キャッシュを確認中…"), None)
            restored = False
            if cached is not None:
                try:
                    restored = restore_clip(cached, clip, cancellation.check)
                except OSError:
                    clip.unlink(missing_ok=True)
                    cached = None
            if restored:
                update(tr("変換済み素材を再利用"), 100)
            else:
                source = title_source(title, work, index, update, cancellation, len(internal))
                encode_title(source, clip, chapters, lambda percent: update(tr("Blu-ray 用に変換中 ({0})", encoder), percent),
                             cancellation, encoder=encoder, vaapi_device=vaapi_device,
                             internal_audio=len(internal), audio_tracks=audio_tracks, subtitle_tracks=subtitles)
                if cached is not None and cached.stem == clip_key(title, chapters, encoding):
                    update(tr("変換済み素材をキャッシュに保存中…"), None)
                    try:
                        store_clip(clip, cached, cancellation.check)
                    except OSError as exc:
                        progress(tr("キャッシュを保存できませんでした。書き出しを続けます。\n{0}", exc), None)
            end = f"title:{index + 1}" if title.get("playback_end") == "next" and index < len(plans) else "lastmenu"
            disc.add_title(str(clip), chapters=chapters, end=end,
                           audio=[("ac3", 2, language) for language in audio], subtitles=languages)
            if popup:
                add_popup(disc, index, popup, work, cancellation)
            chapter_counts.append(len(chapters))
        progress(tr("HDMV メニューと BDMV を生成中…"), None)
        add_menus(disc, project, actions, work, cancellation, progress)
        progress(tr("HDMV メニューと BDMV を生成中…"), None)
        output = work / "disc"
        cancellation.check()
        result = disc.write(str(output), move=True, play_all=False)
        cancellation.check()
        if result["chapters"] != chapter_counts:
            raise ValueError(tr("近接したチャプターが同じキーフレームに重なっています。チャプターの時刻を調整してください。"))
        if iso:
            write_iso(output, target, progress, cancellation)
            return result
        # Reserve the destination before moving files; preserve any prior export.
        target.mkdir()
        try:
            for child in output.iterdir():
                cancellation.check()
                child.rename(target / child.name)
            cancellation.check()
        except (OSError, ExportCancelled):
            shutil.rmtree(target)
            raise
    return result
