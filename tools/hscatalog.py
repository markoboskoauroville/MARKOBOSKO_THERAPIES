"""hscatalog: 20-second sample from the MIDDLE of the FIRST track of EVERY album in Hemi-Sync Flow (Marko, 21.11.2026).
Real time: the track is streamed (no download, no app cache), seeked to its midpoint and recorded by Screen Copy (Mantra).

  python3 hscatalog.py            run / resume
  python3 hscatalog.py publish    rebuild site copy + catalog.json, commit, push, deploy

Album list: ~/Music/HemiSync/catalog_albums.json from hscatalog_list.py (35 Applications categories, A-Z lists).
Number = position in the A-Z list of all unique albums (catalog_index.json, fixed once; new albums appended).
Master: ~/Music/Hemi Sync samples/<Album>/<NNN> <Track>.mp3  (20 s, 0.5 s fades, -1 dBFS, zero-block repair, cover).
Site copy (made from the master): site/audio/catalog/NNN-slug.mp3 + site/audio/catalog.json. Deploy every 20 samples.
Voice: local Whisper (MANTRA_VOICE :8837) on the sample -> true / false / "unknown". Temp WAVs: /Volumes/EXT_1TB/HemiSyncTemp.
"""
import html, json, os, re, shutil, subprocess, sys, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import hsdrv as h
import hsaudio as au
import hsrun as R
from hsprogress import Progress
from hssite import clean_title, clean_artist

MASTER = os.path.expanduser('~/Music/Hemi Sync samples')
CAT_DIR = R.SITE + '/catalog'
TEMP = '/Volumes/EXT_1TB/HemiSyncTemp' if os.path.isdir('/Volumes/EXT_1TB') else os.path.expanduser('~/Music/HemiSync/.temp')
LIST = os.path.expanduser('~/Music/HemiSync/catalog_albums.json')
INDEX = os.path.expanduser('~/Music/HemiSync/catalog_index.json')
META = os.path.expanduser('~/Music/HemiSync/catalog_meta')
for d in (MASTER, CAT_DIR, TEMP, META):
    os.makedirs(d, exist_ok=True)
log = R.log
SEEK_X0, SEEK_X1, SEEK_Y = 87, 995, 1405
SAMPLE_S = 20


def index():
    data = json.load(open(LIST))
    albums = data['albums']
    idx = json.load(open(INDEX)) if os.path.exists(INDEX) else []
    known = {x['album'] for x in idx}
    for a in sorted(albums, key=lambda s: s.lower()):
        if a not in known:
            idx.append({'n': len(idx) + 1, 'album': a})
    json.dump(idx, open(INDEX, 'w'), ensure_ascii=False, indent=1)
    return idx, albums, data.get('done_cats', [])


def safe(s):
    return re.sub(r'[/:\\]', '-', html.unescape(s)).strip().rstrip('.')


def meta_path(n):
    return f'{META}/{n:03d}.json'


def is_done(n):
    if not os.path.exists(meta_path(n)):
        return False
    m = json.load(open(meta_path(n)))
    return os.path.exists(m.get('master', '')) and abs(au.probe_len(m['master']) - SAMPLE_S) < 1.0


ART = [r'(?:composed|performed|created|written)(?: and (?:composed|performed|produced))? by ([A-Z][\w.\-]+(?: [A-Z][\w.\-]+){0,3})',
       r'\bby ([A-Z][\w.\-]+(?: [A-Z][\w.\-]+){1,3})',
       r'(?:music|sounds|flute|guitar|piano|voice) of ([A-Z][\w.\-]+(?: [A-Z][\w.\-]+){1,3})',
       r'featur(?:es|ing) ([A-Z][\w.\-]+(?: [A-Z][\w.\-]+){1,3})',
       r'\b([A-Z][a-z]+ (?:[A-Z]\. )?[A-Z][a-z]+) and Hemi-Sync']


