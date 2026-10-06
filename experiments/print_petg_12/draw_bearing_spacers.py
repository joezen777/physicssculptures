from pathlib import Path
import html
r=Path('/mnt/c/Users/josep/OneDrive/Documents/angularmomflyer')
out=r/'experiments/print_petg_12/output'
s=[]
def text(x,y,t,size=20,color='#243449',weight='normal'):
 s.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(t)}</text>')
def rect(x,y,w,h,c,stroke='none'):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" stroke="{stroke}" rx="3"/>')
def line(x,y,X,Y,c='#536478',width=2):
 s.append(f'<path d="M{x},{y} L{X},{Y}" fill="none" stroke="{c}" stroke-width="{width}"/>')
def circle(x,y,R,c):
 s.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="{c}"/>')
gold='#d99a25'; blue='#1684bb'; gray='#64748b'; pale='#eaf2f8'
s.append('<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1450" viewBox="0 0 1800 1450"><rect width="1800" height="1450" fill="#f5f8fc"/><g font-family="DejaVu Sans, sans-serif">')
text(50,58,'BEARING SPACERS: WHAT TOUCHES, WHAT TURNS',32,weight='bold')
text(50,94,'Four-level flowerpot turbine | Assembly cutaways, not a dimensioned bearing drawing',21)
for x,c,t in [(50,gold,'STATIONARY: spacers + inner rings'),(560,blue,'ROTATING: housing + outer ring'),(1070,gray,'Balls roll between the rings')]:
 rect(x,117,22,22,c);text(x+32,136,t,19)
rect(35,167,860,715,'white');rect(915,167,850,715,'white')
text(60,207,'A. CENTRAL 608 BEARING ON THE M8 ROD',24,weight='bold')
text(60,239,'Shown through the axis; left and right are one annular part.',18)
# Enlarged schematic bearing. Shaft x420..500; center 460.
rect(420,276,80,491,gray)
for y in range(290,760,15): line(422,y,498,y-9,'#94a3b8',1)
# spacers each side of shaft, clearance visible
for x in [391,505]:
 rect(x,315,24,120,gold);rect(x,575,24,130,gold)
# bearing inner/outer rings
for x in [382,500]: rect(x,435,38,140,gold)
for x in [266,620]: rect(x,435,38,140,blue)
for x in [343,577]:
 circle(x,505,27,gray)
 line(x-28,444,x+28,444,'#9cabb9',4);line(x-28,566,x+28,566,'#9cabb9',4)
# housing + outer retainers
rect(224,407,40,196,blue);rect(660,407,40,196,blue)
rect(224,407,88,26,blue);rect(608,407,92,26,blue)
rect(224,577,88,26,blue);rect(608,577,92,26,blue)
# contacts
for x in [391,505]:
 line(x,435,x+24,435,'#172c44',5);line(x,575,x+24,575,'#172c44',5)
text(70,300,'Spacer above',21,weight='bold');line(224,305,398,360)
text(70,335,'Clamped; does NOT turn',17)
text(70,470,'Printed hub',21,blue,'bold');line(185,478,236,492)
text(70,499,'+ outer ring turn',18,blue)
text(70,641,'Spacer below',21,weight='bold');line(233,637,398,634)
text(70,672,'Carries inner-ring load',17)
text(595,300,'M8 rod: fixed',21,gray,'bold');line(635,313,480,326)
text(715,443,'Inner ring',18,gold,'bold');line(706,451,530,468)
text(715,471,'stays fixed',17)
text(705,641,'Black lines:',18,weight='bold');text(705,668,'contact faces',17);line(710,620,520,575)
text(65,802,'Tube ends touch ONLY the inner-ring faces.',23,weight='bold')
text(65,836,'Keep clear of shields, balls, outer rings and printed rotating parts.',18)
# planet panel
text(940,207,'B. PLANET GEAR: 604 BEARING / M4 AXLE',24,weight='bold')
# axis 1240
rect(1220,279,40,505,gray)
rect(1183,288,114,30,gold);text(1350,310,'M4 nut + narrow washer: fixed',18);line(1337,310,1280,310)
rect(1183,318,114,13,gold)
for x in [1194,1266]:rect(x,331,20,89,gold)
text(1350,374,'10 mm upper spacer',20);line(1337,377,1280,374)
for x in [1180,1260]:rect(x,420,40,90,gold)
for x in [1080,1360]:rect(x,420,35,90,blue)
for x in [1147,1330]:circle(x,465,20,gray)
rect(1048,396,30,139,blue);rect(1397,396,30,139,blue)
for x in [1048,1351]:
 rect(x,396,76,22,blue);rect(x,512,76,23,blue)
