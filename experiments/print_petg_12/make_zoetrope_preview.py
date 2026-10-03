from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/"pot_zoetrope/output"
def font(n,bold=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",n)
for raw,out,title,subtitle in [
    ("zoetrope_pots_raw.png","zoetrope_pots_preview.png","P02 + P03 | ENGRAVED BOUNCING-BALL ZOETROPE","P02: CCW, levels 1 and 3     |     P03: CW, level 2     |     directions viewed from above"),
    ("zoetrope_etch_closeup_raw.png","zoetrope_etch_closeup.png","0.6 mm RECESSED ARTWORK","24 frames around each pot; five platforms and one ball per frame")]:
    pic=Image.open(OUT/raw).convert("RGB");im=Image.new("RGB",(pic.width,pic.height+220),"white");im.paste(pic,(0,130))
    d=ImageDraw.Draw(im);d.text((45,25),title,font=font(40,True),fill="#173546")
    d.text((45,82),subtitle,font=font(24),fill="#354a55")
    d.text((45,im.height-65),"Dark recess floors show the engraving; printed contrast depends on material, finishing and lighting.",font=font(23),fill="#354a55")
    im.save(OUT/out)
print("Zoetrope preview images saved.")