def artist_guess(desc):
    for p in ART:
        m = re.search(p, desc or '')
        if m and 'Hemi' not in m.group(1) and 'Monroe Institute' not in m.group(1):
            return clean_artist(m.group(1).rstrip('.,;'))
    return ''


def fd_count():
    try:
        pid = subprocess.run(['pgrep', '-f', 'MacOS/ScreenCopy'], capture_output=True, text=True).stdout.split()[0]
        return int(subprocess.run(f'lsof -p {pid} | wc -l', shell=True, capture_output=True, text=True).stdout.strip())
    except Exception:
        return 0


def restart_screencopy(why):
    log('SCREEN COPY RESTART:', why)
    R.notify('SCREEN COPY RESTART: ' + why)
    subprocess.run(['osascript', '-e', 'tell application "Screen Copy (Mantra)" to quit'], capture_output=True)
    time.sleep(6)
    subprocess.run(['open', '-a', 'Screen Copy (Mantra)'], capture_output=True)
    for _ in range(40):
        time.sleep(3)
        if R.tab_live():
            time.sleep(5); return True
    raise RuntimeError('Screen Copy could not be restarted')


def ocr_times():
    from ocr import ocr
    h.shot('/tmp/hs2/_pl.png')
    els = rem = None
    for t, _ in ocr('/tmp/hs2/_pl.png', (0, 1300, 1080, 1560)):
        m = re.fullmatch(r'(-?)(\d{1,2}):(\d\d)(?::(\d\d))?', t.strip().replace(' ', ''))
        if not m:
            continue
        v = (int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))) if m.group(4) else int(m.group(2)) * 60 + int(m.group(3))
        if m.group(1):
            rem = v
        else:
            els = v
    return els, rem


def back_to_list(cat):
    """From the full player/home after a sample: album page -> close the mini player (dumps work again) -> list."""
    h.front(); time.sleep(1)
    h.key('KEYCODE_BACK'); time.sleep(1.5)
    h.tap(60, 2035); time.sleep(1.5)          # X on the mini player (stops playback)
    ns = h.nodes(2)
    if any('\n' in n['text'] and n['text'].startswith('A\n') for n in ns):
        return True
    if h.find(ns, id='tv_title_album_name'):
        h.key('KEYCODE_BACK'); time.sleep(2)
        ns = h.nodes(2)
        if any('\n' in n['text'] and n['text'].startswith('A\n') for n in ns):
            return True
    return h.to_album_list(cat)


def quick_page():
    """One dump of the album page: title, category, description and the visible track rows (track 1 is all we need)."""
    ns = []
    for _ in range(4):
        ns = h.nodes()
        if h.find(ns, id='tv_name_of_track') and (h.find(ns, id='tv_album_description') or {'text': ''})['text']:
            break
        time.sleep(1.5)
    g = lambda i: (h.find(ns, id=i) or {'text': ''})['text']
    nums = [n for n in ns if n['id'] == 'tv_number_of_track']; names = [n for n in ns if n['id'] == 'tv_name_of_track']
    tracks = [(int(a['text'].strip('.') or 0), t['text']) for a, t in zip(nums, names)]
    return {'album': g('tv_title_album_name'), 'category': g('tv_title_album_category'), 'description': g('tv_album_description'),
            'tracks': sorted(tracks)}


import threading
VOICE_Q = []


def voice_worker():
    """Whisper runs beside the queue so it never holds up the next album."""
    while True:
        if not VOICE_Q:
            time.sleep(1); continue
        n, wavp = VOICE_Q.pop(0)
        try:
            seg = au.load(wavp)
            nw, heard = R.speech_words(seg)
            m = json.load(open(meta_path(n)))
            m['voice'] = 'unknown' if nw < 0 else bool(nw > 6); m['heard'] = heard
            json.dump(m, open(meta_path(n), 'w'), ensure_ascii=False, indent=1)
            log('VOICE', n, m['voice'], repr(heard)[:60])
        except Exception as e:
            log('voice check failed', n, repr(e)[:100])
        finally:
            if wavp.startswith(TEMP):
                try:
                    os.remove(wavp)
                except OSError:
                    pass


