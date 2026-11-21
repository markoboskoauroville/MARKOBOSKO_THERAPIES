"""hsdrv: drive Hemi-Sync Flow on the Pixel_7_API_35 emulator (emulator-5556) through adb.

Navigation, album pages, per-track downloads, playback state. Later the taps can go through
Screen Copy (Mantra) /tap; for now adb input is used. Never touches emulator-5554.
"""
import html, os, re, subprocess, time

ADB = os.path.expanduser('~/Library/Android/sdk/platform-tools/adb')
SER = os.environ.get('HS_SERIAL', 'emulator-5556')
PKG = 'com.hemisync.hemisyncflow'
assert SER != 'emulator-5554'


def adb(*a, timeout=40, out=True):
    try:
        r = subprocess.run([ADB, '-s', SER] + list(a), capture_output=True, timeout=timeout)
        return r.stdout if out else r
    except subprocess.TimeoutExpired:
        return b''


def sh(c, timeout=40):
    return adb('shell', c, timeout=timeout).decode('utf8', 'ignore')


def tap(x, y):
    sh(f'input tap {int(x)} {int(y)}')


def key(k):
    sh(f'input keyevent {k}')


def swipe(x1, y1, x2, y2, ms=300):
    sh(f'input swipe {x1} {y1} {x2} {y2} {ms}')


def shot(path):
    open(path, 'wb').write(adb('exec-out', 'screencap', '-p'))


def nodes(tries=4):
    """List of dicts: text, id, desc, bounds, click."""
    for _ in range(tries):
        o = sh('uiautomator dump /sdcard/ui.xml 2>&1')
        if 'dumped to' in o:
            x = adb('exec-out', 'cat', '/sdcard/ui.xml').decode('utf8', 'ignore')
            res = []
            for m in re.finditer(r'<node[^>]*>', x):
                n = m.group(0)
                g = lambda k: (re.search(r' ' + k + r'="([^"]*)"', n) or [None, ''])[1]
                b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', n)
                res.append({'text': html.unescape(g('text')), 'id': g('resource-id').split('/')[-1],
                            'desc': html.unescape(g('content-desc')),
                            'b': tuple(map(int, b.groups())) if b else (0, 0, 0, 0),
                            'click': 'clickable="true"' in n})
            return res
        time.sleep(1.5)
    return []


def find(ns, text=None, id=None, start=False):
    for n in ns:
        if id and n['id'] != id:
            continue
        if text is not None:
            if start and not n['text'].startswith(text):
                continue
            if not start and n['text'] != text:
                continue
        return n
    return None


def center(b):
    return ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)


def dismiss_dialogs(ns=None):
    ns = ns if ns is not None else nodes()
    if find(ns, id='alertTitle') or find(ns, id='button2'):
        for label in ('CANCEL', 'Cancel', 'NOT NOW', 'Not now', 'LATER', 'Later', 'NO', 'No'):
            n = find(ns, label)
            if n:
                tap(*center(n['b'])); time.sleep(1.5); return True
    return False


def volume_max():
    for _ in range(16):
        key('KEYCODE_VOLUME_UP')
    sh('svc power stayon true')


def fresh():
    sh(f'am force-stop {PKG}'); time.sleep(1)
    sh(f'monkey -p {PKG} -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1'); time.sleep(7)


def front():
    sh(f'monkey -p {PKG} -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1'); time.sleep(2.5)


def to_album_list(cat='Relaxation'):
    """Fresh start -> Explore -> Applications See all -> <cat> -> Albums (A-Z list)."""
    fresh()
    for _ in range(8):
        ns = nodes(); dismiss_dialogs(ns)
        if find(ns, 'Recently Played') or find(ns, id='nav_explore'):
            break
        time.sleep(2)
    for _ in range(5):
        tap(540, 2200); time.sleep(3)
        ns = nodes(); dismiss_dialogs(ns)
        if find(ns, 'Applications'):
            break
    tap(998, 575); time.sleep(3)
    b = None
    for _ in range(30):
        ns = nodes(); n = find(ns, cat); b = n['b'] if n else None
        if b and 700 < b[1] < 1700:
            break
        if b and b[1] <= 700:
            swipe(540, 1000, 540, 1400)
        else:
            swipe(540, 1700, 540, 1100)
        time.sleep(0.8)
    if not b:
        return False
    tap(center(b)[0], b[1] - 110); time.sleep(4)
    for _ in range(4):
        ns = nodes()
        al = [n for n in ns if n['text'] == 'Albums' and n['b'][1] > 1000]
        if al:
            tap(*center(al[0]['b'])); time.sleep(5); return True
        time.sleep(2)
    return False


