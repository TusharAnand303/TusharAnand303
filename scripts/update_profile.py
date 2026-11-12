#!/usr/bin/env python3
"""GitHub-native SVG profile charts. Python stdlib only; no third-party chart APIs.

Uses GITHUB_TOKEN in GitHub Actions to load public contribution information
from GitHub's GraphQL API, then commits SVGs to this repository.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, timedelta
import json
import math
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
USER = os.environ.get('PROFILE_USERNAME', 'TusharAnand303')
BG = '#0d1117'
PANEL = '#111827'
BORDER = '#30363d'
WHITE = '#e6edf3'
MUTED = '#8b949e'
BLUE = '#58a6ff'
CYAN = '#2dd4bf'
PURPLE = '#a78bfa'
GREEN = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']

QUERY = '''
query ($login: String!) {
  user(login: $login) {
    login
    followers { totalCount }
    repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER,
                 isFork: false, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      nodes {
        name
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { date contributionCount weekday } }
      }
    }
  }
}
'''


def api_data():
    token = os.environ.get('GITHUB_TOKEN', '')
    if not token:
        raise RuntimeError('GITHUB_TOKEN is not set; run this through GitHub Actions or supply a token')
    body = json.dumps({'query': QUERY, 'variables': {'login': USER}}).encode('utf-8')
    req = Request('https://api.github.com/graphql', data=body, headers={
        'Authorization': f'Bearer {token}', 'Content-Type': 'application/json',
        'Accept': 'application/vnd.github+json', 'User-Agent': 'github-profile-svg-builder',
    }, method='POST')
    with urlopen(req, timeout=30) as res:
        parsed = json.load(res)
    if parsed.get('errors'):
        raise RuntimeError('GraphQL returned errors: '+str(parsed['errors'])[:900])
    u = parsed.get('data', {}).get('user')
    if not u:
        raise RuntimeError('GitHub GraphQL did not return user: ' + USER)
    return u


def txt(x, y, s, size=15, fill=WHITE, weight=400, anchor=None, **extra):
    attrs = f' x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}"'
    if anchor: attrs += f' text-anchor="{anchor}"'
    for k,v in extra.items(): attrs += f' {k.replace("_", "-")}="{escape(str(v))}"'
    return f'<text{attrs}>{escape(str(s))}</text>'


def rect(x,y,w,h,fill=BG,r=0,stroke=None,sw=1,other=''):
    rattr = f' rx="{r}"' if r else ''
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{rattr}{st}{other}/>'


def svg(content, width, height, title, animation=''):
    safe = escape(title)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{safe}">' 
            f'<title>{safe}</title><style>text{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif}}{animation}</style>'
            f'{rect(1,1,width-2,height-2,BG,14,BORDER)}{content}</svg>')


def write(name, xml):
    ASSETS.mkdir(exist_ok=True, parents=True)
    (ASSETS / name).write_text(xml + '\n', encoding='utf-8')


def placeholder(name, title, caption, width=1000, height=250):
    content = txt(34,43,title,23,WHITE,700)
    content += '<g opacity="0.28">'
    for i in range(6):
        y = 80+i*23
        content += f'<line x1="36" y1="{y}" x2="{width-36}" y2="{y}" stroke="{BORDER}"/>'
    content += '</g>'
    content += txt(width//2, height//2+5, 'Chart refresh not run yet', 21, BLUE, 600, 'middle')
    content += txt(width//2, height//2+34, 'Actions → Refresh profile charts → Run workflow', 15, MUTED, 400, 'middle')
    content += txt(34, height-25, caption, 13, MUTED)
    write(name, svg(content,width,height,title))


def draw_activity(weeks):
    width,height=1000,288
    counts=[sum(max(0,d['contributionCount']) for d in w['contributionDays']) for w in weeks[-52:]]
    if not counts: raise RuntimeError('Contribution calendar returned no weeks')
    xmin,xmax,ymin,ymax=50,966,87,244
    mx=max(1,max(counts))
    yvalue=lambda v: ymax-(v/mx)*(ymax-ymin)
    pts=[(xmin+(xmax-xmin)*i/max(1,len(counts)-1),yvalue(val)) for i,val in enumerate(counts)]
    path=' '.join(('M' if i==0 else 'L')+f'{x:.1f},{y:.1f}' for i,(x,y) in enumerate(pts))
    area=path+f' L{xmax:.1f},{ymax} L{xmin:.1f},{ymax} Z'
    content=txt(32,41,'Contribution activity',23,WHITE,700)
    content+=txt(965,41,'LAST 52 WEEKS',12,MUTED,700,'end',letter_spacing='1.1')
    for i in range(5):
        y=ymax-(ymax-ymin)*i/4
        content+=f'<line x1="{xmin}" y1="{y:.1f}" x2="{xmax}" y2="{y:.1f}" stroke="{BORDER}" stroke-dasharray="4 6"/>'
        content+=txt(xmin-8, y+4, f'{round(mx*i/4)}', 11,MUTED,400,'end')
    content+=f'<path d="{area}" fill="{BLUE}" opacity=".08"/>'
    content+=f'<path d="{path}" fill="none" stroke="{BLUE}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" class="trace"/>'
    last=pts[-1]
    content+=f'<circle cx="{last[0]}" cy="{last[1]}" r="5.6" fill="{CYAN}" stroke="{BG}" stroke-width="2"/>'
    content+=txt(xmin,272,'52 weeks ago',12,MUTED)
    content+=txt(xmax,272,'Now',12,MUTED,400,'end')
    css='@keyframes enter{from{stroke-dashoffset:2400}to{stroke-dashoffset:0}}.trace{stroke-dasharray:2400;animation:enter 2.2s ease-out both}@media(prefers-reduced-motion:reduce){.trace{animation:none;stroke-dasharray:none}}'
    write('activity.svg', svg(content,width,height,'GitHub contribution activity by week, live from GitHub',css))


def draw_calendar(weeks,total):
    width,height=1000,248
    weeks=weeks[-53:]
    x0,y0,step,cell=36,80,17,12
    content=txt(32,40,'Contribution calendar',23,WHITE,700)
    content+=txt(967,40, f'{total:,} contributions · last year',13,CYAN,600,'end')
    months_seen=set()
    for i,w in enumerate(weeks):
        for d in w['contributionDays']:
            dt=date.fromisoformat(d['date'])
            if dt.day<=7 and dt.month not in months_seen and d['weekday'] == 0:
                content+=txt(x0+i*step,68,dt.strftime('%b'),11,MUTED)
                months_seen.add(dt.month)
            value=d['contributionCount']
            shade=0 if value==0 else min(4,1+math.ceil(math.log2(value+1)/2))
            content+=rect(x0+i*step,y0+d['weekday']*step,cell,cell,GREEN[shade],2)
    content+=txt(35,226,'Contributions include commits, pull requests, issues and reviews.',12,MUTED)
    legend_x=778
    content+=txt(legend_x-12,202,'Less',11,MUTED,400,'end')
    for i,c in enumerate(GREEN): content+=rect(legend_x+i*22,192,13,13,c,2)
    content+=txt(legend_x+118,202,'More',11,MUTED)
    write('calendar.svg', svg(content,width,height,'GitHub yearly contribution heatmap'))


def draw_stats(user, total, daily_counts):
    width,height=1000,217
    repos=user['repositories']['nodes'] or []
    public_count=user['repositories']['totalCount']
    stars=sum(max(0,int(r['stargazerCount'])) for r in repos)
    follower=user['followers']['totalCount']
    day_contrib={date.fromisoformat(d['date']):d['contributionCount'] for d in daily_counts}
    today=max(day_contrib) if day_contrib else date.today()
    # Current streak counts up to most recent calendar date, allowing an unfinished current day.
    cur=today
    if day_contrib.get(cur,0)==0: cur-=timedelta(days=1)
    streak=0
    while day_contrib.get(cur,0)>0:
        streak+=1;cur-=timedelta(days=1)
    all_days=sorted(day_contrib)
    longest=0;run=0
    for day in all_days:
        if day_contrib[day]>0:
            run+=1;longest=max(run,longest)
        else: run=0
    content=txt(30,38,'At a glance',23,WHITE,700)
    data=[('CONTRIBUTIONS',total,BLUE),('PUBLIC PROJECTS',public_count,CYAN),('STARS',stars,PURPLE),('FOLLOWERS',follower,'#fbbf24')]
    for i,(label,value,color) in enumerate(data):
        x=31+i*244
        content+=rect(x,61,225,103,PANEL,11,BORDER)
        content+=txt(x+17,92,label,11,MUTED,700,letter_spacing='1.1')
        content+=txt(x+17,142,f'{value:,}',33,color,700)
    content+=txt(31,196,f'Current contribution streak: {streak} days',13,MUTED)
    content+=txt(967,196,f'Longest streak in last year: {longest} days',13,MUTED,400,'end')
    write('stats.svg', svg(content,width,height,'Current public GitHub profile statistics'))


def draw_languages(user):
    width,height=1000,306
    totals=Counter()
    colors={}
    for repo in user['repositories']['nodes'] or []:
        for edge in (repo.get('languages') or {}).get('edges') or []:
            if not edge or not edge.get('node'): continue
            lang=edge['node']['name']
            totals[lang]+=int(edge.get('size') or 0)
            colors[lang]=edge['node'].get('color') or BLUE
    top=totals.most_common(5)
    total=sum(totals.values())
    content=txt(30,39,'Languages across public projects',23,WHITE,700)
    content+=txt(30,62,'Measured by repository code bytes, not proficiency',12,MUTED)
    if not top or not total:
        content+=txt(500,155,'No public language breakdown yet',18,MUTED,400,'middle')
    else:
        for i,(lang,val) in enumerate(top):
            y=102+i*38
            pct=100*val/total
            content+=txt(30,y,lang,15,WHITE,600)
            content+=txt(965,y,f'{pct:.1f}%',13,MUTED,600,'end')
            content+=rect(340,y-15,540,12,'#21262d',6)
            # Graph bar fill.
            content+=rect(340,y-15,max(4,540*val/top[0][1]),12,colors[lang],6)
    write('languages.svg',svg(content,width,height,'Public GitHub repository language breakdown'))


def run():
    user=api_data()
    calendar=user['contributionsCollection']['contributionCalendar']
    weeks=calendar['weeks']
    days=[d for week in weeks for d in week['contributionDays']]
    draw_activity(weeks)
    draw_calendar(weeks,calendar['totalContributions'])
    draw_stats(user,calendar['totalContributions'],days)
    draw_languages(user)
    print(f'Updated four SVG charts for {user["login"]} using GitHub API. Last-year contributions: {calendar["totalContributions"]}')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--placeholders', action='store_true',help='create initial truthful placeholder SVGs without API calls')
    args=parser.parse_args()
    if args.placeholders:
        placeholder('activity.svg','Contribution activity','Weekly GitHub activity graph')
        placeholder('calendar.svg','Contribution calendar','Daily contribution heatmap',height=248)
        placeholder('stats.svg','At a glance','Profile metrics from the GitHub API',height=217)
        placeholder('languages.svg','Languages across public projects','Breakdown by repository code bytes',height=306)
    else:
        try: run()
        except Exception as exc:
            print(f'ERROR: {exc}',file=sys.stderr)
            sys.exit(1)
