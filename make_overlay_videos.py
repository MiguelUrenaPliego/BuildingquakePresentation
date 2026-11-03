"""Renders every video exactly as it appears on its slide (full-bleed, crops, raised INSAR, title + footer burned in).
Output: videos_with_overlay/<name>.mp4 (same names as the originals) (1920x1080, H.264 + AAC). Originals in videos/ are never modified.
Run after build.sh (needs the transparent overlays in slides_export/). Requires ffmpeg."""
import os, re, subprocess
W, H = 1920, 1080
parts = open('presentation.md').read().split('\n---\n')[1:]
os.makedirs('videos_with_overlay', exist_ok=True)
for n, p in enumerate(parts, 1):
    m = re.search(r'<video([^>]*)src="\./videos/([^"]+)"', p)
    if not m: continue
    name = m.group(2); crop = re.search(r'inset\(0 0 0 (\d+)px\)', m.group(1)); cpx = int(crop.group(1)) if crop else 0
    dy = -round(56 / 720 * H) if 'media scrim' in p else 0          # INSAR: raised, top cropped
    overlay = f'slides_export/slide_{n:02d}_video_transparent.png'
    out = f'videos_with_overlay/{name}'          # same file name as the original video
    fc = (f'[0:v]crop=iw-{cpx}:ih:{cpx}:0,scale={W}:{H},setsar=1[v];'
          f'color=c=black:s={W}x{H}:r=30[bg];[bg][v]overlay=0:{dy}:shortest=1[base];'
          f'[1:v]scale={W}:{H}[ov];[base][ov]overlay=0:0:format=auto,format=yuv420p[out]')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', 'videos/' + name, '-loop', '1', '-i', overlay, '-filter_complex', fc,
           '-map', '[out]', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '30',
           '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', out]
    print('rendering', out, flush=True); subprocess.check_call(cmd)
print('done')
