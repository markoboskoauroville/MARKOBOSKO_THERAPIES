"""hsaudio: clean Screen Copy captures and encode them (offline, ffmpeg + sox + numpy).

The emulator under load drops short blocks of digital silence (about 21-43 ms, exact zeros) into
the playback capture, then ramps back in. clean() cuts those blocks out with a 4 ms crossfade, and
trims the exact-zero lead-in and tail (before the track started, after it ended).
"""
import json, os, subprocess, tempfile
import numpy as np

SR = 48000


def load(path):
    raw = subprocess.run(['sox', path, '-t', 'raw', '-e', 'float', '-b', '32', '-c', '2', '-r', str(SR), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def save(a, path):
    p = subprocess.run(['sox', '-t', 'raw', '-e', 'float', '-b', '32', '-c', '2', '-r', str(SR), '-',
                        '-e', 'signed', '-b', '24', path], input=a.astype(np.float32).tobytes(), capture_output=True)
    return p.returncode == 0


def zero_runs(a, min_len):
    z = (np.abs(a).sum(1) == 0).astype(np.int8)
    d = np.diff(np.concatenate([[0], z, [0]]))
    s = np.where(d == 1)[0]; e = np.where(d == -1)[0]
    return [(int(x), int(y)) for x, y in zip(s, e) if y - x >= min_len]


def clean(a, max_gap_s=0.5, xf_ms=4):
    """Return (cleaned, report)."""
    nz = np.where(np.abs(a).sum(1) > 0)[0]
    if len(nz) == 0:
        return a[:0], {'silent': True}
    a = a[nz[0]:nz[-1] + 1]
    runs = [(s, e) for s, e in zero_runs(a, 256) if e - s <= max_gap_s * SR]   # dropouts are >= ~20 ms; shorter zero runs are music (fade-ins)
    xf = int(SR * xf_ms / 1000)
    out = []; pos = 0
    for s, e in runs:
        seg = a[pos:s]
        if out and len(seg) > xf and len(out[-1]) > xf:
            prev = out[-1]
            r = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
            prev[-xf:] = prev[-xf:] * (1 - r) + seg[:xf] * r
            seg = seg[xf:]
        out.append(seg.copy()); pos = e
    out.append(a[pos:].copy())
    c = np.concatenate(out) if out else a
    return c, {'gaps_removed': len(runs), 'gap_s': round(sum(e - s for s, e in runs) / SR, 3)}


def stats(a):
    if len(a) == 0:
        return {'len_s': 0, 'rms': 0, 'peak': 0}
    return {'len_s': round(len(a) / SR, 2), 'rms': round(float(np.sqrt((a.astype(np.float64) ** 2).mean())), 5),
            'peak': round(float(np.abs(a).max()), 4)}


def silent_stretches(a, floor=0.0005, win_s=2.0):
    """Count windows (win_s) whose RMS is under floor: a dead-air check."""
    w = int(SR * win_s); n = len(a) // w
    if n == 0:
        return 0
    r = np.sqrt((a[:n * w].reshape(n, w, 2).astype(np.float64) ** 2).mean(axis=(1, 2)))
    return int((r < floor).sum())


def encode_clip(a, out_mp3, cover, title, artist, album, start_s=45, dur_s=60, fade_s=2):
    s = int(start_s * SR)
    if len(a) < s + dur_s * SR:
        s = max(0, len(a) - dur_s * SR)
    seg = a[s:s + dur_s * SR].astype(np.float64)
    pk = np.abs(seg).max()
    if pk > 0:
        seg *= (10 ** (-1 / 20)) / pk
    f = int(fade_s * SR); r = np.linspace(0, 1, f)[:, None]
    seg[:f] *= r; seg[-f:] *= r[::-1]
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, 'c.wav'); save(seg.astype(np.float32), w)
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', w]
        if cover and os.path.exists(cover):
            cmd += ['-i', cover, '-map', '0:a', '-map', '1:v', '-c:v', 'mjpeg', '-disposition:v', 'attached_pic',
                    '-metadata:s:v', 'title=Album cover', '-metadata:s:v', 'comment=Cover (front)']
        cmd += ['-c:a', 'libmp3lame', '-b:a', '192k', '-ar', '44100', '-id3v2_version', '3',
                '-metadata', f'title={title}', '-metadata', f'artist={artist}', '-metadata', f'album={album}', out_mp3]
        return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def encode_track(a, out_m4a, cover, title, artist, album, track, total):
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, 't.wav'); save(a, w)
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', w]
        if cover and os.path.exists(cover):
            cmd += ['-i', cover, '-map', '0:a', '-map', '1:v', '-c:v', 'copy', '-disposition:v', 'attached_pic']
        cmd += ['-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-metadata', f'title={title}', '-metadata', f'artist={artist}',
                '-metadata', f'album_artist={artist}', '-metadata', f'album={album}', '-metadata', f'track={track}/{total}',
                '-movflags', '+faststart', out_m4a]
        return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def probe_len(path):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', path],
                       capture_output=True, text=True).stdout
    try:
        return float(json.loads(o)['format']['duration'])
    except Exception:
        return 0.0
