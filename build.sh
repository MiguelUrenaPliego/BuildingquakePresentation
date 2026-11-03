#!/bin/sh
# Rebuilds index.html + PNG exports. Non-video slides: normal render; video slides: transparent, video removed.
cd "$(dirname "$0")"; export CHROME_PATH=/usr/bin/chromium
mkdir -p export/normal export/png slides_export
sed -e 's/^theme: emergence$/theme: emergence-export/' -e 's#<video[^>]*></video>##' -e 's#\./logos/#../logos/#g' -e 's#\./images/#../images/#g' -e 's#\./figures/#../figures/#g' presentation.md > export/presentation_export.md
O="--html --allow-local-files --browser-timeout 60"
marp presentation.md --theme-set theme $O --images png --image-scale 2 -o export/normal/slide.png
(cd export && marp presentation_export.md --theme-set ../theme $O --images png --image-scale 2 -o png/slide.png)
python3 - <<'P'
import shutil
parts = open('presentation.md').read().split('\n---\n')[1:]   # [0] is the front matter
for n, p in enumerate(parts, 1):
    if '<video' in p:
        shutil.copy(f'export/png/slide.{n:03d}.png', f'slides_export/slide_{n:02d}_video_transparent.png')
    else:
        shutil.copy(f'export/normal/slide.{n:03d}.png', f'slides_export/slide_{n:02d}.png')
print(len(parts), 'slides exported')
P
marp presentation.md --theme-set theme $O -o index.html
echo DONE
