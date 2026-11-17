"""Render timeline compositing and audio mixing with FFmpeg."""
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory

from addons.bluray.export import ExportCancellation, run_ffmpeg

from .project import TRACKS, duration, end, length


def timeline_inputs(project, size=(1280, 720), fps="30"):
    if not project["clips"]:
        raise ValueError("Add a clip to the timeline first.")
    if not which("ffmpeg"):
        raise RuntimeError("FFmpeg was not found.")
    clips = sorted(project["clips"], key=lambda clip: (-TRACKS.index(clip["track"]), clip["start"]))
    assets = project["assets"]
    for source in {assets[clip["asset"]]["path"] for clip in clips}:
        if not Path(source).is_file():
            raise FileNotFoundError(source)

    width, height = size
    seconds = duration(project) / 1000
    inputs = ["-f", "lavfi", "-i", f"color=black:size={width}x{height}:rate={fps}:duration={seconds:.3f}",
              "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={seconds:.3f}"]
    filters = []
    video = "0:v"
    audio = ["[1:a]"]
    for index, clip in enumerate(clips, 2):
        asset = assets[clip["asset"]]
        offset = clip["start"] / 1000
        span = length(clip) / 1000
        if asset["still"]:
            inputs += ["-loop", "1", "-framerate", str(fps)]
        else:
            inputs += ["-ss", f'{clip["in"] / 1000:.3f}']
        inputs += ["-t", f"{span:.3f}", "-i", asset["path"]]
        if clip["track"].startswith("V"):
            layer, combined = f"layer{index}", f"video{index}"
            filters.append(
                f"[{index}:{asset['video']}]setpts=PTS-STARTPTS,"
                f"scale=trunc(iw*sar/2)*2:ih,setsar=1,"
                f"scale={width}:{height}:force_original_aspect_ratio=decrease:force_divisible_by=2,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},"
                f"tpad=stop_mode=clone:stop_duration=0.10,trim=duration={span:.3f},"
                f"setpts=PTS+{offset:.3f}/TB[{layer}]")
            filters.append(
                f"[{video}][{layer}]overlay=eof_action=pass:repeatlast=0:"
                f"enable='gte(t,{offset:.3f})*lt(t,{end(clip) / 1000:.3f})'[{combined}]")
            video = combined
        if asset["audio"] is not None and not clip["muted"]:
            name = f"audio{index}"
            filters.append(f"[{index}:{asset['audio']}]aresample=48000,"
                           f"aformat=sample_fmts=fltp:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
                           f"atrim=duration={span:.3f},adelay={clip['start']}:all=1[{name}]")
            audio.append(f"[{name}]")
    filters.append("".join(audio) + f"amix=inputs={len(audio)}:normalize=0:duration=first,"
                   "alimiter=limit=0.95:level=0:latency=1[audio]")
    return inputs, filters, video, "audio", seconds


def render(project, target, *, size=(1280, 720), proxy=False, progress=None, cancellation=None):
    cancellation = cancellation or ExportCancellation()
    cancellation.check()
    target = Path(target).absolute()
    if target.exists():
        raise FileExistsError("Choose a new output file.")
    inputs, filters, video, audio, seconds = timeline_inputs(project, size)
    with TemporaryDirectory(prefix=".maruvideo-render-", dir=target.parent) as directory:
        work = Path(directory)
        graph = work / "filters.txt"
        graph.write_text(";\n".join(filters), encoding="ascii")
        output = work / "render.mp4"
        run_ffmpeg(*inputs, "-filter_complex_threads", "1", "-filter_complex_script", graph,
                   "-map", f"[{video}]" if video != "0:v" else video, "-map", "[audio]",
                   "-t", f"{seconds:.3f}", "-c:v", "libx264", "-threads:v", "3",
                   "-preset", "ultrafast" if proxy else "fast", "-crf", "27" if proxy else "20",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                   output, duration=seconds, on_progress=progress, cancellation=cancellation)
        cancellation.check()
        with target.open("xb"):
            pass
        try:
            cancellation.check()
            output.replace(target)
        except BaseException:
            target.unlink(missing_ok=True)
            raise
