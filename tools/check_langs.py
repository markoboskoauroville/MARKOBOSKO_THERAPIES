#!/usr/bin/env python3
"""Fails (exit 1) when the Croatian page (site/index.html) and the English page (site/en/index.html) differ in
structure: section ids, image files, external links, in-page anchors, language switch, lang/hreflang.
Texts are not compared (they are translated by hand): the TAKEOVER checklist says to edit both pages in one commit."""
import re, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p): return open(os.path.join(R, p), encoding='utf-8').read()
def norm(u): return u.lstrip('/') if not u.startswith('http') else u
def facts(s):
    return {
        'sections': re.findall(r'<section id="([^"]+)"', s),
        'images': sorted(norm(u) for u in re.findall(r'<img[^>]*\ssrc="([^"]+)"', s) if 'ytimg' not in u),
        'ext links': sorted(set(u for u in re.findall(r'href="(https?://[^"]+)"', s) if 'therapies.markobosko.org' not in u)),
        'anchors': sorted(set(re.findall(r'href="(#[^"]+)"', s))),
        'iframes': sorted(re.findall(r'<iframe[^>]*src="([^"]+)"', s)),
        'data-v': sorted(re.findall(r'data-v="([^"]+)"', s)),
        'scripts': sorted(norm(u) for u in re.findall(r'<script[^>]*src="([^"]+)"', s)),
    }
hr, en = load('site/index.html'), load('site/en/index.html')
bad = []
fh, fe = facts(hr), facts(en)
for k in fh:
    if fh[k] != fe[k]:
        a, b = set(map(str, fh[k])), set(map(str, fe[k]))
        bad.append(f'{k}: only in hr {sorted(a-b)[:5]}, only in en {sorted(b-a)[:5]}' if a != b else f'{k}: same items, different count/order')
for name, s, lang in (('hr', hr, 'hr'), ('en', en, 'en')):
    if f'<html lang="{lang}" data-lang="{lang}">' not in s: bad.append(f'{name}: html lang/data-lang wrong')
    if 'class="langsw"' not in s or 'data-l="hr"' not in s or 'data-l="en"' not in s: bad.append(f'{name}: language switch missing')
    if s.count('class="langsw"')!=1: bad.append(f'{name}: exactly one language switch needed, found {s.count(chr(34).join(["class=","langsw"])+chr(34))}')
    for h in ('hreflang="hr"', 'hreflang="en"', 'hreflang="x-default"'):
        if h not in s: bad.append(f'{name}: {h} missing')
if bad:
    print('LANGUAGE PARITY FAILED:'); [print(' -', b) for b in bad]; sys.exit(1)
print('language parity ok:', len(fh['sections']), 'sections,', len(fh['images']), 'images')
