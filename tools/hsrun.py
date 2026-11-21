"""hsrun: unattended, resumable Hemi-Sync Flow recorder (emulator-5556 -> Screen Copy (Mantra) v31).

  python3 hsrun.py clips      the 12 clip-only albums (one 60 s sample each) -> site/audio
  python3 hsrun.py albums     the 10 full albums -> ~/Music/HemiSync/<Album>/ (+ their site clip)
  python3 hsrun.py all        clips, then albums
  python3 hsrun.py site       rewrite samples.json / albums.json from what exists

Every finished file is checked (sound + length); a rerun skips what already passed.
Recording: `screencopy record start/next/stop --serial emulator-5556` (device playback capture to WAV).
No internet needed once the albums are downloaded except the app's own start; no AI, no credits.
"""
import json, os, re, shutil, subprocess, sys, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hsdrv as h
import hsaudio as au
from hsprogress import Progress
from ocr import ocr

REPO = os.path.expanduser('~/Developer/MARKOBOSKO_THERAPIES')
SITE = REPO + '/site/audio'
MUSIC = os.path.expanduser('~/Music/HemiSync')
WORK = MUSIC + '/.work'
SCREC = os.path.expanduser('~/Music/Screen Copy Recordings/Pixel 7 emulator')
LOG = MUSIC + '/record.log'
SERIAL = h.SER
RMS_FLOOR = 0.002

# The 10 full albums, in order. Swaps (voice or sudden loud passages) go to SWAPS in order.
ALBUMS = ['Guitar Lullaby with Hemi-Sync', 'Lullaby with Hemi-Sync', 'Cloudscapes', 'Meeresbrandung (Surf)', 'Enchanted Forest',
          'Pearl Moon', 'Path to Peace', 'Open Window', 'Cascade', 'Celestial Space']
ALBUM_NOTES = {}
SWAPS = ['Dreamland', 'Midsummer Night', 'Music for Unwinding']
# Clip-only candidates (12 needed), best first; voice-suspect ones are skipped automatically.
CLIP_CANDIDATES = ['Desert Moon Song with Hemi-Sync', 'Himalayan Soul', 'Eternity Within', 'Galilean Moons', 'Oasis',
                   'Orbits of Hope', 'Reflections', 'Pachelbel Canon', 'Prisms', 'Portraits', 'Music for Rejuvenation',
                   'Komuso', 'Romantic Wonder', 'Masterworks', 'Midsummer Night', 'Music for Unwinding']
VOICE = re.compile(r'\bguid(e|ed|ance)\b|\bvoices?\b|\bvocals?\b|narrat|\bspoken\b|\bspeaks? (to you|softly|gently)\b(?! to your soul)|\bsing(s|ing|er|ers)?\b|\bsung\b|'
                   r'\bchant|\blyric|\bverbal|affirmation|instruction|\bexercises?\b|focus \d|countdown|\btalk|Stimme|gesprochen', re.I)
CALM = re.compile(r'lullaby|cradle|berceuse|dream|calm|peace|moon|rain|cloud|water|sleep|serene|quiet|gentle|night|'
                  r'stillness|rest|float|soft', re.I)

os.makedirs(WORK, exist_ok=True); os.makedirs(SITE + '/albums', exist_ok=True)
P = None


def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, 'a') as f:
        f.write(s + '\n')


def slug(s):
    s = re.sub(r'with Hemi-Sync®?|®', '', s)
    s = s.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def clean_album_name(s):
    return re.sub(r'\s*®', '', s).replace(' with Hemi-Sync', '').strip()


def safe(s):
    return re.sub(r'[/:\\]', '-', s).strip()


def sc(*args):
    r = subprocess.run(['screencopy'] + list(args) + ['--serial', SERIAL], capture_output=True, text=True)
    if r.returncode == 2:
        raise RuntimeError('Screen Copy (Mantra) is not running')
    try:
        return json.loads(r.stdout)
    except Exception:
        return {'raw': r.stdout + r.stderr}


def capture_level():
    """Screen Copy's live level for the emulator tab (0 = silent)."""
    try:
        st = json.loads(subprocess.run(['screencopy', 'status'], capture_output=True, text=True).stdout)
        for d in st if isinstance(st, list) else st.get('status', []):
            if 'emulator' in d.get('phone', ''):
                return float(d.get('level_rms') or 0)
    except Exception:
        pass
    return 0.0


HEALS = [0]


def tab_live():
    try:
        st = json.loads(subprocess.run(['screencopy', 'tabs'], capture_output=True, text=True).stdout or '[]')
        for d in (st if isinstance(st, list) else st.get('tabs', [])):
            if d.get('serial') == SERIAL:
                return bool(d.get('connected'))
    except Exception:
        pass
    return False


