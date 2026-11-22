#!/usr/bin/env python3
"""Idempotent: every link that leaves the page (http/https, other host than therapies.markobosko.org) gets target=_blank,
rel="noopener", the sign ↗ and an accessible label, on both pages; the one-line note is added after the .ded paragraph.
Run by hand after editing (the page is hand-edited; this only normalises links)."""
import re, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = {'site/index.html': ('otvara se u novoj kartici', 'Poveznice se otvaraju u novoj kartici; ova stranica ostaje otvorena.'),
     'site/en/index.html': ('opens in a new tab', 'Links open in a new tab; this page stays open.')}
for p, (label, note) in L.items():
    s = open(os.path.join(R, p), encoding='utf-8').read()
    def fix(m):
        tag, inner = m.group(1), m.group(2)
        h = re.search(r'href="([^"]*)"', tag).group(1)
        if not re.match(r'https?://', h) or re.match(r'https?://therapies\.markobosko\.org', h): return m.group(0)
        tag = re.sub(r'\s(target|rel)="[^"]*"', '', tag)
        tag = tag[:-1] + ' target="_blank" rel="noopener">'
        if 'class="ext"' not in inner:
            inner += '<span class="ext" aria-hidden="true"> ↗</span><span class="sr"> (%s)</span>' % label
        return tag + inner + '</a>'
    s = re.sub(r'(<a\b[^>]*>)(.*?)</a>', fix, s, flags=re.S)
    if 'class="note newtab"' not in s:
        i = s.find('class="ded"'); j = s.find('</p>', i) + 4
        s = s[:j] + '\n<p class="note newtab">%s</p>' % note + s[j:]
    if 'nav.js' not in s:
        src = '/nav.js' if p.endswith('en/index.html') else 'nav.js'
        s = s.replace('<script src="%s" defer></script>' % ('/playlist.js' if '/en/' in p else 'playlist.js'),
                      '<script src="%s" defer></script>\n<script src="%s" defer></script>' % (('/playlist.js' if '/en/' in p else 'playlist.js'), src), 1)
    open(os.path.join(R, p), 'w', encoding='utf-8').write(s)
    print(p, s.count('class="ext"'), 'marked')