threading.Thread(target=voice_worker, daemon=True).start()


def take_sample(x, cat, P):
    n = x['n']; name = x['album']
    if not h.open_in_list(name):
        if not (h.to_album_list(cat) and h.open_in_list(name)):
            raise RuntimeError('album not found in ' + cat)
    info = quick_page()
    if not info['tracks']:
        info = h.album_page()
    if not info['tracks']:
        raise RuntimeError('no tracks')
    album = R.clean_album_name(info['album'] or name)
    k, track = info['tracks'][0]
    cover = f'{TEMP}/{n:03d}.jpg'
    h.shot(f'{TEMP}/{n:03d}.png')
    from PIL import Image
    Image.open(f'{TEMP}/{n:03d}.png').convert('RGB').crop((42, 325, 462, 745)).resize((400, 400), Image.LANCZOS).save(cover, quality=90)
    row = h.track_row(k)
    if not row:
        raise RuntimeError('first track row not visible')
    P.set(state='navigating', message=f'{n}: {album} - "{track}"')
    if not R.start_playback(row):
        raise RuntimeError('playback did not start (streaming)')
    R.open_full_player()
    els = rem = None
    for _ in range(10):
        els, rem = ocr_times()
        if rem:
            break
        time.sleep(1.5)
    length = (els or 0) + (rem or 0)
    if not length:
        raise RuntimeError('track length not readable')
    target = length / 2
    h.tap(int(SEEK_X0 + (SEEK_X1 - SEEK_X0) * 0.5), SEEK_Y); time.sleep(3)
    e2, r2 = ocr_times()
    if e2 is None or abs(e2 - target) > max(20, length * 0.08):
        h.tap(int(SEEK_X0 + (SEEK_X1 - SEEK_X0) * 0.5), SEEK_Y); time.sleep(3); e2, r2 = ocr_times()
    h.key('KEYCODE_HOME'); time.sleep(2)
    rec = f'cat {n:03d}'
    wav = R.wav_for(rec)
    if os.path.exists(wav):
        os.remove(wav)
    R.sc('record', 'start', '--name', rec)
    P.set(state='recording', message=f'{n}: {album} - recording 20 s from the middle ({int(target // 60)}:{int(target % 60):02d})')
    R.check_capture()
    time.sleep(SAMPLE_S + 2.5)
    R.sc('record', 'stop')
    P.set(state='encoding')
    a, rep = au.clean(au.load(wav))
    s = au.stats(a)
    if s['rms'] < 0.0003 or s['len_s'] < SAMPLE_S:
        raise RuntimeError(f'capture too quiet or short {s}')
    seg = a[-int(SAMPLE_S * au.SR):].astype(np.float64)      # the last 20 s: away from the HOME transition
    pk = np.abs(seg).max()
    seg *= (10 ** (-1 / 20)) / pk
    f = int(0.5 * au.SR); rmp = np.linspace(0, 1, f)[:, None]
    seg[:f] *= rmp; seg[-f:] *= rmp[::-1]
    title = clean_title(track, album, len(info['tracks']))
    artist = artist_guess(info['description'])
    folder = f'{MASTER}/{safe(album)}'
    os.makedirs(folder, exist_ok=True)
    master = f'{folder}/{n:03d} {safe(title)}.mp3'
    tw = f'{TEMP}/{n:03d}.wav'
    au.save(seg.astype(np.float32), tw)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', tw, '-i', cover, '-map', '0:a', '-map', '1:v', '-c:v', 'mjpeg',
           '-disposition:v', 'attached_pic', '-c:a', 'libmp3lame', '-b:a', '192k', '-ar', '44100', '-id3v2_version', '3',
           '-metadata', f'title={title}', '-metadata', f'artist={artist or "Hemi-Sync"}', '-metadata', f'album={album}',
           '-metadata', f'track={n}', master]
    if subprocess.run(cmd, capture_output=True).returncode != 0:
        raise RuntimeError('encode failed')
    voice, heard = 'unknown', ''
    m = {'n': n, 'album': album, 'album_raw': info['album'], 'title': title, 'track_raw': track, 'artist': artist,
         'voice': voice, 'heard': heard, 'master': master, 'cover': cover, 'duration_s': length, 'sample_from_s': int(target),
         'seeked_to_s': e2, 'category_in_app': info['category'], 'list': cat, 'tracks': len(info['tracks']),
         'description': info['description'], 'gaps': rep.get('gaps_removed', 0), 'gap_ms': int(rep.get('gap_s', 0) * 1000)}
    json.dump(m, open(meta_path(n), 'w'), ensure_ascii=False, indent=1)
    os.remove(wav); VOICE_Q.append((n, tw))
    log('CAT', n, album, '|', title, '|', artist, '| len', length, 'from', e2, '| gaps', m['gaps'])
    return m


