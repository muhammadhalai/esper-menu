#!/usr/bin/env python3
"""Build esper-menu.html: real HTML for every service, JS only adds behaviour."""
import json, re, html, io

MENU = json.load(open('menu.json', encoding='utf-8'))
LOGO = open('logo_datauri.txt', encoding='utf-8').read().strip()

PILL_HIDE = ["Treatment", "Full set", "Service"]


def e(t):
    return html.escape(str(t), quote=True)


def num(n):
    return f"{n:,}"


def card_html(item, key):
    o = item['o']
    only = len(o) == 1
    body_id = 'd-' + re.sub(r'[^A-Za-z0-9]+', '-', key)
    w = io.StringIO()
    w.write(f'<article class="card v2" data-key="{e(key)}">')
    w.write(f'<div class="toprow"><h3 class="sname">{e(item["n"])}</h3></div>')
    w.write(f'<p class="hook">{e(item["h"])}</p>')
    if item.get('flag'):
        w.write(f'<span class="flag">{e(item["flag"])}</span>')
    w.write('<div class="opts">')
    for oi, op in enumerate(o):
        cls = 'opt fixed' if only else 'opt'
        attrs = ' disabled' if only else f' aria-pressed="{"true" if oi == 0 else "false"}"'
        inner = ''
        if op['l'] not in PILL_HIDE:
            inner += e(op['l']) + '<span class="dot">·</span>'
        inner += f'<span class="amt">{num(op["p"])}</span>'
        w.write(f'<button type="button" class="{cls}" data-oi="{oi}"{attrs}>{inner}</button>')
    w.write('</div>')
    if item.get('note'):
        w.write(f'<p class="note">{e(item["note"])}</p>')
    w.write('<div class="cardfoot">')
    w.write(f'<button type="button" class="discl" aria-expanded="false" aria-controls="{body_id}">'
            f'<span class="lbl-full">What this involves</span>'
            f'<span class="lbl-short">Details</span>'
            f'<span class="pm">+</span></button>')
    w.write('<div class="addzone">')
    w.write('<button type="button" class="addbtn" aria-pressed="false">Add to my visit</button>')
    w.write(f'<div class="stepper" hidden>'
            f'<button type="button" class="stepbtn" aria-label="One fewer {e(item["n"])}">−</button>'
            f'<span class="qty">1</span>'
            f'<button type="button" class="stepbtn" aria-label="One more {e(item["n"])}">+</button>'
            f'</div>')
    w.write('</div></div>')
    w.write(f'<div class="detailbody" id="{body_id}" hidden>{e(item["d"])}</div>')
    w.write('</article>')
    return w.getvalue()


def build():
    tabs, panels, slim = io.StringIO(), io.StringIO(), []

    for ti, tab in enumerate(MENU):
        sel = 'true' if ti == 0 else 'false'
        tabs.write(f'<button type="button" class="tab" id="tab-{e(tab["id"])}" role="tab" '
                   f'aria-selected="{sel}" aria-controls="panel-{e(tab["id"])}">{e(tab["label"])}</button>')

        hid = '' if ti == 0 else ' data-inactive'
        panels.write(f'<section id="panel-{e(tab["id"])}" role="tabpanel" '
                     f'aria-labelledby="tab-{e(tab["id"])}"{hid}>')

        multi = len(tab['groups']) > 1
        if multi:
            panels.write(f'<div class="xscroll"><div class="subrail" role="tablist" '
                         f'aria-label="{e(tab["label"])} sections">')
            for gi, g in enumerate(tab['groups']):
                gid = f'{tab["id"]}-{g["id"]}'
                s = 'true' if gi == 0 else 'false'
                panels.write(f'<button type="button" class="subtab" id="sub-{e(gid)}" role="tab" '
                             f'aria-selected="{s}" aria-controls="grp-{e(gid)}">{e(g["label"])}</button>')
            panels.write('</div></div>')

        slim_groups = []
        for gi, g in enumerate(tab['groups']):
            gid = f'{tab["id"]}-{g["id"]}'
            if multi:
                hg = '' if gi == 0 else ' data-inactive'
                panels.write(f'<div id="grp-{e(gid)}" role="tabpanel" aria-labelledby="sub-{e(gid)}"{hg}>')
            else:
                panels.write(f'<div id="grp-{e(gid)}">')

            panels.write(f'<div class="sectionhead"><h2>{e(g["title"])}</h2>')
            if g.get('blurb'):
                panels.write(f'<p>{e(g["blurb"])}</p>')
            panels.write('</div>')

            if g.get('intro'):
                panels.write(f'<div class="intro"><strong>{e(g["intro"]["t"])}</strong>'
                             f'{e(g["intro"]["b"])}</div>')

            panels.write('<div class="list">')
            slim_items = []
            for ii, item in enumerate(g['items']):
                if item.get('sec'):
                    panels.write(f'<div class="seclabel">{e(item["sec"])}</div>')
                    slim_items.append({"sec": 1})
                    continue
                key = f'{tab["id"]}/{g["id"]}:{ii}'
                panels.write(card_html(item, key))
                si = {"n": item["n"], "o": item["o"]}
                if item.get('ctx'):
                    si["ctx"] = item["ctx"]
                slim_items.append(si)
            panels.write('</div></div>')
            slim_groups.append({"id": g["id"], "items": slim_items})

        panels.write('</section>')
        slim.append({"id": tab["id"], "groups": slim_groups})

    src = open('esper-menu-src.html', encoding='utf-8').read()
    out = (src
           .replace('__TABS__', tabs.getvalue())
           .replace('__PANELS__', panels.getvalue())
           .replace('__DATA__', json.dumps(slim, ensure_ascii=False, separators=(',', ':')))
           .replace('__LOGO__', LOGO))
    for ph in ('__TABS__', '__PANELS__', '__DATA__', '__LOGO__'):
        assert ph not in out, f'placeholder {ph} not filled'
    open('esper-menu.html', 'w', encoding='utf-8').write(out)

    n = sum(1 for t in MENU for g in t['groups'] for i in g['items'] if not i.get('sec'))
    print(f'built esper-menu.html  {len(out):,} bytes  {n} services in static HTML')


if __name__ == '__main__':
    build()
