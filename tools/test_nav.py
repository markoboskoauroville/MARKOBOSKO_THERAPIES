#!/usr/bin/env python3
"""Proof for the way back: python3 tools/test_nav.py <base url> <screenshot dir>. Static asserts on both pages and a browser run
(desktop 1280x900 and phone 390x844): maker link opens a new tab and the therapies tab stays; in-page jump returns with the
button and with the browser's Back to the same position; midicontrol panel opens, Esc closes."""
import re, sys, os, urllib.request
from playwright.sync_api import sync_playwright
base, out = sys.argv[1].rstrip('/'), sys.argv[2]; os.makedirs(out, exist_ok=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
bad = 0
def check(c, m):
    global bad
    print(('ok   ' if c else 'FAIL ') + m); bad += (not c)
for lang, path in (('hr', '/'), ('en', '/en/')):
    s = urllib.request.urlopen(urllib.request.Request(base + path, headers={'User-Agent': 'Mozilla/5.0'})).read().decode()
    tags = re.findall(r'(<a\b[^>]*href="https?://(?!therapies\.markobosko\.org)[^"]*"[^>]*>)(.*?)</a>', s, flags=re.S)
    ok = [t for t, i in tags if 'target="_blank"' in t and 'rel="noopener"' in t and 'class="ext"' in i and 'class="sr"' in i]
    check(len(tags) == len(ok) and len(tags) > 100, f'{lang}: {len(ok)} of {len(tags)} outside links have target=_blank, noopener, the sign and the label')
    check('class="note newtab"' in s, f'{lang}: the one-line note is there')
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--mute-audio'])
    for name, vp, mob in (('desktop', {'width': 1280, 'height': 900}, False), ('phone', {'width': 390, 'height': 844}, True)):
        for lang, path in (('hr', '/'), ('en', '/en/')):
            ctx = b.new_context(viewport=vp, is_mobile=mob, has_touch=mob); pg = ctx.new_page(); pg.goto(base + path); pg.wait_for_timeout(800)
            # a catalogue link that jumps inside the page
            pg.evaluate("document.querySelector('details.catalogue').open=true")
            link = pg.locator('details.catalogue a[href^="#"]').first
            link.scroll_into_view_if_needed(); pg.wait_for_timeout(900)
            y0 = pg.evaluate('scrollY'); link.click(); pg.wait_for_timeout(1500)
            y1 = pg.evaluate('scrollY'); check(abs(y1 - y0) > 200, f'{name}/{lang}: in-page jump moved ({y0:.0f} -> {y1:.0f})')
            btn = pg.locator('#tp-back'); check(btn.is_visible(), f'{name}/{lang}: back button visible')
            pg.screenshot(path=f'{out}/{name}-{lang}-after-jump.png')
            btn.click(); pg.wait_for_timeout(1500); y2 = pg.evaluate('scrollY')
            check(abs(y2 - y0) <= 5 and not btn.is_visible(), f'{name}/{lang}: button returns to {y0:.0f} (got {y2:.0f}), then hides')
            link.click(); pg.wait_for_timeout(1500); pg.go_back(); pg.wait_for_timeout(1500); y3 = pg.evaluate('scrollY')
            check(abs(y3 - y0) <= 5, f'{name}/{lang}: browser Back returns to {y0:.0f} (got {y3:.0f})')
            # outside link opens a new tab, this tab stays
            ext = pg.locator('a[href^="https://remo.com"]').first; ext.scroll_into_view_if_needed()
            with ctx.expect_page() as np_:
                ext.click()
            n = np_.value; check(len(ctx.pages) == 2 and pg.url.startswith(base), f'{name}/{lang}: maker link opened a second tab, therapies tab still at {pg.url}')
            n.close()
            # panel
            mc = pg.locator('a[href^="https://midicontrol.markobosko.org"]').first; mc.scroll_into_view_if_needed(); ys = pg.evaluate('scrollY'); mc.click(); pg.wait_for_timeout(5000)
            check(pg.locator('#tp-panel').is_visible() and len(ctx.pages) == 1, f'{name}/{lang}: midicontrol panel open, no new tab')
            pg.screenshot(path=f'{out}/{name}-{lang}-panel.png')
            fr = [f for f in pg.frames if 'midicontrol' in f.url]; check(bool(fr), f'{name}/{lang}: the page loaded inside the panel: ' + (fr[0].title() if fr else 'no frame'))
            if fr:   # real input on a slider inside the framed page (method of MIDI_CONTROL_PROPOSAL/tests/sliders_real_input.py)
                f = fr[0]; val = lambda: f.evaluate("+document.querySelectorAll('#sliders input')[3].value")
                sl = f.locator('#sliders input').nth(3); sl.scroll_into_view_if_needed(); bx = sl.bounding_box(); v0 = val(); cx = bx['x'] + bx['width'] / 2; ty = bx['y'] + bx['height'] * (1 - v0 / 1000)
                pg.mouse.move(cx, ty); pg.mouse.down()
                for k in range(1, 9): pg.mouse.move(cx, ty - k * 8)
                pg.mouse.up(); v1 = val(); check(v1 != v0, f'{name}/{lang}: slider 4 in the panel, mouse drag {v0} -> {v1}')
                sl.focus(); pg.keyboard.press('ArrowUp'); v2 = val(); check(v2 != v1, f'{name}/{lang}: slider 4 in the panel, ArrowUp {v1} -> {v2}')
                pg.locator('#tp-panel .x').focus()
            pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
            check(not pg.locator('#tp-panel').is_visible() and abs(pg.evaluate('scrollY') - ys) <= 5, f'{name}/{lang}: Esc closes the panel, position kept (open at {ys:.0f}, after {pg.evaluate("scrollY"):.0f}, panel visible {pg.locator("#tp-panel").is_visible()})')
            ctx.close()
    b.close()
print('FAILED' if bad else 'ALL PASSED'); sys.exit(1 if bad else 0)