def site_slug(s):
    return R.slug(s)[:60] or 'album'


def publish(idx):
    for _ in range(90):
        if not VOICE_Q:
            break
        time.sleep(1)
    out = []
    for x in idx:
        if not os.path.exists(meta_path(x['n'])):
            continue
        m = json.load(open(meta_path(x['n'])))
        if not os.path.exists(m['master']):
            continue
        f = f'{x["n"]:03d}-{site_slug(m["album"])}.mp3'
        dst = f'{CAT_DIR}/{f}'
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(m['master']):
            shutil.copy2(m['master'], dst)
        out.append({'n': m['n'], 'album': m['album'], 'title': m['title'], 'artist': m['artist'] or 'Hemi-Sync',
                    'voice': m['voice'], 'file': 'catalog/' + f, 'duration_s': m['duration_s']})
    json.dump(out, open(R.SITE + '/catalog.json.tmp', 'w'), ensure_ascii=False, indent=1)
    os.replace(R.SITE + '/catalog.json.tmp', R.SITE + '/catalog.json')
    g = lambda *a: subprocess.run(['git'] + list(a), cwd=R.REPO, capture_output=True, text=True, timeout=600)
    g('add', 'site/audio/catalog', 'site/audio/catalog.json')
    g('commit', '-m', f'Catalogue sampler: {len(out)} samples of 20 s ({time.strftime("%d.%m.%Y")})\n\n'
      'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n'
      'Claude-Session: https://claude.ai/code/session_01NceKU9CD57DmmcThDwnk3v')
    g('pull', '--rebase', '-q'); g('push', '-q', 'origin', 'main')
    d = subprocess.run('ACCESS_ON=1 bash deploy.sh', shell=True, cwd=R.REPO, capture_output=True, text=True, timeout=1200)
    newest = out[-1]['file'] if out else ''
    code = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '30', '--resolve',
                           'therapies.markobosko.org:443:104.21.27.25', f'https://therapies.markobosko.org/audio/{newest}'],
                          capture_output=True, text=True).stdout
    log('PUBLISHED catalogue', len(out), 'samples; deploy rc', d.returncode, newest, 'HTTP', code)
    R.notify(f'PUBLISHED catalogue {len(out)} samples, {newest} HTTP {code}')


CATS_FILE = os.path.expanduser('~/Music/HemiSync/catalog_categories.json')


def discover(cat):
    """Open the category's A-Z album list and add its albums to catalog_albums.json and the index (append-only)."""
    from hscatalog_list import list_albums
    data = json.load(open(LIST)) if os.path.exists(LIST) else {'albums': {}, 'done_cats': []}
    if cat in data['done_cats']:
        return h.to_album_list(cat)
    if not h.to_album_list(cat):
        data['done_cats'].append(cat); json.dump(data, open(LIST, 'w'), ensure_ascii=False, indent=1)
        log('no album list in', cat); return False
    for a in list_albums():
        data['albums'].setdefault(a, [])
        if cat not in data['albums'][a]:
            data['albums'][a].append(cat)
    data['done_cats'].append(cat)
    json.dump(data, open(LIST, 'w'), ensure_ascii=False, indent=1)
    for _ in range(4):
        h.swipe(540, 700, 540, 2000, 150)
    return True


