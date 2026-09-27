"""Annotate actual FreeCAD renders and produce a portable animation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"output"
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
def compose(src,t=None):
    c=Image.new("RGB",(1480,1030),"#edf2f6");d=ImageDraw.Draw(c)
    d.rectangle((0,0,1480,138),fill="#132e42")
    d.text((36,21),"MECHANICAL STUDY / FIRST DRAFT",font=font(17,True),fill="#8bcfdc")
    d.text((36,55),"Stacking cones / staggered tooth rows",font=font(35,True),fill="white")
    d.text((36,103),"Two stages | 608 bearings | Hex coupling | Split ring inserts",font=font(19),fill="#cbdde8")
    d.rounded_rectangle((22,158,900,968),radius=16,fill="white")
    im=Image.open(src).convert("RGB")
    mask=ImageChops.difference(im,Image.new("RGB",im.size,"white")).convert("L").point(lambda x:255 if x>28 else 0)
    bb=mask.getbbox()
    if bb:
        x0,y0,x1,y1=bb
        im=im.crop((max(0,x0-20),max(0,y0-20),min(im.width,x1+20),min(im.height,y1+20)))
    im.thumbnail((830,748));c.paste(im,(461-im.width//2,551-im.height//2))
    d.text((43,938),"Actual FreeCAD cutaway; full housing also supplied.",font=font(16),fill="#586d7b")
    d.rounded_rectangle((922,158,1458,968),radius=16,fill="white")
    x=947
    d.text((x,180),"YOUR STACKING MECHANISM",font=font(23,True),fill="#17384e")
    y=227
    for color,title,sub in [
        ("#237faf","Rotating cone + removable cap","The cone carries the keyed ring inserts."),
        ("#9561c4","Two semicircular ring inserts","72 teeth per row; half-tooth stagger."),
        ("#e9a426","Center gear + hex connection","24 teeth; plugs into the next cone."),
        ("#28aa77","Three intermediate gears","24 teeth each, spaced 120 degrees apart."),
        ("#505b65","Stationary carrier and shaft","Holds the axles and reacts the torque.")]:
        d.ellipse((x,y+4,x+16,y+20),fill=color)
        d.text((x+29,y),title,font=font(19,True),fill="#183a50")
        d.text((x+29,y+30),sub,font=font(16),fill="#5a7180")
        y+=76
    d.line((x,610,1430,610),fill="#d9e3ea",width=2)
    d.text((x,635),"TWO ROWS ON EVERY GEAR",font=font(21,True),fill="#17384e")
    d.text((x,674),"Row A     tooth   gap   tooth   gap",font=font(18),fill="#34556b")
    d.text((x,704),"Row B     gap   tooth   gap   tooth",font=font(18),fill="#34556b")
    d.rounded_rectangle((x,756,1432,836),radius=10,fill="#edf5fa")
    d.text((x+13,768),"Fan 90 RPM > middle -30 > bottom 10",font=font(18,True),fill="#17384e")
    d.text((x+13,803),"Ideal 9x bottom torque; direction reverses twice.",font=font(16),fill="#536d7d")
    d.text((x,862),"Cylindrical teeth inside conical housings.",font=font(18,True),fill="#17384e")
    d.text((x,899),"Snap fits and bearing retention need fit tests.",font=font(16),fill="#6f6071")
    text="DRAFT 01 / Geometry and kinematics / Not a production print release"
    if t is not None:text=f"DRAFT 01 / bottom 3 deg/s, fan 27 deg/s / visual time {t:04.1f} s"
    d.text((36,993),text,font=font(18,True),fill="#214157")
    return c
compose(OUT/"tower_overview.png").save(OUT/"annotated_tower.png")
frames=sorted((OUT/"frames").glob("*.png"))
if len(frames)!=60:raise SystemExit(f"Expected 60 frames; found {len(frames)}")
images=[compose(f,i/12).resize((1184,824)).quantize(colors=128) for i,f in enumerate(frames)]
images[0].save(OUT/"tower_animation.gif",save_all=True,append_images=images[1:],
               duration=[83,83,84]*20,loop=0,disposal=2)
print("Saved annotated_tower.png and tower_animation.gif")