STATUS_FILE = os.path.expanduser('~/Library/Application Support/ScreenCopyMantra/record_status.json')


def capture_healthy():
    """While recording: live level above floor and the status file fresh (written within 30 s)."""
    try:
        fresh = time.time() - os.path.getmtime(STATUS_FILE) < 30
    except OSError:
        fresh = False
    lv = 0.0
    for _ in range(4):
        lv = capture_level()
        if lv > 0.0005:
            break
        time.sleep(1.5)
    return lv > 0.0005 and fresh, lv, fresh


def heal(why):
    """Coordinator's recipe (21.11.2026): kill Screen Copy's scrcpy-server on the emulator, wait 15 s; still not
    reachable -> quit and reopen Screen Copy (Mantra). The caller redoes the track."""
    HEALS[0] += 1
    log('HEAL', HEALS[0], why)
    notify(f'HEAL {HEALS[0]}: {why}')
    if HEALS[0] > 8:
        raise RuntimeError('Screen Copy keeps failing (more than 8 heals): stopping')
    h.pause()
    try:
        sc('record', 'stop')
    except Exception:
        pass
    # Screen Copy's server is the app_process with audio=true (Marko's viewer runs audio=false); never the sh wrapper
    for line in h.sh('ps -A -o PID,ARGS').splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[1].startswith('app_process / com.genymobile.scrcpy.Server') and 'audio=true' in parts[1]:
            h.sh(f'kill {parts[0]}'); log('HEAL: killed scrcpy-server', parts[0])
    time.sleep(15)
    ok = False
    for _ in range(6):
        if tab_live():
            ok = True; break
        time.sleep(3)
    if not ok:
        log('HEAL: tab not reachable, restarting Screen Copy (Mantra)')
        subprocess.run(['osascript', '-e', 'tell application "Screen Copy (Mantra)" to quit'], capture_output=True)
        time.sleep(6)
        subprocess.run(['open', '-a', 'Screen Copy (Mantra)'], capture_output=True)
        for _ in range(30):
            time.sleep(3)
            if tab_live():
                ok = True; break
    log('HEAL done' if ok else 'HEAL failed: emulator tab still not reachable')
    if not ok:
        raise RuntimeError('Screen Copy could not be healed')
    time.sleep(5)


def check_capture():
    """Called while the track plays: a silent capture heals Screen Copy and asks for a redo."""
    for _ in range(6):
        if capture_level() > 0.0005:
            return True
        time.sleep(1.5)
    heal('capture silent while the track plays')
    raise RedoTrack('capture was silent: healed, redo')


class RedoTrack(Exception):
    pass


def free_kb():
    try:
        return int(h.sh('df -k /data | tail -1').split()[3])
    except Exception:
        return 0


def meta_path(name):
    return f'{WORK}/{slug(name)}.json'


def read_album(name):
    """Open the album page, save JSON + 400 px cover. Returns info dict."""
    if not h.open_album(name):
        raise RuntimeError('album not found: ' + name)
    info = h.album_page()
    info['query'] = name
    m = re.search(r'(?:Composed|composed|performed|Performed|by)\s+(?:and performed\s+)?by\s+([A-Z][\w.\-]+(?:\s[A-Z][\w.\-]+){0,3})',
                  info['description'])
    info['artist'] = m.group(1) if m else ''
    shot = f'{WORK}/{slug(name)}.png'
    h.shot(shot)
    from PIL import Image
    Image.open(shot).convert('RGB').crop((42, 325, 462, 745)).resize((400, 400), Image.LANCZOS).save(
        f'{WORK}/{slug(name)}.jpg', quality=92)
    info['voice_suspect'] = bool(VOICE.search(info['description'] + ' ' + ' '.join(t for _, t in info['tracks'])))
    try:
        old = json.load(open(meta_path(name)))
        for key in ('lengths', 'clip_file', 'clip_track', 'clip_track_length', 'reason'):
            if old.get(key) and not info.get(key):
                info[key] = old[key]
        if old.get('artist') and (not info.get('artist') or old['artist'] != info['artist']):
            info['artist'] = old['artist']     # the Downloads list's artist beats the regex
        if not info['description'] and old.get('description'):
            info['description'] = old['description']
    except Exception:
        pass
    json.dump(info, open(meta_path(name), 'w'), ensure_ascii=False, indent=1)
    return info


def artist_from_downloads(album_title):
    """Library > Downloads shows the artist under each album: used when the description does not name one."""
    return ''