def index_append():
    """Numbers in order of discovery (category order, then A-Z inside the list); never renumbered."""
    data = json.load(open(LIST))
    idx = json.load(open(INDEX)) if os.path.exists(INDEX) else []
    known = {x['album'] for x in idx}
    for cat in data['done_cats']:
        for a in sorted((a for a in data['albums'] if cat in data['albums'][a]), key=lambda s: s.lower()):
            if a not in known:
                idx.append({'n': len(idx) + 1, 'album': a}); known.add(a)
    json.dump(idx, open(INDEX, 'w'), ensure_ascii=False, indent=1)
    return idx, data['albums']


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'publish':
        publish(index_append()[0]); return
    cats = json.load(open(CATS_FILE))
    P = Progress(); R.P = P
    idx, albums = index_append()
    ndone = sum(is_done(x['n']) for x in idx); since = 0; t_avg = 120.0
    P.d['clips'] = {'done': ndone, 'total': len(idx), 'current': ''}
    P.set(phase='catalog', state='idle', message=f'catalogue: {len(idx)} albums known so far, {ndone} done')
    log('START catalogue', len(idx), 'known,', ndone, 'done; temp', TEMP)
    for x in idx:
        if os.path.exists(meta_path(x['n'])):
            m = json.load(open(meta_path(x['n'])))
            if m.get('voice') == 'unknown' and os.path.exists(m.get('master', '')):
                VOICE_Q.append((x['n'], m['master']))
    failed = {}
    for ci, cat in enumerate(cats):
        P.set(state='navigating', message=f'list {ci + 1}/{len(cats)}: {cat}')
        if not discover(cat):
            continue
        idx, albums = index_append(); num = {x['album']: x['n'] for x in idx}
        P.items([{'kind': 'album', 'name': f'{x["n"]:03d} {x["album"]}', 'status': 'done' if is_done(x['n']) else 'pending',
                  'duration_s': SAMPLE_S, 'note': ''} for x in idx])
        P.set(clips={'total': len(idx)})
        todo = [a for a in albums if cat in albums[a] and not is_done(num[a]) and failed.get(a, 0) < 3]
        log('LIST', ci + 1, cat, len(todo), 'to sample;', len(idx), 'albums known')
        for a in sorted(todo, key=lambda s: s.lower()):
            x = {'n': num[a], 'album': a}; key = f'{x["n"]:03d} {a}'
            if fd_count() > 1200:
                restart_screencopy(f'{fd_count()} open fds'); h.to_album_list(cat)
            P.item('album', key, status='active')
            P.set(clips={'done': ndone, 'current': a}, remaining_s=int((len(idx) - ndone) * t_avg))
            t0 = time.time()
            try:
                m = take_sample(x, cat, P)
                ndone += 1; since += 1
                P.item('album', key, status='done', note=('voice' if m['voice'] is True else ''))
                t_avg = 0.8 * t_avg + 0.2 * (time.time() - t0)
            except R.RedoTrack:
                log('redo after heal', a); failed[a] = failed.get(a, 0) + 1
            except Exception as e:
                failed[a] = failed.get(a, 0) + 1
                log('ERR catalogue', x['n'], a, repr(e)[:200])
                if 'Screen Copy' in str(e):
                    raise
                P.item('album', key, status='failed' if failed[a] >= 3 else 'pending', note=repr(e)[:100])
                try:
                    R.sc('record', 'stop')
                except Exception:
                    pass
            try:
                if not back_to_list(cat):
                    log('could not return to', cat)
            except Exception as e:
                log('ERR back', repr(e)[:120]); h.to_album_list(cat)
            if since >= 20:
                publish(idx); since = 0
    publish(idx)
    P.set(phase='done', state='idle', message=f'catalogue finished: {ndone} of {len(idx)}', clips={'done': ndone})
    log('FINISHED catalogue', ndone, 'of', len(idx))


if __name__ == '__main__':
    main()
