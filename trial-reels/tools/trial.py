"""Render one trial-reel variant of The Bus Story.
usage: trial.py SRC OUT FONTDIR [--hook "text"] [--sat up|down] [--speed fast|slow] [--warm]
Original hook: Montserrat Medium 59.5px, black on a white rounded box x145-934 y688-812, frames 0-73 (cut at 2.4667s)."""
import argparse, os, re, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

p = argparse.ArgumentParser()
p.add_argument('src'); p.add_argument('out'); p.add_argument('fontdir')
p.add_argument('--hook'); p.add_argument('--sat', choices=['up', 'down']); p.add_argument('--speed', choices=['fast', 'slow'])
p.add_argument('--warm', action='store_true')
a = p.parse_args()

filters, inputs = [], ['-i', a.src]
grade = []
if a.sat == 'up': grade.append('eq=saturation=1.12')
if a.sat == 'down': grade.append('eq=saturation=0.92')
if a.warm: grade.append('colorbalance=rs=0.03:bs=-0.03:rm=0.035:bm=-0.035:rh=0.02:bh=-0.02')
filters.append(f"[0:v]{','.join(grade) or 'null'}[g]"); v = '[g]'

def hook_frames():
    """source frames (from 0) that show the original white hook box. The new box goes on exactly these frames, BEFORE
    the speed change, so every frame carries its own caption and it can never spill into the next shot"""
    r = subprocess.run(['ffmpeg', '-v', 'error', '-t', '5', '-i', a.src, '-vf', 'crop=760:90:160:705,scale=1:1,format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True, check=True)
    n = 0
    while n < len(r.stdout) and r.stdout[n] > 150: n += 1     # white box with black text averages ~200; next shot is dark
    assert 30 < n < 120, f'unexpected hook length: {n} frames'
    return n

if a.hook:
    cut = hook_frames()
    font = ImageFont.truetype(os.path.join(a.fontdir, 'Montserrat-500.ttf'), 59.5)
    b = font.getbbox(a.hook); tw = b[2] - b[0]
    assert tw <= 938, f'hook too wide for one line inside the safe zone: {tw}px'
    bw = max(tw + 72, 934 - 145 + 1 + 4)           # never narrower than the original box (+2px each side)
    x0 = round(539.5 - bw / 2); x1 = x0 + bw
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, 686, x1, 814), radius=22, fill=(254, 255, 253, 255))
    d.text((round(539.5 - tw / 2) - b[0], 723 - b[1]), a.hook, font=font, fill=(0, 0, 0, 255))
    png = os.path.join(tempfile.mkdtemp(), 'hook.png'); img.save(png)
    inputs += ['-loop', '1', '-framerate', '30', '-i', png]
    filters.append(f"{v}[1:v]overlay=0:0:shortest=1:enable='lt(n,{cut})'[h]"); v = '[h]'
    print('new hook on source frames 0 -', cut - 1)

amap = '0:a'
if a.speed:
    f = 1.07 if a.speed == 'fast' else 0.93
    filters.append(f"{v}split[va][vb];[va]trim=0:1,setpts=(PTS-STARTPTS)/{f}[v1];[vb]trim=start=1,setpts=PTS-STARTPTS[v2];"
                   f"[0:a]asplit[aa][ab];[aa]atrim=0:1,asetpts=PTS-STARTPTS,atempo={f}[a1];[ab]atrim=start=1,asetpts=PTS-STARTPTS[a2];"
                   f"[v1][a1][v2][a2]concat=n=2:v=1:a=1[cv][ca];[cv]fps=30[s]")
    v, amap = '[s]', '[ca]'
filters.append(f"{v}format=yuv420p[out]")
cmd = ['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters), '-map', '[out]', '-map', amap,
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-color_primaries', 'bt709', '-color_trc', 'bt709',
       '-colorspace', 'bt709', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-movflags', '+faststart', a.out]
subprocess.run(cmd, check=True)
print('ok', a.out)