def open_in_list(name):
    ns = nodes(); idx = None
    for n in ns:
        if '\n' in n['text'] and n['text'].startswith('A\n'):
            idx = (n['text'].split('\n'), n['b'])
    if idx:
        L, b = idx; ch = name[0].upper()
        if ch in L:
            i = L.index(ch); tap(1042, b[1] + int((b[3] - b[1]) * (i + 0.5) / len(L))); time.sleep(1.5)
    for _ in range(10):
        ns = nodes()
        hit = next((n for n in ns if n['text'] == name), None) or next((n for n in ns if n['text'].startswith(name)), None)
        if hit and 300 < hit['b'][1] < 2000:
            tap(center(hit['b'])[0], hit['b'][1] - 100); time.sleep(4)
            ns = nodes()
            t = find(ns, id='tv_title_album_name')
            return bool(t and t['text'].startswith(name.split(' (')[0][:10]))
        swipe(540, 1700, 540, 1000); time.sleep(0.8)
    return False


def open_album(name, cat='Relaxation'):
    for attempt in range(3):
        if to_album_list(cat) and open_in_list(name):
            return True
    return False


def album_page():
    """Read the open album page fully (scrolls). Returns dict with tracks [(num, title)]."""
    for _ in range(5):
        ns = nodes()
        if (find(ns, id='tv_album_description') or {'text': ''})['text']:
            break
        time.sleep(2)
    g = lambda i: (find(ns, id=i) or {'text': ''})['text']
    info = {'album': g('tv_title_album_name'), 'category': g('tv_title_album_category'),
            'description': g('tv_album_description'), 'tracks': []}
    seen = {}
    for _ in range(12):
        ns = nodes()
        nums = [n for n in ns if n['id'] == 'tv_number_of_track']
        names = [n for n in ns if n['id'] == 'tv_name_of_track']
        new = 0
        for a, t in zip(nums, names):
            k = int(a['text'].strip('.') or 0)
            if k not in seen:
                seen[k] = t['text']; new += 1
        if not new and seen:
            break
        swipe(540, 1900, 540, 900, 500); time.sleep(1)
    info['tracks'] = sorted(seen.items())
    # back to top
    for _ in range(4):
        swipe(540, 700, 540, 2000, 200)
    time.sleep(1)
    return info


def track_row(num):
    """Scroll the album page until track <num> row is on screen; returns its bounds or None."""
    for direction in (None, 'down', 'down', 'down', 'down', 'down', 'down', 'up', 'up', 'up', 'up', 'up', 'up', 'up'):
        ns = nodes()
        for a in ns:
            if a['id'] == 'tv_number_of_track' and a['text'].strip('.') == str(num):
                b = a['b']
                if 300 < b[1] < 1950:
                    return (0, b[1] - 27, 1080, b[3] + 27)
        if direction == 'down':
            swipe(540, 1700, 540, 1100, 400)
        elif direction == 'up':
            swipe(540, 1000, 540, 1600, 400)
        time.sleep(0.8)
    return None


def icon_state(row, png='/tmp/hs2/_icon.png'):
    """Look at the per-track download icon (x 958-1037): 'arrow', 'stop' (downloading) or 'done'."""
    from PIL import Image
    shot(png)
    im = Image.open(png).convert('RGB')
    y0, y1 = row[1] + 16, row[3] - 16
    box = im.crop((958, y0, 1037, y1))
    px = list(box.getdata()); w, h = box.size
    purple = [(i % w, i // w) for i, (r, g, b) in enumerate(px) if b > 150 and r > 100 and g < 140]
    if not purple:
        return 'none'
    xs = [p[0] for p in purple]; ys = [p[1] for p in purple]
    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    fill = len(purple) / float((bw + 1) * (bh + 1))
    if fill > 0.75 and bw < 30:
        return 'stop'
    if bw < 30 and bh > 25:
        return 'arrow'
    return 'done'


def session():
    """(state, title, album) of the Hemi-Sync media session."""
    o = sh('dumpsys media_session')
    i = o.find('package=' + PKG)
    if i < 0:
        return ('', '', '')
    seg = o[i:i + 1500]
    j = seg.find('\n    ', 20)
    while j >= 0 and seg[j + 5:j + 6] == ' ':
        j = seg.find('\n    ', j + 1)
    seg = seg[:j] if j > 0 else seg
    st = re.search(r'state=PlaybackState \{state=(\w+)', seg)
    md = re.search(r'description=(.*?), (.*?), null', seg)
    return (st.group(1) if st else '', md.group(1) if md else '', md.group(2) if md else '')


def pause():
    key('KEYCODE_MEDIA_PAUSE')