text(1460,447,'P07 gear + P08 cap',18,blue,'bold');text(1460,477,'+ outer ring',18,blue,'bold')
text(1460,507,'rotate together.',18,blue);line(1450,467,1408,467)
for x in [1194,1266]:rect(x,510,20,183,gold)
text(1350,644,'37.2 mm lower spacer',20);line(1335,648,1280,639)
rect(1183,694,114,26,gold)
rect(1080,724,322,35,gray);text(1430,748,'P04: fixed',19);line(1420,742,1380,742)
rect(1192,762,96,24,gray)
text(940,805,'Both spacers clamp the 604 INNER ring.',23,weight='bold')
text(940,838,'Axle bolt, nuts, washer and carrier stay stationary.',19)
# bottom
rect(35,904,1730,501,'white')
text(60,945,'C. WHAT ROTATES TOGETHER',25,weight='bold')
text(60,977,'All CW / CCW directions are viewed from ABOVE. Example: bottom input turns CCW.',20)
rows=[
('LEVEL 4','CW  8x','P17 top fan + its P01 cap; driven by stage 3 sun'),
('LEVEL 3','CCW  4x','P02 pot + P09 ring + P11 collar; driven by stage 2 sun'),
('LEVEL 2','CW  2x','P03 pot + P09 ring + P10 collar; driven by stage 1 sun'),
('LEVEL 1','CCW  1x','P02 pot + P09 ring + P10 collar + P13-P16 wind drive')]
for i,(a,b,c) in enumerate(rows):
 y=1002+i*65
 rect(60,y,1010,54,pale);text(76,y+34,a,20,weight='bold');text(212,y+34,b,22,blue,'bold');text(355,y+33,c,17)
text(1110,1016,'At EACH gear stage:',22,weight='bold')
text(1110,1054,'Ring (72 teeth): input speed',19)
text(1110,1089,'Planets (18): same direction, 4x input',19)
text(1110,1124,'Sun (36): opposite direction, 2x input',19)
text(1110,1159,'P05 + P06 + attached P01 turn together.',18)
text(1110,1192,'The sun hex drives the next fan/pot.',18)
text(60,1302,'FIXED THROUGHOUT: P12 base, M8 rod, all spacers, all bearing inner rings, P04 carriers,',20,weight='bold')
text(60,1335,'planet axle hardware, and P18/P19 top guard. Planet centers stay in place; they do not orbit.',20)
text(60,1375,'Reverse the wind input and every rotation arrow reverses. The speed ratios remain unchanged.',18)
s.append('</g></svg>')
svg=out/'bearing_spacers_motion.svg';svg.write_text(''.join(s))
from PySide6 import QtCore,QtGui,QtSvg
app=QtGui.QGuiApplication.instance() or QtGui.QGuiApplication([])
im=QtGui.QImage(1800,1450,QtGui.QImage.Format_ARGB32);im.fill(QtGui.QColor('white'))
p=QtGui.QPainter(im);QtSvg.QSvgRenderer(str(svg)).render(p);p.end()
im.save(str(out/'bearing_spacers_motion.png'))
print(svg)
