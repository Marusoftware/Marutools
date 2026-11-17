"""Author DVD-Video titles, menus and navigation with vtskit."""
from contextlib import suppress
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from .disc_tracks import read_srt, source_audio_languages
from .export import (ExportCancellation, ExportCancelled, chapter_times, probe_duration,
                     render_background, render_button, run_ffmpeg, scaled, title_source)
from .l10n import tr
from .menu_navigation import HEIGHT, WIDTH, initial_focus, navigation, page_buttons, page_count
from .menu_objects import menu_font
from .preflight import check_project, issue_message

# Standard DVD raster and the corresponding 16:9 pixel aspect ratio.
DVD_STANDARDS = {"NTSC": (480, "32/27"), "PAL": (576, "64/45")}


def check_dvd_tools(*, iso=False):
    try:
        from vtskit import lang, menu, titleset, vmg
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(tr("DVD の書き出しには vtskit 0.3.1 と Pillow が必要です。")) from exc
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise RuntimeError(tr("{0} が見つかりません。", tool))
    if iso:
        try:
            from udfkit.dvd import write_image
        except ImportError as exc:
            raise RuntimeError(tr("ISO 出力には udfkit 0.2.0 が必要です。README の導入手順を確認してください。")) from exc


def check_dvd_project(project):
    errors, warnings = check_project(project)
    titles = project["titles"]
    if len(titles) > 99:
        errors.append(tr("DVD に収録できるタイトルは99個までです。"))
    menu = project["menu"]
    for page in range(page_count(menu)):
        if len(page_buttons(menu, page, titles[0]["id"] if titles else None)) > 36:
            errors.append(tr("DVD のメニューは1ページにつき36ボタンまでです。ページ {0}", page + 1))
    for title in titles:
        try:
            times, _ = chapter_times(title)
        except ValueError:
            continue  # The common preflight already reports invalid timestamps.
        if len(times) > 99:
            errors.append(tr("DVD のチャプターは1タイトルにつき99個までです。 {0}", title["name"]))
        if len(title.get("subtitle_tracks", [])) > 32:
            errors.append(tr("DVD の字幕は1タイトルにつき32トラックまでです。 {0}", title["name"]))
        if any(Path(track["path"]).suffix.lower() != ".srt" for track in title.get("subtitle_tracks", [])):
            errors.append(tr("DVD の字幕には UTF-8 の SRT を指定してください。 {0}", title["name"]))
    if any(title.get("popup_menu") for title in titles):
        warnings.append(tr("Blu-ray の再生中ポップアップは DVD に書き出されません。"))
    return errors, warnings


def dvd_language(code):
    from babel.core import get_global

    result = get_global("language_aliases").get(code, code)
    return result if len(result) == 2 and result.isascii() and result.isalpha() else None


def dvd_mux_args(standard):
    return ("-target", standard.lower() + "-dvd", "-aspect", "16:9", "-bf", "0",
            "-flags", "+cgop", "-sc_threshold", "1000000000", "-threads:v", "2",
            "-c:a", "ac3", "-ar", "48000", "-ac", "2", "-b:a", "192k")


def encode_dvd_title(source, output, chapters, audio_count, tracks, standard, cancellation, notify):
    duration = probe_duration(source)
    if any(chapter >= duration for chapter in chapters):
        raise ValueError(tr("DVD のチャプターが素材の再生範囲外です。"))
    height, sar = DVD_STANDARDS[standard]
    display_width = round(height * 16 / 9 / 2) * 2
    filters = (f"scale=trunc(iw*sar/2)*2:ih,setsar=1,"
               f"scale={display_width}:{height}:force_original_aspect_ratio=decrease:force_divisible_by=2,"
               f"pad={display_width}:{height}:(ow-iw)/2:(oh-ih)/2,scale=720:{height},setsar={sar}")
    inputs = ["-i", source]
    maps = ["-map", "0:v:0"]
    for index in range(audio_count):
        maps.extend(("-map", f"0:a:{index}"))
    for index, track in enumerate(tracks, 1):
        inputs.extend(("-i", track["path"]))
        maps.extend(("-map", f"{index}:a:0"))
    if not audio_count and not tracks:
        inputs.extend(("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"))
        maps.extend(("-map", "1:a:0"))
    keys = [f"{time:.6f}" for time in chapters if time]
    key_args = ("-force_key_frames", ",".join(keys)) if keys else ()
    run_ffmpeg(*inputs, *maps, "-t", f"{duration:.6f}", "-filter_threads", "1", "-vf", filters, "-af", "apad",
               *dvd_mux_args(standard), *key_args, output, duration=duration,
               on_progress=notify, cancellation=cancellation)
    return duration


