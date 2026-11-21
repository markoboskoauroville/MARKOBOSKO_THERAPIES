"""hssite: write site/audio/samples.json and site/audio/albums.json from the album metadata.
Texts (why / why_hr / reason) are hand-written per album below; categories are the app's, shown in Croatian."""
import html, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsrun import WORK, SITE, REPO, ALBUMS, slug, clean_album_name

CAT_HR = {'Meditation': 'Meditacija', 'Child & Baby': 'Djeca i san', 'Reduce Stress': 'Manje stresa', 'Creativity': 'Kreativnost',
          'Relaxation': 'Opuštanje', 'Sleep': 'San', 'Healing': 'Iscjeljenje'}

# slug -> (why, why_hr, reason_hr for the sample list)
TEXT = {
    'guitar-lullaby': ("Solo classical guitar lullabies by Ricardo Cobo with Hemi-Sync sleep frequencies; soft, predictable and warm.",
                       "Nježne uspavanke na klasičnoj gitari (Ricardo Cobo) uz Hemi-Sync frekvencije za san: tiho, toplo i predvidljivo, bez iznenađenja.",
                       "Mirna gitara, ujednačen ritam, bez glasa."),
    'lullaby': ("The world's favourite lullabies on flute (Laura Nashman) and piano (John Alonso) with Hemi-Sync sleep frequencies.",
                "Najdraže uspavanke svijeta na flauti (Laura Nashman) i klaviru (John Alonso) uz Hemi-Sync frekvencije za san; za djecu i odrasle.",
                "Flauta i klavir, poznate uspavanke."),
    'dreamland': ("Flute and piano by Laura Nashman, made for drifting into sleep.",
                  "Flauta i klavir Laure Nashman za lagani prijelaz u san; mekan zvuk koji ne traži pažnju.",
                  "Flauta i klavir, vrlo mekano."),
    'cloudscapes': ("Ray Dretske's gentle musical imagery for deep relaxation, one even 30-minute piece.",
                    "Blage glazbene slike Raya Dretskea za duboko opuštanje: jedna ujednačena skladba od 30 minuta, bez naglih promjena.",
                    "Ujednačena, prozračna glazba."),
    'meeresbrandung-surf': ("Ocean surf and distant gulls with Hemi-Sync; pure nature sound, no melody to follow.",
                       "Šum morskih valova i daleki galebovi uz Hemi-Sync: čisti zvuk prirode, bez melodije koju treba pratiti.",
                       "Valovi mora, zvuk prirode."),
    'enchanted-forest': ("Ambient music with nature sounds by Jeffree Clarkson, made for relaxation, massage and energy work.",
                         "Ambijentalna glazba sa zvukovima šume (Jeffree Clarkson) za opuštanje, masažu i rad s energijom.",
                         "Šuma i ambijent, smirujuće."),
    'pearl-moon': ("Andrzej Rejman's luminous, flowing ambient textures for a peaceful inner journey.",
                   "Svijetle, tekuće ambijentalne teksture Andrzeja Rejmana za miran unutarnji odmor.",
                   "Meke teksture, tekući tok."),
    'himalayan-soul': ("Haunting flute music by Ilona Selke: a quiet refuge from a hurried day.",
                       "Tiha, zanosna flauta Ilone Selke: utočište od užurbanog dana.",
                       "Flauta, mirna i topla."),
    'eternity-within': ("Spacious ambient music by Frank Danna for stillness.",
                        "Prostrana ambijentalna glazba Franka Danne za tišinu i mir.",
                        "Prostran, miran ambijent."),
    'galilean-moons': ("Rob Dobson's slow-shifting atmospheres inspired by Jupiter's moons.",
                       "Spore, lebdeće atmosfere Roba Dobsona nadahnute Jupiterovim mjesecima.",
                       "Sporo, lebdeće, bez ritma."),
    'oasis': ("Andrzej Rejman's warm keyboards, piano and strings: a safe harbour from daily worries.",
              "Topli klavijaturni zvuk, klavir i gudači Andrzeja Rejmana: sigurna luka od svakodnevnih briga.",
              "Klavir i gudači, toplo."),
}


# Player order (Marko, 21.11.2026: numbered 1..22 so he can pick favourites by number): the clip-only albums in the
# order they were recorded, then the full albums' clips in album order. New clips append; numbers never move.
CLIP_ORDER = ['himalayan-soul', 'eternity-within', 'galilean-moons', 'oasis', 'orbits-of-hope', 'reflections',
              'pachelbel-canon', 'prisms', 'portraits', 'music-for-rejuvenation', 'komuso', 'romantic-wonder']
SMALL = {'in', 'of', 'the', 'a', 'an', 'and', 'to', 'with', 'for', 'on', 'at', 'by', 'de', 'del', 'la', 'le', 'des'}
ARTIST_FIX = {'Johanne Pachelbel': 'Johann Pachelbel'}


