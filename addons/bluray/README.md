# Marutools Blu-ray Add-on v0.5

This checkout already includes the add-on in `addons/bluray/`. To install it in another copy of Marutools, extract the v0.5 ZIP into `addons/`, check that `addons/bluray/__init__.py` is present, and restart Marutools.

- Select the Blu-ray editor in Marutools and create a new `.marubd` project or open an existing one.
- Use **Add Media** to select multiple images, audio files, or videos. You can also drag files from your file manager onto the media list when TkDND is enabled. **Open BDMV** reads the main video segments and chapter marks from the BDMV playlist files (MPLS) and adds them as titles to the current project. The import reads the source files without modifying them.
- Select media in the left pane to rename or reorder it. Drag the divider between the media list and the preview to adjust their widths. Use the Marutools **Edit** menu to undo or redo changes. The seek bar below the preview follows playback. Move to a position and select **Add Chapter Here**. Use **Chapters** to edit chapter names and times, delete chapters, or seek to them.
- The **Media** tab contains the media list, video preview, and chapter controls. The **Menu** tab has a canvas for editing the menu background and layout. Displaying background images requires Pillow.
- Select a title in the **Media** tab and open **After Playback…** to choose **Return to menu** (the default) or **Play next title**. In the exported BDMV or ISO, this setting applies at the end of the title whether playback started at the beginning or from a chapter. The next title follows the order of the media list. After the final title, playback returns to the menu.
- In the **Menu** tab, add rectangles, ellipses, text, and images, then drag them into position. You can link each object to a title or chapter. Menu images and backgrounds can use images registered through **Add Media**. **Add Video Thumbnail** captures a frame from a registered video at the time you choose. The thumbnail is embedded in the project and initially links to the source video. Enable **Show video title** when adding or editing the thumbnail to display the title beneath the image. You can edit menu titles from earlier versions as text. Drag the lower-right corner of the selection box to resize an object. Use **Edit Selected Item** to choose a shape and set its fill and outline colors. For text, you can set a font file (TTF, OTF, or TTC), font size, text color, and background color. The project references the font file. Layout and formatting changes appear immediately. Save the project in Marutools to keep them.
- Use **Add Page** in the **Menu** tab to create pages. Use **‹ Previous** and **Next ›** below the canvas to switch between pages while editing. Use **Visible on** to choose where an object appears. With the default navigation, export adds **Previous** and **Next** buttons at the top of the menu where adjacent pages are available.
- To create a page navigation button manually, add text, a shape, or an image and choose the destination **Menu Page** under **Link target**. For example, link a **Back to Top** text object on page 2 to **Menu Page 1**. These links work in the exported BDMV or ISO.
- **Generate Standard Layout…** creates a top menu, chapter pages, and audio and subtitle settings pages from your media. The left side of the top menu has room for an image. The chapter pages show thumbnails for the start of each video and its saved chapter marks. Choose an even number from 2 to 16 for thumbnails per page. The audio and subtitle settings pages let viewers choose a track combination and play the corresponding title. If the menu already has pages or objects, Marutools asks before replacing them. The generated layout keeps the background and music. Use **Undo** to restore the previous layout.
- **Delete Page** removes the current page and objects specific to it. Links to the deleted page are cleared. Objects shared across all pages are kept, and the menu always has at least one page. You can undo a page deletion from the **Edit** menu.
- Select a linked object in the **Menu** tab and open **Remote Navigation…** to set which button is selected initially on the page and where the remote's directional buttons move from the selected object. These settings apply to the exported BDMV or ISO. Open the link target list and scroll when there are many choices.
- **Check** and the export preflight look for broken links, missing files, chapter marks beyond the known duration, and overlapping button areas. Fix errors before exporting. If only warnings remain, you can review them and continue.
- **Save As** updates references to media, BDMV sources, and menu images relative to the new project location. The editor also opens v0.4 `.marubd` projects.

## Interface language

The add-on follows the Marutools language setting. Reopen the Blu-ray project after changing the language. Japanese and English are included, and English is the fallback for untranslated strings. To add a translation, place a JSON file such as `fr.json` next to `en.json`, using the same format. Preserve placeholders such as `{0}` in the translated strings.