def dvd_subtitles(path, height, duration, cancellation):
    from PIL import Image, ImageDraw
    from vtskit import spu, subtitles

    font = menu_font(30)
    cues = [cue for cue in read_srt(path) if cue.start < duration]
    if not cues:
        raise ValueError(tr("再生範囲内に字幕がありません。 {0}", path))
    for index, cue in enumerate(cues):
        cancellation.check()
        end = min(cue.end, cues[index + 1].start if index + 1 < len(cues) else duration, duration)
        if end <= cue.start:
            continue
        picture = Image.new("L", (720, height))
        draw = ImageDraw.Draw(picture)
        lines = []
        for paragraph in cue.text.splitlines():
            line = ""
            for char in paragraph:
                if line and draw.textlength(line + char, font=font) > 644:
                    lines.append(line)
                    line = ""
                line += char
            lines.append(line)
        draw.multiline_text((360, height - 34), "\n".join(lines), font=font, fill=255, stroke_width=2,
                            stroke_fill=90, align="center", anchor="md", spacing=4)
        box = picture.getbbox()
        if box:
            pixels = picture.crop(box).point([0] + [2] * 144 + [1] * 111)
            yield subtitles.Cue(cue.start, end, spu.Overlay(*pixels.size, pixels.tobytes()), box[0], box[1])


def encode_menu_background(menu, page, items, names, work, standard, progress, cancellation):
    from PIL import Image

    height, sar = DVD_STANDARDS[standard]
    png = render_background(menu, work, names, page=page)
    with Image.open(png) as base:
        background = base.convert("RGBA")
    for index, item in enumerate(items):
        if "kind" not in item.entry:
            path = render_button(work, f"dvd-{page}-{index}", item.entry, item.size, False)
            with Image.open(path) as button:
                background.alpha_composite(button, scaled(item.xy))
    motion, music = menu.get("motion"), menu.get("music")
    background.resize((720, height), Image.Resampling.LANCZOS).convert("RGBA" if motion else "RGB").save(png)
    duration = probe_duration(motion or music) if motion or music else 1.0
    # A DVD highlight is muxed as a subpicture over the normal menu picture.
    if motion:
        display_width = round(height * 16 / 9 / 2) * 2
        filter_graph = (f"[0:v]scale=trunc(iw*sar/2)*2:ih,setsar=1,"
                        f"scale={display_width}:{height}:force_original_aspect_ratio=increase:force_divisible_by=2,"
                        f"crop={display_width}:{height},scale=720:{height},setsar={sar}[bg];[bg][1:v]overlay[video]")
        inputs = ["-i", motion, "-loop", "1", "-i", png]
        options = ["-filter_complex", filter_graph, "-map", "[video]"]
    else:
        inputs = ["-loop", "1", "-i", png]
        options = ["-map", "0:v:0", "-vf", f"setsar={sar}"]
    if music:
        inputs += ["-i", music]
        options += ["-map", f"{2 if motion else 1}:a:0", "-af", "apad"]
    else:
        options += ["-an"]
    stream = work / f"menu-{page}.mpg"
    run_ffmpeg(*inputs, *options, "-filter_threads", "1", "-filter_complex_threads", "1",
               "-t", f"{duration:.6f}", *dvd_mux_args(standard), stream, duration=duration,
               on_progress=progress, cancellation=cancellation)
    return str(stream)


def stream_selection(link):
    if "audio" not in link:
        return ""
    # DVD audio and subtitle stream numbers start at zero. Bit 6 shows the subtitle.
    subtitle = link["subtitle"] - 1 + 64 if link["subtitle"] else 0
    return f"g3 = {link['audio'] - 1}; g4 = {subtitle}; g5 = 1; "


