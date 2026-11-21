"""hsretag: set the artist tag of every clip MP3 and album M4A from the album metadata (~/Music/HemiSync/.work/*.json).
The artist comes from the app's Downloads list (read when the download is deleted). Audio is copied, not re-encoded."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsrun import WORK, SITE, MUSIC, album_dir, clean_album_name
from hssite import clean_artist, clean_title


def tag(path, artist, title=None):
    cur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags=artist,title', '-of', 'json', path],
                         capture_output=True, text=True).stdout
    tags = {k.lower(): v for k, v in (json.loads(cur or '{}').get('format', {}).get('tags', {}) or {}).items()}
    if tags.get('artist') == artist and (not title or tags.get('title') == title):
        return False
    tmp = path + '.tmp' + os.path.splitext(path)[1]
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', path, '-map', '0', '-c', 'copy', '-metadata', f'artist={artist}']
    if title:
        cmd += ['-metadata', f'title={title}']
    if path.endswith('.m4a'):
        cmd += ['-metadata', f'album_artist={artist}', '-disposition:v', 'attached_pic']
    else:
        cmd += ['-id3v2_version', '3']
    r = subprocess.run(cmd + [tmp], capture_output=True, text=True)
    if r.returncode == 0:
        os.replace(tmp, path); return True
    print('retag failed', path, r.stderr[-200:])
    return False


for f in sorted(os.listdir(WORK)):
    if not f.endswith('.json'):
        continue
    m = json.load(open(f'{WORK}/{f}'))
    a = clean_artist(m.get('artist'))
    if not a:
        continue
    if m.get('clip_file') and os.path.exists(f'{SITE}/{m["clip_file"]}'):
        if tag(f'{SITE}/{m["clip_file"]}', a, clean_title(m.get('clip_track'), clean_album_name(m['album']), len(m['tracks']))):
            print('clip', m['clip_file'], '->', a)
    d = album_dir(m)
    if os.path.isdir(d):
        for t in sorted(os.listdir(d)):
            if t.endswith('.m4a') and tag(f'{d}/{t}', a):
                print('track', t, '->', a)