## Preview requirements and limitations

Video and audio previews with sound require Tkinter and a compatible tkmedia3 installation. The add-on recognizes the `tkmedia` and `media` import names. Use **Audio Output** at the bottom of the window to select the system default, mute sound, or choose a device. The add-on saves this setting separately and applies it the next time playback starts. Image previews use Pillow.

When the installed tkmedia supports setting the video size, it scales decoded video to fit the preview. Older versions use Tk to downscale it. The seek bar requires PyAV to determine the playback duration. Seeking to a chapter starts at the corresponding clip, with accuracy depending on the decoder. Move between clips manually when previewing segmented titles. Playback may continue past a segment's endpoint within the source clip. Playback requires unencrypted media. Editing and saving are available even if the preview is unavailable.

## Exporting BDMV with menus

Install [bdmvkit](https://pypi.org/project/bdmvkit/) 0.7 and Pillow in the Python environment Marutools uses. Put `ffmpeg` (with libx264 support) and `ffprobe` on your PATH. If you run Marutools with Poetry, install bdmvkit from the Marutools folder:

```bash
poetry run python -m pip install 'bdmvkit==0.7.0'
```

Open **Export** and choose a parent folder and a name for the new output folder. The same window shows conversion progress for each media item and reports when export completes. An activity bar appears while the menu and BDMV structure are being generated. **Stop Export** stops FFmpeg during media conversion. During final menu and BDMV generation, cleanup takes place once the current operation finishes. Export requires an unused destination name.

The exporter generates an HDMV BDMV folder from the current media order, chapters, menu backgrounds, layout, images, text, and links. Legacy menu buttons are grouped into pages of four. Assign any missing button links before export. If the first page has no linked items, export adds a **Play** button that opens the first title.

Export uses 1080p video at 23.976 fps and AC-3 stereo audio. Still images are displayed for five seconds, and audio-only media plays over a black screen. Chapter marks align with keyframes in the exported video. Japanese menu text requires a system font with Japanese glyphs. Burning to a physical disc is currently unsupported.

**Reuse Encoded Media** is enabled by default. Encoded files are cached in `.marubd-cache/` next to the project, or in the chosen parent folder if the project has not been saved. Changing only the menu allows export to reuse media encoded with the same settings. Files that finished encoding and were saved to the cache before cancellation can be reused on the next export. To reclaim disk space, delete `.marubd-cache/` after export has finished.

### Video backgrounds, music, audio, subtitles, and pop-up menus

- In the **Menu** tab, open **Background and Music…**. Select a registered video as the background or an audio file as the music. The layout canvas shows the first frame of a background video. The exported menu loops at the end of the background video, or at the end of the music if the background is a still image. Audio from the background video is muted.
- Select a title in the **Media** tab and open **Audio, Subtitles and Pop-up…**. The source audio is included. You can also add external audio and UTF-8 SRT or Blu-ray PGS (SUP) subtitles. Each audio track is encoded as AC-3 stereo. Subtitles are included as PGS. To include subtitles embedded in the source video, add them as separate subtitle files.
- Enable **Add an in-playback pop-up menu** in the same dialog. During playback, use the player's **Pop-up Menu** key to return to the top menu, jump to a chapter, switch audio tracks, or turn subtitles on or off. The add-on lays out up to 48 buttons per title from the available options.

### Blu-ray ISO

Install [udfkit](https://pypi.org/project/udfkit/0.2.0/) 0.2.0 in the same Python environment:

```bash
poetry run python -m pip install 'udfkit==0.2.0'
```

In the export settings, set **Output format** to **Blu-ray ISO (UDF 2.50)**. This creates an `.iso` file containing the edited menus. ISO and BDMV folder exports share the encoded media cache.

### Video encoder

Use **Video encoder** in the export settings to choose among the CPU and hardware H.264 encoders built into FFmpeg. CPU encoding with libx264 is the default when available. Hardware encoding requires a compatible GPU and driver. With VAAPI, specify the device as well. The selected encoder is used for final H.264 encoding of title video, and the cache is kept per encoder. Decoding, some preprocessing, and menu encoding use the CPU.