def author_dvd(project, work, folder, standard, progress, cancellation):
    from vtskit import lang, menu as dvd_menu, ps, spu, subtitles, titleset, vmg

    project_menu = project["menu"]
    titles = project["titles"]
    names = {title["id"]: title["name"] for title in titles}
    indices = {title["id"]: n for n, title in enumerate(titles, 1)}
    marks = {title["id"]: chapter_times(title) for title in titles}
    count = page_count(project_menu)
    height, _ = DVD_STANDARDS[standard]
    audio_entries = [entry["target"] for entry in project_menu["buttons"] + project_menu["elements"]
                     if "audio" in (entry.get("target") or {})]
    audio_plans = []
    for title in titles:
        cancellation.check()
        tracks = title.get("audio_tracks", [])
        internal = source_audio_languages(title)
        languages = internal + [track["language"] for track in tracks] or ["und"]
        if len(languages) > 8:
            raise ValueError(tr("DVD の音声は1タイトルにつき8トラックまでです。 {0}", title["name"]))
        if any(link["title"] == title["id"] and link["audio"] > len(languages) for link in audio_entries):
            raise ValueError(tr("メニューの音声トラックが見つかりません。音声・字幕設定を作り直してください。"))
        audio_plans.append((tracks, len(internal), languages))
    # Chunk the return dispatcher so a disc can have many pages without a long PGC.
    route_pages = [range(start, min(start + 30, count + 1)) for start in range(1, count + 1, 30)]
    return_pgc = count + 1
    compiler = lang.Disc({(n, 1): n for n in indices.values()},
                         vmgm=lang.Menus(count + len(route_pages), {"title": 1}),
                         titlesets={n: lang.Menus(2, {"root": 1, "ptt": 2}) for n in indices.values()})
    title_posts = []
    for n, title in enumerate(titles, 1):
        # The default returns to the page that launched playback. Play All overrides title endings.
        end = f"call vmgm menu {return_pgc};"
        if n < len(titles):
            follow = f"jump titleset {n + 1} title 1;"
            end = follow if title.get("playback_end") == "next" else f"if (g2 == 1) {{ {follow} }} {end}"
        title_posts.append(compiler.compile(end, "vts", n))

    menus = []
    for page in range(count):
        cancellation.check()
        items = page_buttons(project_menu, page, titles[0]["id"])
        pgc = page + 1
        commands = []
        for item in items:
            destination = item.destination_page
            if destination is not None:
                commands.append(f"jump menu {destination + 1};")
            elif item.target.get("play_all") is True:
                commands.append("g2 = 1; jump title 1;")
            else:
                target = item.target
                title_id = target["title"]
                chapter = marks[title_id][1].get(target.get("chapter"))
                command = f"jump title {indices[title_id]}"
                if chapter and chapter > 1:
                    command += f" chapter {chapter}"
                commands.append(stream_selection(target) + command + ";")
        button_codes, post = compiler.menu(commands, f"jump menu {pgc};", "vmgm")
        moves = navigation(items, page)
        buttons, strokes = [], []
        numbers = {item.key: n for n, item in enumerate(items, 1)}
        for item, code in zip(items, button_codes):
            x, y = item.xy
            box_width, box_height = item.size
            xa, ya = x * 720 // WIDTH, y * height // HEIGHT
            xb, yb = (x + box_width) * 720 // WIDTH, (y + box_height) * height // HEIGHT
            directions = {key: numbers[value] for key, value in moves[item.key].items()}
            buttons.append(dvd_menu.Button((xa, ya, xb, yb), code, **directions))
            # Highlight the edge without obscuring the thumbnail underneath.
            strokes.extend(((xa, ya, xb, min(ya + 3, yb)), (xa, max(ya, yb - 3), xb, yb),
                            (xa, ya, min(xa + 3, xb), yb), (max(xa, xb - 3), ya, xb, yb)))
        overlay = spu.Overlay.from_rects(720, height, strokes)
        caption = tr("DVD メニュー {0}/{1} を変換中…", pgc, count)
        stream = encode_menu_background(project_menu, page, items, names, work, standard,
                                        lambda value: progress(caption, value), cancellation)
        pre = compiler.compile(f"g1 = {pgc}; g2 = 0; g5 = 0;", "vmgm")
        menus.append(dvd_menu.Menu(stream, buttons, overlay=overlay, pre=pre, post=post,
                                   entry="title" if page == 0 else None,
                                   first_button=numbers.get(initial_focus(project_menu, page, items), 0)))
    for index, routes in enumerate(route_pages):
        instructions = "".join(f"if (g1 == {page}) {{ jump menu {page}; }}" for page in routes)
        fallback = return_pgc + index + 1 if index + 1 < len(route_pages) else 1
        pre = compiler.compile(instructions + f"jump menu {fallback};", "vmgm")
        menus.append(dvd_menu.Menu(None, pre=pre))
    menus.extend(dvd_menu.Menu(None, pre=pre) for pre in compiler.vmgm_pads())
    folder.mkdir(parents=True)
    written = []
    for n, (title, audio_plan) in enumerate(zip(titles, audio_plans), 1):
        cancellation.check()
        label = tr("素材 {0}/{1}　{2}", n, len(titles), title["name"])
        audio_tracks, internal_count, languages = audio_plan
        subtitle_tracks = title.get("subtitle_tracks", [])
        source = title_source(title, work, n, lambda stage, value: progress(f"{label}\n{stage}", value),
                              cancellation, internal_count)
        mpg = work / f"title-{n}.mpg"
        chapters = marks[title["id"]][0]
        duration = encode_dvd_title(source, mpg, chapters, internal_count, audio_tracks, standard, cancellation,
                                    lambda value: progress(label, value))
        if subtitle_tracks:
            stream = work / f"title-{n}-subtitles.mpg"
            cues = {i: dvd_subtitles(track["path"], height, duration, cancellation)
                    for i, track in enumerate(subtitle_tracks)}
            with ps.Mapped(mpg) as encoded, stream.open("wb") as output:
                subtitles.mux(encoded, cues, out=output)
            mpg = stream
        cancellation.check()
        pre = compiler.compile("if (g5 == 1) { audio = g3; subtitle = g4; g5 = 0; }", "vts", n)
        authored = titleset.Title(stream=str(mpg), chapters=tuple(chapters),
                                  audio=tuple(titleset.Audio(dvd_language(code)) for code in languages),
                                  subpictures=tuple(titleset.Subpicture(dvd_language(track["language"]))
                                                    for track in subtitle_tracks),
                                  palette=((16, 128, 128), (235, 128, 128), (16, 128, 128)),
                                  pre=pre, post=title_posts[n - 1])
        root = compiler.compile("jump vmgm menu entry title;", "vtsm", n)
        pad = compiler.vts_pad(n) or root
        domain_menus = (dvd_menu.Menu(None, pre=root, entry="root"), dvd_menu.Menu(None, pre=pad, entry="ptt"))
        progress(tr("DVD の構造を生成中…"), None)
        result = titleset.write(folder, n, (authored,), menus=domain_menus, pan_scan=False)
        if len(result.titles[0].programs) != len(chapters):
            raise ValueError(tr("DVD の同じ GOP に複数のチャプターが重なっています。 {0}", title["name"]))
        written.append(result)
    cancellation.check()
    vmg.write(folder, written, menus=menus, provider="Marutools", pan_scan=False)
    cancellation.check()
    return {"titles": len(written), "menus": count, "chapters": [len(marks[title["id"]][0]) for title in titles]}


