# Marutools Video

Select **Video** and create a `.maruvideo` project, or open an MP4 in Video to start with that clip. Save the edit as a `.maruvideo` file. Projects reference the original media and keep the timeline editable.

- Use **Add Media…** or drop files on the media list. Drag an item from the list to a track, or position the playhead and select **Add to Timeline**.
- Drag a timeline clip to move it, or drag either edge to trim it. Select a clip and choose **Split at Playhead** to cut it at that position. Delete, mute, undo, and redo are available in the timeline toolbar.
- V2 appears above V1. Both video tracks include their clips' sound by default. A1 and A2 play audio only. Unmuted clips are mixed, and gaps in the video are black.
- **Preview Source** plays the selected media item. **Play Timeline** renders a 360p preview of the current edit and reuses it until timeline changes invalidate it. Playback needs the same tkmedia installation as the Blu-ray add-on.
- **Export MP4…** renders the edit to a new 720p, 30 fps H.264/AAC file. Preview generation and export show progress and can be cancelled.
- To author a disc, save the project and add the `.maruvideo` file as media in **Blu-ray and DVD**. The disc editor reads the saved timeline and encodes its composite directly into a Blu-ray or DVD title during export. Save further Video edits before exporting to include them in the disc.

FFmpeg with libx264 and AAC encoding and `ffprobe` must be on PATH. This version provides tracks, cuts and trims, and volume muting. Transitions, effects, and keyframe editing are not available yet.