def title_case(t):
    w = t.split()
    return ' '.join(x if (x.isupper() and len(x) > 1) else (x.lower() if i and x.lower() in SMALL else x[:1].upper() + x[1:])
                    for i, x in enumerate(w))


def clean_title(track, album, ntracks):
    t = re.sub(r'^\s*\d+\s*[.:)\-_]*\s*', '', track or '')
    t = re.sub(r'\b(extended|version|edit|remaster(ed)?)\b', '', t, flags=re.I)
    t = re.sub(r'(?<=\w)-(?=\w)', ' ', t).replace('-', ' ')
    t = re.sub(r'\s+', ' ', t).strip(' -.')
    t = title_case(t) if t else album
    if ntracks > 1 and len(t.split()) == 1 and t.lower() not in album.lower():
        t = f'{album}: {t}'
    return t


def clean_artist(a):
    a = html.unescape(a or '')
    a = re.sub(r',?\s*\b(Ph\.?\s?D\.?|M\.?D\.?|Dr\.)', '', a).strip(' ,')
    return ARTIST_FIX.get(a, a) or 'Hemi-Sync'


def load_metas():
    out = {}
    for f in os.listdir(WORK):
        if f.endswith('.json'):
            try:
                m = json.load(open(f'{WORK}/{f}'))
                out[slug(m['query'])] = m
            except Exception:
                pass
    return out


def renumber(metas):
    """Give every clip its final number: NN-slug.mp3 (git mv when tracked). Returns [(n, slug, file)]."""
    order = CLIP_ORDER + [slug(a) for a in ALBUMS]
    present = {f[3:-4]: f for f in os.listdir(SITE) if f.endswith('.mp3') and re.match(r'\d\d-', f)}
    extra = sorted(k for k in present if k not in order)
    out = []; n = 0
    for s in order + extra:
        if s not in present:
            continue
        n += 1
        want = f'{n:02d}-{s}.mp3'
        if present[s] != want:
            tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', f'site/audio/{present[s]}'], cwd=REPO,
                                     capture_output=True).returncode == 0
            if tracked:
                subprocess.run(['git', 'mv', '-f', f'site/audio/{present[s]}', f'site/audio/{want}'], cwd=REPO, capture_output=True)
            else:
                os.replace(f'{SITE}/{present[s]}', f'{SITE}/{want}')
            if s in metas:
                metas[s]['clip_file'] = want
                json.dump(metas[s], open(f'{WORK}/{metas[s]["_file"]}', 'w'), ensure_ascii=False, indent=1)
        out.append((n, s, want))
    return out


def main():
    metas = load_metas()
    for f in os.listdir(WORK):
        if f.endswith('.json'):
            try:
                m = json.load(open(f'{WORK}/{f}')); metas[slug(m['query'])]['_file'] = f
            except Exception:
                pass
    samples = []
    for n, s, f in renumber(metas):
        m = metas.get(s)
        if not m:
            continue
        t = TEXT.get(s, ('', '', ''))
        album = clean_album_name(m['album'])
        samples.append({'n': n, 'file': f, 'title': clean_title(m.get('clip_track'), album, len(m['tracks'])), 'album': album,
                        'artist': clean_artist(m.get('artist')), 'category': 'Hemi-Sync uzorci',
                        'category_in_app': m.get('category', ''), 'reason': t[2]})
    json.dump(samples, open(f'{SITE}/samples.json', 'w'), ensure_ascii=False, indent=1)
    # albums: the full albums first (best-first order of ALBUMS), then the clip-only ones, up to 12
    order = [slug(a) for a in ALBUMS] + sorted(k for k in metas if k not in [slug(a) for a in ALBUMS])
    albums = []
    for s in order:
        m = metas.get(s)
        if not m or m.get('voice_suspect') or not os.path.exists(f'{SITE}/albums/{s}.jpg'):
            continue
        t = TEXT.get(s, ('', '', ''))
        lengths = m.get('lengths') or {}
        dur = sum(lengths.values()) if lengths else (m.get('clip_track_length') if len(m['tracks']) == 1 else None)
        albums.append({'slug': s, 'album': clean_album_name(m['album']), 'artist': clean_artist(m.get('artist')),
                       'category_in_app': m.get('category', ''), 'tracks': len(m['tracks']),
                       'duration': f'{int(dur // 60)} min' if dur else '', 'why': t[0], 'why_hr': t[1],
                       'cover': f'{s}.jpg', 'in_clips': any(x['file'][3:-4] == s for x in samples)})
        if len(albums) >= 12:
            break
    json.dump(albums, open(f'{SITE}/albums.json', 'w'), ensure_ascii=False, indent=1)
    print(len(samples), 'samples,', len(albums), 'albums')


if __name__ == '__main__':
    main()