def ensure_track_downloaded(num, timeout=600):
    row = h.track_row(num)
    if not row:
        return False
    st = h.icon_state(row)
    if st == 'done':
        return wait_disk_settled()
    if st == 'arrow':
        h.tap(997, (row[1] + row[3]) // 2)
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(5)
        row = h.track_row(num) or row
        st = h.icon_state(row)
        if st == 'done':
            return wait_disk_settled()
        if st == 'arrow' and time.time() - t0 > 60:
            h.tap(997, (row[1] + row[3]) // 2)
    return False


def wait_disk_settled(timeout=900):
    """The check mark appears before the file is complete: wait until /data stops shrinking (3 equal readings)."""
    t0 = time.time(); last = free_kb(); same = 0
    while time.time() - t0 < timeout:
        time.sleep(5)
        f = free_kb()
        same = same + 1 if abs(f - last) < 64 else 0
        last = f
        if same >= 3:
            return True
    return False


def start_playback(row):
    """Tap the track row; make sure the session is PLAYING (retry once)."""
    for attempt in range(2):
        h.tap(400, (row[1] + row[3]) // 2)
        for _ in range(12):
            time.sleep(1)
            if h.session()[0] == 'PLAYING':
                time.sleep(2)
                return True
    return False


def album_downloaded():
    from PIL import Image
    h.shot('/tmp/hs2/_alb.png')
    im = Image.open('/tmp/hs2/_alb.png').convert('RGB').crop((791, 666, 870, 745))
    px = list(im.getdata()); w = im.size[0]
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


def ensure_album_downloaded(name, timeout=1800):
    st = album_downloaded()
    if st == 'done':
        return True
    if st == 'arrow':
        h.tap(830, 705)
    t0 = time.time(); last = free_kb()
    while time.time() - t0 < timeout:
        time.sleep(8)
        st = album_downloaded()
        f = free_kb()
        P.set(state='downloading', message=f'downloading {name}: {round((last - f) / 1024)} MB so far, {round(f / 1024)} MB free on the emulator')
        if st == 'done':
            return wait_disk_settled()
        if f < 15000:
            log('emulator storage nearly full while downloading', name)
            return False
        if st == 'arrow' and time.time() - t0 > 90:
            h.tap(830, 705)
    return False


def save_artist(album_title, artist):
    import html as _h
    artist = _h.unescape(artist)
    for f in os.listdir(WORK):
        if f.endswith('.json'):
            try:
                m = json.load(open(f'{WORK}/{f}'))
            except Exception:
                continue
            if m.get('album') == album_title and m.get('artist') != artist:
                m['artist'] = artist
                json.dump(m, open(f'{WORK}/{f}', 'w'), ensure_ascii=False, indent=1)
                log('artist', album_title, '=', artist)


def delete_download(album_title):
    """Library > Downloads > X on the album's row > YES."""
    h.front(); h.key('KEYCODE_BACK'); time.sleep(1)
    h.fresh()
    for _ in range(3):
        h.tap(310, 2200); time.sleep(3)
        ns = h.nodes(); h.dismiss_dialogs(ns)
        d = h.find(ns, 'Downloads')
        if d:
            h.tap(*h.center(d['b'])); time.sleep(3); break
    for _ in range(3):
        ns = h.nodes()
        hit = next((n for n in ns if n['text'] == album_title or n['text'].startswith(album_title[:14])), None)
        if not hit:
            log('download deleted:', album_title, 'free', free_kb() // 1024, 'MB')
            return True
        y = (hit['b'][1] + hit['b'][3]) // 2 + 28   # the X sits level with the title/artist pair
        below = [n for n in ns if n['text'] and 0 < n['b'][1] - hit['b'][3] < 40 and n['b'][0] == hit['b'][0]]
        if below:
            save_artist(album_title, below[0]['text'])
        h.tap(1019, y); time.sleep(2)
        ns = h.nodes(); yes = h.find(ns, 'YES')
        if yes:
            h.tap(*h.center(yes['b'])); time.sleep(3)
    return False


def read_length():
    """OCR the full player: elapsed + remaining = track length (s)."""
    h.shot('/tmp/hs2/_pl.png')
    els = rem = None
    for t, (x, y) in ocr('/tmp/hs2/_pl.png', (0, 1300, 1080, 1560)):
        m = re.fullmatch(r'(-?)(\d{1,2}):(\d\d)(?::(\d\d))?', t.strip().replace(' ', ''))
        if not m:
            continue
        v = int(m.group(2)) * 60 + int(m.group(3)) if not m.group(4) else int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
        if m.group(1) == '-':
            rem = v
        else:
            els = v
    if els is not None and rem is not None:
        return els + rem
    return None


def open_full_player():
    h.tap(500, 2035); time.sleep(2.5)


def wav_for(name):
    return f'{SCREC}/{name}.wav'


# ------------------------------------------------------------------ clips

def clip_path(n, name):
    return f'{SITE}/{n:02d}-{slug(name)}.mp3'


def existing_clip(name):
    for f in os.listdir(SITE):
        if f.endswith('.mp3') and f[3:-4] == slug(name):
            return f'{SITE}/{f}'
    return None


def clip_ok(path):
    return path and os.path.exists(path) and abs(au.probe_len(path) - 60) < 1.5


def pick_track(tracks):
    for k, t in tracks:
        if CALM.search(t) and not re.search(r'intro|guid|welcome|talk', t, re.I):
            return k, t
    for k, t in tracks:
        if not re.search(r'intro|guid|welcome|talk', t, re.I):
            return k, t
    return tracks[0]


def do_clip(name, num):
    out = clip_path(num, name)
    info = read_album(name)
    if info['voice_suspect']:
        log('VOICE-SUSPECT, skipped:', info['album'])
        return 'voice'
    if not info['tracks']:
        return 'notracks'
    k, title = pick_track(info['tracks'])
    P.set(state='downloading', clips={'current': clean_album_name(info['album'])}, message=f'clip {num}: downloading {title}')
    if not ensure_track_downloaded(k):
        log('download failed', name, title)
        return 'download'
    row = h.track_row(k)
    rec = f'clip {slug(name)}'
    if os.path.exists(wav_for(rec)):
        os.remove(wav_for(rec))
    h.volume_max()
    sc('record', 'start', '--name', rec)
    P.set(state='recording', message=f'clip {num} of 22: {clean_album_name(info["album"])}, {title}')
    if not start_playback(row):
        sc('record', 'stop'); log('playback did not start', name, title); return 'noplay'
    open_full_player(); length = read_length(); h.key('KEYCODE_HOME')
    check_capture()
    t0 = time.time()
    while time.time() - t0 < 112:
        time.sleep(2)
        st = h.session()
        if st[0] not in ('PLAYING', 'BUFFERING', 'CONNECTING') and time.time() - t0 > 15:
            break
    sc('record', 'stop'); h.pause()
    P.set(state='encoding')
    a, rep = au.clean(au.load(wav_for(rec)))
    s = au.stats(a)
    log('CLIP raw', name, title, s, rep, 'track length', length)
    if s['rms'] < RMS_FLOOR or s['len_s'] < 50:
        return 'silent'
    ok = au.encode_clip(a, out, f'{WORK}/{slug(name)}.jpg', title, info.get('artist') or 'Hemi-Sync', clean_album_name(info['album']))
    if not ok or not clip_ok(out):
        return 'encode'
    shutil.copy(f'{WORK}/{slug(name)}.jpg', f'{SITE}/albums/{slug(name)}.jpg')
    info.update(clip_file=os.path.basename(out), clip_track=title, clip_track_length=length)
    json.dump(info, open(meta_path(name), 'w'), ensure_ascii=False, indent=1)
    os.remove(wav_for(rec))
    return 'ok'


def run_clips(target=12, first_number=11):
    """Clip-only albums get numbers 11..22 (1..10 are the full albums' clips)."""
    done = 0; n = first_number
    for name in CLIP_CANDIDATES:
        if done >= target:
            break
        if name in ALBUMS:
            continue
        ex = existing_clip(name)
        if clip_ok(ex):
            done += 1; n += 1; P.item('clip', name, status='done'); continue
        P.item('clip', name, status='active')
        for attempt in range(3):
            try:
                r = do_clip(name, n)
            except RedoTrack as e:
                log('redo clip after heal', name); r = 'healed'; continue
            except RuntimeError as e:
                if 'Screen Copy' in str(e):
                    raise
                log('ERR clip', name, repr(e), traceback.format_exc()[-400:]); r = 'error'
            except Exception as e:
                log('ERR clip', name, repr(e), traceback.format_exc()[-400:]); r = 'error'
            if r in ('ok', 'voice', 'notracks'):
                break
            log('clip retry', name, r)
        if r == 'ok':
            done += 1; n += 1
            P.item('clip', name, status='done', duration_s=60)
            try:
                info = json.load(open(meta_path(name)))
                delete_download(info['album'])
            except Exception as e:
                log('delete failed', name, repr(e))
        else:
            P.item('clip', name, status='failed' if r != 'voice' else 'swapped', note=r)
        P.set(clips={'done': count_clips()})
        publish()
    publish(force=True)
    return done


def count_clips():
    return len([f for f in os.listdir(SITE) if f.endswith('.mp3')])


# ------------------------------------------------------------------ albums

def album_dir(info):
    return f'{MUSIC}/{safe(clean_album_name(info["album"]))}'


def track_file(info, k, title):
    return f'{album_dir(info)}/{k:02d} {safe(title)}.m4a'


def track_ok(path, length):
    if not os.path.exists(path):
        return False
    L = au.probe_len(path)
    return L > 5 and (not length or abs(L - length) <= 2)


def split_boundaries(a, marks):
    """marks: approximate sample index of each track start (from title changes). Refine each to the
    quietest point (prefer exact-zero runs) within +-3 s."""
    W = 3 * au.SR; out = []
    for m in marks:
        lo, hi = max(0, m - W), min(len(a), m + W)
        seg = a[lo:hi]
        runs = au.zero_runs(seg, 240)
        if runs:
            s, e = max(runs, key=lambda r: r[1] - r[0])
            out.append(lo + (s + e) // 2); continue
        e = (seg.astype('float64') ** 2).sum(1)
        win = 480; n = len(e) // win
        if n == 0:
            out.append(m); continue
        en = e[:n * win].reshape(n, win).sum(1)
        out.append(lo + int(en.argmin()) * win + win // 2)
    return out


def measure_lengths(info):
    """Before recording: walk the album in the full player with its Next button and read each track's length
    (elapsed + remaining, OCR). Done before the recording so no UI runs while the music is captured."""
    tracks = info['tracks']; titles = {t: k for k, t in tracks}; out = {}
    row = h.track_row(tracks[0][0])
    if not row or not start_playback(row):
        return out
    open_full_player()
    for _ in range(len(tracks) + 2):
        st, title, alb = h.session()
        k = titles.get(title)
        L = read_length()
        if k and L:
            out[k] = L
        if len(out) >= len(tracks):
            break
        h.tap(740, 1572)          # Next
        for _ in range(16):
            time.sleep(0.5)
            if h.session()[1] != title:
                break
        time.sleep(1.5)
    h.pause()
    log('LENGTHS', info['album'], out)
    return out


def record_album(info, want):
    """Play the album from track <first> and record continuously; per-track WAVs via `record next`.
    want: list of (k, title) still needed. Returns {k: (wav, length, start_offset)}."""
    tracks = info['tracks']; titles = {t: k for k, t in tracks}
    first = want[0][0]
    row = h.track_row(first)
    h.volume_max()
    name0 = f'rec {slug(info["album"])} {first:02d}'
    for k, t in tracks:
        p = wav_for(f'rec {slug(info["album"])} {k:02d}')
        if os.path.exists(p):
            os.remove(p)
    pre = info.get('lengths') or {}
    pre = {int(k): v for k, v in pre.items()}
    sc('record', 'start', '--name', name0)
    if not start_playback(row):
        sc('record', 'stop'); raise RuntimeError('playback did not start')
    h.key('KEYCODE_HOME')
    check_capture()
    L = pre.get(first)
    cur = first; lengths = dict(pre); t_start = time.time()
    P.set(state='recording', albums={'current_track': dict(tracks)[first], 'track_index': first})
    P.track_started(L)
    log('PLAY', info['album'], first, dict(tracks)[first], 'length', L)
    last_k = max(k for k, _ in want)
    stalled = 0; last_health = time.time()
    while True:
        time.sleep(0.4)
        st, title, alb = h.session()
        if st != 'PLAYING':
            stalled += 1
            if stalled > 25:      # ~10 s not playing: finished or stuck
                log('playback stopped', st, title)
                break
            continue
        stalled = 0
        if cur >= last_k and lengths.get(cur) and time.time() - P.track_t0 > lengths[cur] + 4:
            log('last wanted track reached its length'); break
        k = titles.get(title)
        if k and k != cur:
            if cur >= last_k or k < cur:
                break
            sc('record', 'next', '--name', f'rec {slug(info["album"])} {k:02d}')
            cur = k
            L = lengths.get(k)
            P.set(albums={'current_track': title, 'track_index': k}); P.track_started(L)
            log('NEXT', k, title, 'length', L)
        if time.time() - t_start > 4 * 3600:
            break
        if time.time() - last_health > 60:
            last_health = time.time()
            ok, lv, fresh = capture_healthy()
            if not ok and h.session()[0] == 'PLAYING':
                heal(f'during {info["album"]} track {cur}: level {lv:.5f}, status file fresh {fresh}')
                raise RedoTrack('healed mid-album')
    sc('record', 'stop'); h.pause()
    return lengths


def finish_album(info, lengths, want, prev=None):
    """Concatenate the per-track WAVs, refine the boundaries, clean, encode, check."""
    import numpy as np
    parts = []; marks = []; pos = 0; ks = []
    for k, t in info['tracks']:
        p = wav_for(f'rec {slug(info["album"])} {k:02d}')
        if not os.path.exists(p):
            continue
        a = au.load(p)
        if parts:
            marks.append(pos)
        parts.append(a); ks.append((k, t)); pos += len(a)
    if not parts:
        return {}
    A = np.concatenate(parts)
    cuts = [0] + split_boundaries(A, marks) + [len(A)]
    os.makedirs(album_dir(info), exist_ok=True)
    res = {}
    artist = info.get('artist') or 'Hemi-Sync'
    wanted = {k for k, _ in want}
    for i, (k, t) in enumerate(ks):
        if k not in wanted:
            os.remove(wav_for(f'rec {slug(info["album"])} {k:02d}')); continue
        seg, rep = au.clean(A[cuts[i]:cuts[i + 1]])
        s = au.stats(seg); L = lengths.get(k)
        dead = au.silent_stretches(seg)
        out = track_file(info, k, t)
        okay = s['rms'] >= RMS_FLOOR and (not L or abs(s['len_s'] - L) <= 2)
        attempts = (prev or {}).get(str(k), {}).get('attempts', 0) + 1
        heavy = rep.get('gaps_removed', 0) > 10 or rep.get('gap_s', 0) > 0.2
        if okay and heavy and attempts < 2:
            okay = False   # re-record once (coordinator, 21.11.2026)
        if s['len_s'] > 5:
            au.encode_track(seg, out, f'{WORK}/{slug(info["query"])}.jpg', t, artist, clean_album_name(info['album']), k, len(info['tracks']))
        nw, heard = speech_words(seg) if s['len_s'] > 25 else (0, '')
        if nw > 6:
            notify(f'SPEECH? {info["album"]} track {k} {t}: {heard}')
        log('TRACK', info['album'], k, t, s, rep, 'want', L, 'dead2s', dead, 'speech words', nw, repr(heard)[:60], 'OK' if okay else 'CHECK FAILED')
        res[k] = {'title': t, 'ok': okay, 'len_s': s['len_s'], 'length': L, 'rms': s['rms'], 'gaps': rep.get('gaps_removed', 0),
                  'gap_ms': int(rep.get('gap_s', 0) * 1000), 'attempts': attempts, 'heavy': heavy, 'speech_words': nw}
        if okay:
            os.remove(wav_for(f'rec {slug(info["album"])} {k:02d}'))
    return res


def write_album_files(info, results):
    d = album_dir(info)
    shutil.copy(f'{WORK}/{slug(info["query"])}.jpg', f'{d}/cover.jpg')
    st = {}
    sp = f'{d}/.status.json'
    if os.path.exists(sp):
        st = json.load(open(sp))
    st.update({str(k): v for k, v in results.items()})
    json.dump(st, open(sp, 'w'), ensure_ascii=False, indent=1)
    lines = [clean_album_name(info['album']), info.get('artist') or '', info.get('category', ''), '', info['description'], '']
    for k, t in info['tracks']:
        r = st.get(str(k), {})
        L = r.get('len_s') or 0
        lines.append(f'{k:02d}  {t}  {int(L // 60)}:{int(L % 60):02d}  {"ok" if r.get("ok") else "not checked"}  '
                     f'rms {r.get("rms", 0)}  repaired gaps {r.get("gaps", 0)} ({r.get("gap_ms", 0)} ms)'
                     + ('  re-recorded' if r.get('attempts', 1) > 1 else ''))
    if ALBUM_NOTES.get(info['query']):
        lines += ['', 'Note: ' + ALBUM_NOTES[info['query']]]
    open(f'{d}/tracklist.txt', 'w').write('\n'.join(lines) + '\n')


def album_clip(info, num):
    """Site clip for a full album: from its chosen track's finished m4a."""
    k, t = pick_track(info['tracks'])
    src = track_file(info, k, t)
    if not os.path.exists(src):
        return False
    a = au.load(src)
    out = clip_path(num, info['query'])
    ok = au.encode_clip(a, out, f'{WORK}/{slug(info["query"])}.jpg', t, info.get('artist') or 'Hemi-Sync', clean_album_name(info['album']))
    if ok:
        shutil.copy(f'{WORK}/{slug(info["query"])}.jpg', f'{SITE}/albums/{slug(info["query"])}.jpg')
        info.update(clip_file=os.path.basename(out), clip_track=t)
        json.dump(info, open(meta_path(info['query']), 'w'), ensure_ascii=False, indent=1)
    return ok and clip_ok(out)


def run_albums(only=None):
    order = [a for a in ALBUMS if not only or a in only]; swaps = list(SWAPS); done = 0; idx = 0
    while idx < len(order):
        name = order[idx]; num = (ALBUMS.index(name) + 1) if name in ALBUMS else idx + 1
        P.set(phase='albums', albums={'current_album': name, 'done': done})
        P.item('album', name, status='active')
        try:
            info = read_album(name)
            if info['voice_suspect'] and swaps:
                new = swaps.pop(0)
                log('SWAP', name, '->', new, '(voice-suspect description)')
                P.item('album', name, status='swapped', note='voice-suspect, replaced by ' + new)
                ALBUM_NOTES[new] = f'swapped in for "{name}" (voice-suspect)'
                order[idx] = new
                P.items(P.d['items'] + [{'kind': 'album', 'name': new, 'status': 'pending', 'duration_s': 0, 'note': 'swap'}])
                continue
            st = {}
            sp = f'{album_dir(info)}/.status.json'
            if os.path.exists(sp):
                st = json.load(open(sp))
            want = [(k, t) for k, t in info['tracks'] if not (st.get(str(k), {}).get('ok') and track_ok(track_file(info, k, t), st[str(k)].get('length')))]
            P.set(albums={'track_count': len(info['tracks'])})
            if want:
                if not ensure_album_downloaded(info['album']):
                    log('album download incomplete, trying per track', name)
                    for k, t in want:
                        ensure_track_downloaded(k)
                if not info.get('lengths') or len(info['lengths']) < len(info['tracks']):
                    info['lengths'] = measure_lengths(info)
                    json.dump(info, open(meta_path(name), 'w'), ensure_ascii=False, indent=1)
                    if not h.open_album(name):
                        raise RuntimeError('album not found again: ' + name)
                lengths = record_album(info, want)
                P.set(state='encoding', message=f'encoding {clean_album_name(info["album"])}')
                res = finish_album(info, lengths, want, st)
                write_album_files(info, res)
                st.update({str(k): v for k, v in res.items()})
            bad = [k for k, t in info['tracks'] if not st.get(str(k), {}).get('ok')]
            album_clip(info, num)
            total = sum(v.get('len_s', 0) for v in st.values())
            if not bad:
                done += 1
                P.item('album', name, status='done', duration_s=int(total), note=ALBUM_NOTES.get(name, ''))
                delete_download(info['album'])
                log('ALBUM DONE', name, len(info['tracks']), 'tracks', int(total), 's')
                notify(f'ALBUM DONE {clean_album_name(info["album"])}: {len(info["tracks"])} tracks, {int(total // 60)} min, all checks passed')
                idx += 1
            else:
                log('ALBUM INCOMPLETE', name, 'failed tracks', bad)
                tries = st.get('_tries', 0) + 1 if isinstance(st.get('_tries', 0), int) else 1
                json.dump({**st, '_tries': tries}, open(sp, 'w'), ensure_ascii=False, indent=1)
                if tries >= 3:
                    P.item('album', name, status='failed', note=f'tracks {bad} failed the check')
                    notify(f'ALBUM FAILED {name}: tracks {bad}')
                    idx += 1
        except RedoTrack:
            log('redo album after heal', name); continue
        except Exception as e:
            if 'Screen Copy' in str(e):
                raise
            log('ERR album', name, repr(e), traceback.format_exc()[-600:])
            time.sleep(10)
            P.item('album', name, note='error, retrying: ' + repr(e)[:80])
            errs = getattr(run_albums, 'errs', {}); errs[name] = errs.get(name, 0) + 1; run_albums.errs = errs
            if errs[name] >= 3:
                P.item('album', name, status='failed', note=repr(e)[:120]); idx += 1
        P.set(clips={'done': count_clips()})
        publish(force=True)
    P.set(albums={'done': done})


PUBLISHED = [None]


def publish(force=False):
    """Every 4 new clips (and at the end): site json, artist tags, commit, push, deploy, check one MP3 live."""
    n = count_clips()
    if PUBLISHED[0] is None:
        PUBLISHED[0] = n if not force else -1
    if not force and n - PUBLISHED[0] < 4:
        return
    try:
        subprocess.run(['python3', 'hsretag.py'], cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, timeout=600)
        subprocess.run(['python3', 'hssite.py'], cwd=os.path.dirname(os.path.abspath(__file__)), capture_output=True, timeout=120)
        g = lambda *a: subprocess.run(['git'] + list(a), cwd=REPO, capture_output=True, text=True, timeout=300)
        g('add', 'site/audio/samples.json', 'site/audio/albums.json', 'site/audio/albums')
        subprocess.run('git add site/audio/*.mp3', shell=True, cwd=REPO)
        g('commit', '-m', f'Audio: {n} of 22 Hemi-Sync one-minute clips ({time.strftime("%d.%m.%Y")})\n\n'
          'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n'
          'Claude-Session: https://claude.ai/code/session_01NceKU9CD57DmmcThDwnk3v')
        g('pull', '--rebase', '-q'); g('push', '-q', 'origin', 'main')
        d = subprocess.run('ACCESS_ON=1 bash deploy.sh', shell=True, cwd=REPO, capture_output=True, text=True, timeout=900)
        newest = sorted(f for f in os.listdir(SITE) if f.endswith('.mp3'))[-1]
        code = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '30', '--resolve',
                               'therapies.markobosko.org:443:104.21.27.25', f'https://therapies.markobosko.org/audio/{newest}'],
                              capture_output=True, text=True).stdout
        log('PUBLISHED', n, 'clips; deploy rc', d.returncode, newest, 'HTTP', code)
        notify(f'PUBLISHED {n} clips, {newest} HTTP {code}')
        PUBLISHED[0] = n
    except Exception as e:
        log('publish failed', repr(e))


HALLU = re.compile(r"sous-titrage|thank you|thanks for watching|subtitles|amara|\bmfp\b|\bmusic\b|♪|\.\.\.", re.I)


def speech_words(seg):
    """Local Whisper (MANTRA_VOICE :8837/hear, offline) on 20 s from the middle: words that are not the usual
    music hallucinations. 0 = no speech heard."""
    import tempfile, urllib.request
    try:
        m = len(seg) // 2; part = seg[max(0, m - 10 * au.SR): m + 10 * au.SR]
        with tempfile.TemporaryDirectory() as td:
            w = os.path.join(td, 'v.wav'); au.save(part, w)
            data = open(w, 'rb').read()
        req = urllib.request.Request('http://127.0.0.1:8837/hear?lang=auto', data=data, headers={'Content-Type': 'audio/wav'})
        txt = json.loads(urllib.request.urlopen(req, timeout=180).read()).get('text', '')
        words = [x for x in re.findall(r"[\w']+", HALLU.sub(' ', txt)) if len(x) > 1]
        return len(words), txt[:120]
    except Exception as e:
        return -1, repr(e)[:80]


def notify(line):
    with open(MUSIC + '/events.log', 'a') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + line + '\n')


# ------------------------------------------------------------------ site json

WHY_HR = {}


def write_site_json():
    samples = []
    metas = {}
    for f in os.listdir(WORK):
        if f.endswith('.json'):
            try:
                m = json.load(open(f'{WORK}/{f}'))
                metas[m['query']] = m
            except Exception:
                pass
    for f in sorted(os.listdir(SITE)):
        if not f.endswith('.mp3'):
            continue
        m = next((x for x in metas.values() if x.get('clip_file') == f), None)
        if not m:
            continue
        samples.append({'file': f, 'title': m.get('clip_track', ''), 'album': clean_album_name(m['album']),
                        'artist': m.get('artist') or 'Hemi-Sync', 'category': 'Puni albumi' if m['query'] in ALBUMS or m['query'] in SWAPS and int(f[:2]) <= 10 else 'Uzorci',
                        'reason': m.get('reason', '')})
    json.dump(samples, open(f'{SITE}/samples.json.tmp', 'w'), ensure_ascii=False, indent=1)
    os.replace(f'{SITE}/samples.json.tmp', f'{SITE}/samples.json')


def init_items():
    items = []
    for name in CLIP_CANDIDATES:
        if name not in ALBUMS:
            items.append({'kind': 'clip', 'name': name, 'status': 'done' if clip_ok(existing_clip(name)) else 'pending', 'duration_s': 60, 'note': ''})
    for name in ALBUMS:
        items.append({'kind': 'album', 'name': name, 'status': 'pending', 'duration_s': 0, 'note': ALBUM_NOTES.get(name, '')})
    P.items(items)


def main():
    global P
    P = Progress()
    init_items()
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    log('START', cmd, 'free on emulator', free_kb(), 'kB')
    try:
        if cmd in ('clips', 'all'):
            P.set(phase='clips')
            run_clips()
        if cmd in ('albums', 'all'):
            run_albums(sys.argv[2:] or None)
        if cmd == 'site':
            write_site_json()
        P.set(phase='done', state='idle', message='finished', clips={'done': count_clips()})
        log('FINISHED', cmd)
    except Exception as e:
        log('FATAL', repr(e), traceback.format_exc()[-800:])
        P.set(phase='error', state='error', message=repr(e)[:200])
        raise


if __name__ == '__main__':
    main()
