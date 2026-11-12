# Content-Editing

## How to handle videos I send you

I'll send videos by dragging them in or pasting a file path. They can be any size, from anywhere on my Mac or external drives (e.g. `/Volumes/Sam's Hardrive/...`). Never ask me to compress, shrink or re-upload a file. Work on it where it already is.

1. **Treat what I send as a local file path.** If the path has spaces, apostrophes or odd characters (like "Sam's Hardrive" or macOS screen-recording names with hidden spaces), quote it properly. If it doesn't open, use `ls` to find the exact filename.
2. **Probe first.** Before anything else, run `ffprobe` to get duration, resolution, fps, rotation and whether it has audio.
3. **To SEE the video, don't load the whole file.** Pull small pieces with ffmpeg into the scratchpad:
   - a contact sheet (e.g. `fps=1/3,scale=480:-1,tile=4x2`) for an overview
   - single frames at specific timestamps when you need detail
4. **To HEAR it**, extract the audio and transcribe it locally (e.g. whisper) when the words matter.
5. **Do all editing locally** with ffmpeg/Python. Never modify or overwrite the original file.
6. **Save finished renders next to the source file** (or wherever I say), with a clear name. Tell me the full path when done.
7. **Before a long render, show me one still frame** of the result so I can approve the look first.
8. **If I say "this one" or "the video" without a path**, check the newest files in the current folder and `~/Downloads`, say which one you think I mean, and confirm before starting.

### Cloud sessions

These rules assume Claude Code is running on the Mac (desktop app or `claude remote-control`). A cloud session can't see `/Volumes/...` or `~/Downloads` on the Mac. If a pasted path doesn't exist, say so in one line and suggest running the session locally or sharing the folder via Google Drive. Don't ask for compression.
