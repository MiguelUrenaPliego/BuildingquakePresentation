"""Builds two PowerPoint files from slides_export/ (run after build.sh; needs python-pptx + pillow).
  Buildingquake_slides.pptx       slide pictures only, speaker notes tell which video to insert (for Google Slides)
  Buildingquake_with_videos.pptx  videos embedded (autoplay, loop, muted); ~220 MB, for PowerPoint/Keynote
"""
import os, re, subprocess, tempfile
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Emu
from pptx.dml.color import RGBColor

SW, SH = 12192000, 6858000
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
parts = open('presentation.md').read().split('\n---\n')[1:]
os.makedirs('slides_export/jpg', exist_ok=True)

def timing(spid):
    return etree.fromstring(f'''<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>
<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>
<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>
<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>
</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>
</p:childTnLst></p:cTn>
<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>
<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>
<p:video><p:cMediaNode vol="0" showWhenStopped="0"><p:cTn id="7" repeatCount="indefinite" fill="hold" display="0"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>
</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>''')

def build(with_videos, out, posters):
    prs = Presentation(); prs.slide_width = Emu(SW); prs.slide_height = Emu(SH)
    blank = prs.slide_layouts[6]
    for n, p in enumerate(parts, 1):
        m = re.search(r'<video([^>]*)src="\./videos/([^"]+)"', p)
        s = prs.slides.add_slide(blank)
        s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor(0, 0, 0)
        if not m:
            png = f'slides_export/slide_{n:02d}.png'; jpg = f'slides_export/jpg/slide_{n:02d}.jpg'
            Image.open(png).convert('RGB').save(jpg, quality=95, subsampling=0)
            s.shapes.add_picture(jpg, 0, 0, SW, SH); continue
        name = m.group(2); overlay = f'slides_export/slide_{n:02d}_video_transparent.png'
        if with_videos:
            vw = int(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width', '-of', 'csv=p=0', 'videos/' + name]))
            crop = re.search(r'inset\(0 0 0 (\d+)px\)', m.group(1)); c = int(crop.group(1)) / vw if crop else 0.0
            mv = s.shapes.add_movie('videos/' + name, 0, 0, SW, SH, poster_frame_image=posters[name], mime_type='video/mp4')
            if c:
                blip = mv._element.find(f'.//{{{A}}}blip'); sr = etree.Element(f'{{{A}}}srcRect'); sr.set('l', str(int(c * 100000))); blip.addnext(sr)
            s._element.append(timing(mv.shape_id))
        else:
            s.notes_slide.notes_text_frame.text = f'Insert video: videos/{name} (Insert > Video; stretch over the whole slide, Arrange > Send to back; autoplay + loop in Format options).'
        s.shapes.add_picture(overlay, 0, 0, SW, SH)
    prs.save(out); print(out, os.path.getsize(out) // 1048576, 'MB')

with tempfile.TemporaryDirectory() as tmp:
    posters = {}
    for n in {re.search(r'src="\./videos/([^"]+)"', p).group(1) for p in parts if '<video' in p}:
        jp = os.path.join(tmp, n + '.jpg')
        subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', 'videos/' + n, '-frames:v', '1', '-vf', 'scale=1280:-2', jp]); posters[n] = jp
    build(False, 'slides_export/Buildingquake_slides.pptx', posters)
    build(True, 'slides_export/Buildingquake_with_videos.pptx', posters)
