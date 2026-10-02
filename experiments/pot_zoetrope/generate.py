"""Generate closed-path zoetrope relief artwork for the modular flowerpot."""
from pathlib import Path
import math, json, argparse
from xml.etree import ElementTree as ET

TAU=2*math.pi
N=24
ROOT=Path(__file__).resolve().parent

def build(bottom=120., top=168., height=58.):
    if not 0 < bottom < top or height < 40:
        raise ValueError("Expected an outward taper and at least 40 mm body height")
    rb,rt=bottom/2,top/2
    slant=math.hypot(height,rt-rb)
    q=(rt-rb)/slant
    angle=TAU*q
    width=math.pi*(rb+rt)
    rho0,rho1=rb/q,rt/q
    # Bound the complete developed frustum, not just the relief shapes.
    edge=[(r*math.sin(-angle/2+i*angle/400),
           -r*math.cos(-angle/2+i*angle/400))
          for r in (rho0,rho1) for i in range(401)]
    xmin=min(x for x,y in edge); ymin=min(y for x,y in edge)
    xmax=max(x for x,y in edge); ymax=max(y for x,y in edge)
    def mapped(pt):
        x,y=pt
        z=height-y
        rho=(rb+(rt-rb)*z/height)/q
        phi=(x/width-.5)*angle
        return rho*math.sin(phi)-xmin,-rho*math.cos(phi)-ymin

    def scene(j,reverse):
        # Positive pot rotation is CCW viewed from above.
        phase=((j if reverse else -j)/N)%1
        cx=(j+.5)*width/N
        objects=[]
        for row in range(5):
            side=-1 if row%2==0 else 1
            a=-side*.36
            x=side*2.6
            y=height*(9+9*row)/58
            points=[]
            for dx,dy in [(-2,0),(2,0),(2,1),(-2,1)]:
                points.append((cx+x+dx*math.cos(a)-dy*math.sin(a),
                               y+dx*math.sin(a)+dy*math.cos(a)))
            objects.append((f'frame-{j:02}-platform-{row}',points))
        stage=min(3,int(phase*4)); u=phase*4-stage
        side=-1 if stage%2==0 else 1
        radius=.8; contact_offset=radius+.35
        x0=side*2.6-side*contact_offset*math.sin(.36)
        x=cx+x0*(1-2*u)
        y=height*(9+9*stage+9*u-19*u*(1-u))/58-contact_offset*math.cos(.36)
        points=[(x+radius*math.cos(i*TAU/96),y+radius*math.sin(i*TAU/96)) for i in range(96)]
        objects.append((f'frame-{j:02}-ball',points))
        return objects

    def densify(points):
        result=[]
        for a,b in zip(points,points[1:]+points[:1]):
            count=max(1,math.ceil(math.dist(a,b)/.15))
            result.extend((a[0]+(b[0]-a[0])*i/count,a[1]+(b[1]-a[1])*i/count) for i in range(count))
        return result

    def path(points):
        return 'M '+' L '.join(f'{x:.5f},{y:.5f}' for x,y in points)+' Z'

    output=ROOT/'output'; output.mkdir(exist_ok=True)
    report={'pot_mm':{'bottom_diameter':bottom,'top_diameter':top,'body_height':height},
            'frames':N,'platforms_per_frame':5,'ball_diameter_mm':1.6,
            'platform_mm':[4,1],'contact_gap_mm':.35,
            'suggested_relief_mm':.5,'uv_width_mm':width,
            'slant_height_mm':slant,'sector_angle_degrees':math.degrees(angle),
            'developed_page_mm':[xmax-xmin,ymax-ymin],'files':{}}
    for reverse in (False,True):
        direction='cw' if reverse else 'ccw'
        shapes=[item for j in range(N) for item in scene(j,reverse)]
        for kind in ('cone-wrap','uv-strip'):
            w,h=(xmax-xmin,ymax-ymin) if kind=='cone-wrap' else (width,height)
            pieces=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.5f}mm" height="{h:.5f}mm" viewBox="0 0 {w:.5f} {h:.5f}">',
                    f'<title>Bouncing ball zoetrope - {direction.upper()} from above - {kind}</title>',
                    '<desc>24 frames, five tilted platforms and one ball per frame. Filled closed paths only. Black shapes are raised relief. No border is part of the emboss artwork. Cone wrap is a developed frustum; UV strip uses angle and axial height.</desc>',
                    '<g id="raised-relief" fill="#000000" stroke="none">']
            for name,pts in shapes:
                pts=[mapped(p) for p in densify(pts)] if kind=='cone-wrap' else pts
                assert all(-.001<=x<=w+.001 and -.001<=y<=h+.001 for x,y in pts)
                pieces.append(f'<path id="{name}" d="{path(pts)}"/>')
            pieces.extend(['</g>','</svg>'])
            target=output/f'ball-{kind}-{direction}.svg'
            target.write_text('\n'.join(pieces)+'\n')
            parsed=ET.parse(target)
            paths=parsed.findall('.//{http://www.w3.org/2000/svg}path')
            assert len(paths)==144 and all(p.get('d').endswith(' Z') for p in paths)
            report['files'][target.name]={'closed_paths':len(paths),'width_mm':w,'height_mm':h}
    # Separate outline for layout alignment: not emboss geometry.
    outline=[]
    for i in range(401):
        x=i*width/400
        outline.append(mapped((x,0)))
    for i in range(401):
        x=(400-i)*width/400
        outline.append(mapped((x,height)))
    guide=output/'cone-wrap-alignment-guide.svg'
    guide.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{xmax-xmin:.5f}mm" height="{ymax-ymin:.5f}mm" viewBox="0 0 {xmax-xmin:.5f} {ymax-ymin:.5f}"><title>Alignment outline only - do not emboss</title><path d="{path(outline)}" fill="none" stroke="#808080" stroke-width="0.2"/></svg>\n')
    (output/'dimensions.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--bottom-diameter',type=float,default=120)
    parser.add_argument('--top-diameter',type=float,default=168)
    parser.add_argument('--height',type=float,default=58)
    a=parser.parse_args()
    build(a.bottom_diameter,a.top_diameter,a.height)