def export_dvd(project, target, progress, cancellation=None, *, iso=False, standard="NTSC"):
    cancellation = cancellation or ExportCancellation()
    cancellation.check()
    check_dvd_tools(iso=iso)
    if standard not in DVD_STANDARDS:
        raise ValueError(tr("DVD のテレビ方式を確認してください。"))
    errors, _ = check_dvd_project(project)
    if errors:
        raise ValueError(issue_message(errors))
    target = Path(target)
    if target.exists():
        raise FileExistsError(tr("書き出し先が既にあります。 {0}", target))
    with TemporaryDirectory(prefix=".marudvd-export-", dir=target.parent) as directory:
        work = Path(directory)
        disc = work / "disc"
        result = author_dvd(project, work, disc / "VIDEO_TS", standard, progress, cancellation)
        if iso:
            from udfkit.dvd import write_image

            image = work / "disc.iso"

            def update(fraction):
                cancellation.check()
                progress(tr("DVD-Video ISO を生成中…"), min(99, int(fraction * 100)))

            write_image(disc, image, "DVD_VIDEO", on_progress=update)
            cancellation.check()
            with target.open("xb"):
                pass
            try:
                cancellation.check()
                os.replace(image, target)
            except (OSError, ExportCancelled):
                target.unlink()
                raise
        else:
            target.mkdir()
            try:
                cancellation.check()
                (disc / "VIDEO_TS").rename(target / "VIDEO_TS")
            except (OSError, ExportCancelled):
                with suppress(OSError):
                    target.rmdir()
                raise
    return result
