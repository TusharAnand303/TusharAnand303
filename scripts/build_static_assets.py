#!/usr/bin/env python3
"""Build self-hosted hero + technology icon illustration (no network or APIs)."""
from pathlib import Path
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'; ASSETS.mkdir(exist_ok=True)

def start(w,h,title,defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title>'
            '<style>text{font-family:Inter,Segoe UI,Arial,sans-serif}</style>'+defs)

def rect(x,y,w,h,fill,rx=0,stroke=None):
    a=f' stroke="{stroke}"' if stroke else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{a}/>'

def text(x,y,value,size=18,color='#e6edf3',weight=400,anchor='start',spacing=None):
    s=f' letter-spacing="{spacing}"' if spacing is not None else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}"{s}>{escape(value)}</text>'

def hero():
    w,h=1000,230
    s=start(w,h,'Tushar Anand — Full-Stack Developer')
    s+='<defs><linearGradient id="back" x2="1" y2="1"><stop offset="0" stop-color="#0c1424"/><stop offset="1" stop-color="#101827"/></linearGradient><linearGradient id="line"><stop offset="0" stop-color="#58a6ff"/><stop offset="1" stop-color="#2dd4bf"/></linearGradient></defs>'
    s+=rect(1,1,w-2,h-2,'url(#back)',18,'#303f53')
    # subtle grid
    for x in range(520,1000,28):s+=f'<line x1="{x}" y1="0" x2="{x}" y2="230" stroke="#58a6ff" opacity=".055"/>'
    for y in range(20,230,28):s+=f'<line x1="500" y1="{y}" x2="1000" y2="{y}" stroke="#58a6ff" opacity=".055"/>'
    s+=rect(38,35,5,41,'url(#line)',2)
    s+=text(58,70,'TUSHAR ANAND',35,'#eef5ff',750,spacing='2')
    s+=text(58,112,'Full-Stack Software Developer',19,'#9cbad8',500)
    s+=text(58,153,'Building reliable web platforms, APIs & digital experiences.',17,'#c9d1d9')
    s+=text(58,190,'REACT   /   ANGULAR   /   NODE.JS   /   LARAVEL   /   POSTGRESQL',12,'#5eead4',700,spacing='1')
    # SVG code motif, simple pulse animation, static content remains when animation disabled.
    s+='<g transform="translate(752 53)" opacity=".95">'
    s+='<rect width="190" height="126" rx="14" fill="#111d2c" stroke="#2b3f54"/>'
    s+='<circle cx="19" cy="20" r="5" fill="#ff6873"/><circle cx="35" cy="20" r="5" fill="#ffd166"/><circle cx="51" cy="20" r="5" fill="#36d399"/>'
    s+='<path d="M26 73 L47 54 M26 73 L47 92 M159 54 L180 73 L159 92" fill="none" stroke="#58a6ff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    s+='<path d="M103 52 L79 96" fill="none" stroke="#2dd4bf" stroke-width="5" stroke-linecap="round"/>'
    s+='<rect x="115" y="106" width="29" height="3" rx="2" fill="#a78bfa"><animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></rect>'
    s+='</g></svg>'
    (ASSETS/'header.svg').write_text(s,encoding='utf-8')

TECH=[
 ('React','#61dafb','orbit'),('Angular','#e5484d','angular'),('TypeScript','#3178c6','TS'),
 ('JavaScript','#f7df1e','JS'),('Node.js','#80bd4b','node'),('Laravel','#ff5544','laravel'),
 ('PHP','#8b94c4','php'),('PostgreSQL','#4e93c3','database'),('MySQL','#f29111','database'),
 ('Git','#f1502f','git'),('Linux','#c1c8d0','terminal'),('Apache','#c857a0','feather')]

def icon(g,cx,cy,color):
    # Returns a recognizable vector/glyph (self-contained SVG, not a remote URL).
    if g=='orbit':
        e=''
        for deg in [0,60,120]:e+=f'<ellipse cx="{cx}" cy="{cy}" rx="20" ry="7" fill="none" stroke="{color}" stroke-width="2.4" transform="rotate({deg} {cx} {cy})"/>'
        return e+f'<circle cx="{cx}" cy="{cy}" r="4" fill="{color}"/>'
    if g=='angular':
        return f'<path d="M{cx} {cy-23} l19 8 -3 30 -16 9 -16 -9 -3 -30z" fill="{color}"/><path d="M{cx-10} {cy+13} l10 -24 10 24 m-15 -8 h10" stroke="white" stroke-width="3.2" stroke-linecap="round" fill="none"/>'
    if g=='node':
        return f'<path d="M{cx} {cy-24}l21 12 v24 l-21 12 -21-12 v-24z" fill="none" stroke="{color}" stroke-width="4"/>'+text(cx,cy+6,'JS',18,color,750,'middle')
    if g=='laravel':
        return f'<path d="M{cx-20} {cy-14} l15 -8 12 7 0 17 12 7 -18 10 -13 -7 0 -19 -8 -4z M{cx-5} {cy-22}v22 l17 -9" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>'
    if g=='database':
        return f'<ellipse cx="{cx}" cy="{cy-13}" rx="18" ry="8" fill="none" stroke="{color}" stroke-width="3"/><path d="M{cx-18} {cy-13}v26a18 8 0 0 0 36 0v-26 M{cx-18} {cy}a18 8 0 0 0 36 0" fill="none" stroke="{color}" stroke-width="3"/>'
    if g=='git':
        return f'<path d="M{cx} {cy-22}l22 22 -22 22 -22-22z" fill="{color}"/><path d="M{cx-9} {cy-9}l18 18 M{cx} {cy-18}v18l10 10" stroke="white" fill="none" stroke-width="2.5"/><circle cx="{cx-9}" cy="{cy-9}" r="3" fill="white"/><circle cx="{cx+10}" cy="{cy+10}" r="3" fill="white"/>'
    if g=='terminal':
        return f'<rect x="{cx-22}" y="{cy-18}" width="44" height="34" rx="6" fill="none" stroke="{color}" stroke-width="3"/><path d="M{cx-13} {cy-8}l8 8 -8 8 M{cx+1} {cy+8}h12" stroke="{color}" stroke-width="3" stroke-linecap="round" fill="none"/>'
    if g=='feather':
        return f'<path d="M{cx-12} {cy+20}q-2 -36 28 -45q7 31 -28 45z M{cx-12} {cy+20}l26 -35" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>'
    if g in ('TS','JS'):
        bg = '#3178c6' if g=='TS' else '#f7df1e'
        fg = 'white' if g=='TS' else '#1b1b1b'
        return rect(cx-23,cy-23,46,46,bg,6)+text(cx,cy+9,g,24,fg,750,'middle')
    return text(cx,cy+9,g,25,color,750,'middle')

def stack():
    w,h=1000,260
    s=start(w,h,'Technology stack: React, Angular, TypeScript, JavaScript, Node.js, Laravel, PHP, PostgreSQL, MySQL, Git, Linux and Apache')
    s+=rect(1,1,w-2,h-2,'#0d1117',16,'#30363d')
    for i,(name,color,glyph) in enumerate(TECH):
        row=i//6;col=i%6
        x=22+col*162;y=18+row*124
        s+=rect(x,y,146,108,'#161b22',12,'#30363d')
        s+=icon(glyph,x+73,y+46,color)
        s+=text(x+73,y+92,name,14,'#e6edf3',600,'middle')
    s+='</svg>'
    (ASSETS/'stack.svg').write_text(s,encoding='utf-8')

if __name__=='__main__':
    hero();stack()
