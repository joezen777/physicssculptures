"""Compose annotated previews from FreeCAD's actual rendered frames."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
import json

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,bold=False):return ImageFont.truetype(BOLD if bold else REG,n)
p=json.loads((OUT/"physics.json").read_text())
def compose(src,seconds=None):
    canvas=Image.new("RGB",(1440,1000),"#edf2f7")
    d=ImageDraw.Draw(canvas)
    d.rectangle((0,0,1440,142),fill="#112c40")
    d.text((40,24),"PHYSICS EXPERIMENT  /  01",font=font(17,True),fill="#80cce7")
    d.text((40,58),"Falling cylinder / planetary cascade",font=font(36,True),fill="white")
    d.text((40,108),"Six pitched fins  |  Three balanced stages  |  Evacuated interior",font=font(18),fill="#c6d8e5")
    im=Image.open(src).convert("RGB")
    mask=ImageChops.difference(im,Image.new("RGB",im.size,"white")).convert("L").point(lambda x:255 if x>28 else 0)
    box=mask.getbbox()
    if box:
        x0,y0,x1,y1=box
        im=im.crop((max(0,x0-25),max(0,y0-25),min(im.width,x1+25),min(im.height,y1+25)))
    im.thumbnail((855,730))
    d.rounded_rectangle((25,163,915,932),radius=18,fill="white")
    canvas.paste(im,(470-im.width//2,540-im.height//2))
    d.text((45,885),"Actual FreeCAD cutaway geometry | millimetres",font=font(16),fill="#586c7b")
    d.rounded_rectangle((940,163,1415,932),radius=18,fill="white")
    x=965
    d.text((x,188),"THREE LEVELS, ONE AXIS",font=font(22,True),fill="#112c40")
    y=236
    for color,title,sub in [
        ("#277aad","Shell + carriers","Upper fins drive the first carrier"),
        ("#aa68d3","Reaction drum + rings","Independent rotation; not grounded"),
        ("#24b684","Three planets per stage","120 degree spacing / 24 teeth each"),
        ("#e9a022","Sun gears + output","24 teeth; drives next level down")]:
        d.ellipse((x,y+3,x+17,y+20),fill=color)
        d.text((x+30,y),title,font=font(18,True),fill="#19384d")
        d.text((x+30,y+28),sub,font=font(15),fill="#647786")
        y+=72
    d.line((x,533,1390,533),fill="#d8e1e9",width=2)
    d.text((x,552),"AT SHELL = 300 RPM",font=font(20,True),fill="#112c40")
    d.text((x,588),"Reaction held:  1,200 > 4,800 > 19,200",font=font(17),fill="#19384d")
    d.text((x,620),f"Free drum: bottom ~{p['free_bottom_per_shell']*300:,.0f} RPM",font=font(19,True),fill="#724ba0")
    d.text((x,653),"Free result assumes lossless startup",font=font(15),fill="#647786")
    d.text((x,676),"and the CAD model's illustrative inertias.",font=font(15),fill="#647786")
    d.rounded_rectangle((x,722,1390,812),radius=10,fill="#edf5fa")
    d.text((x+14,735),"bottom = 64 x shell - 63 x reaction",font=font(18,True),fill="#19384d")
    d.text((x+14,768),"64:1 is relative to the reaction drum.",font=font(16),fill="#536c7d")
    d.text((x,839),"No aerodynamic RPM prediction.",font=font(18,True),fill="#19384d")
    d.text((x,872),"Concept only; bearings and seals omitted.",font=font(15),fill="#647786")
    footer="STATIC ASSEMBLY  |  Full and cutaway STEP supplied"
    if seconds is not None:
        footer=f"IDEAL RESTRAINED REACTION  |  1,800x slow motion  |  visual time {seconds:04.1f} s"
    d.text((40,955),footer,font=font(18,True),fill="#19384d")
    return canvas

compose(OUT/"overview.png").save(OUT/"annotated_overview.png")
frames=sorted((OUT/"frames").glob("*.png"))
if len(frames)!=72:raise SystemExit(f"Expected 72 frames, got {len(frames)}; wait for FreeCAD rendering.")
images=[compose(f,i/12).resize((1152,800)).quantize(colors=128) for i,f in enumerate(frames)]
images[0].save(OUT/"gearbox_animation.gif",save_all=True,append_images=images[1:],duration=[83,83,84]*24,loop=0,disposal=2)
print("Saved annotated_overview.png and gearbox_animation.gif")
