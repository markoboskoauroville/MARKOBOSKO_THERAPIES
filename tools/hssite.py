"""hssite: write site/audio/samples.json and site/audio/albums.json from the album metadata.
Texts (why / why_hr / reason) are hand-written per album below; categories are the app's, shown in Croatian."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsrun import WORK, SITE, ALBUMS, slug, clean_album_name

CAT_HR = {'Meditation': 'Meditacija', 'Child & Baby': 'Djeca i san', 'Reduce Stress': 'Manje stresa', 'Creativity': 'Kreativnost',
          'Relaxation': 'Opuštanje', 'Sleep': 'San', 'Healing': 'Iscjeljenje'}

# slug -> (why, why_hr, reason_hr for the sample list)
TEXT = {
    'guitar-lullaby': ("Solo classical guitar lullabies by Ricardo Cobo with Hemi-Sync sleep frequencies; soft, predictable and warm.",
                       "Nježne uspavanke na klasičnoj gitari (Ricardo Cobo) uz Hemi-Sync frekvencije za san: tiho, toplo i predvidljivo, bez iznenađenja.",
                       "Mirna gitara, ujednačen ritam, bez glasa."),
    'dreamland': ("Flute and piano by Laura Nashman, made for drifting into sleep.",
                  "Flauta i klavir Laure Nashman za lagani prijelaz u san; mekan zvuk koji ne traži pažnju.",
                  "Flauta i klavir, vrlo mekano."),
    'cloudscapes': ("Ray Dretske's gentle musical imagery for deep relaxation, one even 30-minute piece.",
                    "Blage glazbene slike Raya Dretskea za duboko opuštanje: jedna ujednačena skladba od 30 minuta, bez naglih promjena.",
                    "Ujednačena, prozračna glazba."),
    'meeresbrandung': ("Ocean surf and distant gulls with Hemi-Sync; pure nature sound, no melody to follow.",
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


def main():
    metas = load_metas()
    samples = []
    for f in sorted(os.listdir(SITE)):
        if not f.endswith('.mp3'):
            continue
        s = f[3:-4]
        m = metas.get(s)
        if not m:
            continue
        t = TEXT.get(s, ('', '', ''))
        samples.append({'file': f, 'title': m.get('clip_track') or clean_album_name(m['album']), 'album': clean_album_name(m['album']),
                        'artist': m.get('artist') or 'Hemi-Sync', 'category': CAT_HR.get(m.get('category'), m.get('category') or 'Uzorci'),
                        'reason': t[2]})
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
        albums.append({'slug': s, 'album': clean_album_name(m['album']), 'artist': m.get('artist') or '',
                       'category_in_app': m.get('category', ''), 'tracks': len(m['tracks']),
                       'duration': f'{int(dur // 60)} min' if dur else '', 'why': t[0], 'why_hr': t[1],
                       'cover': f'{s}.jpg', 'in_clips': any(x['file'][3:-4] == s for x in samples)})
        if len(albums) >= 12:
            break
    json.dump(albums, open(f'{SITE}/albums.json', 'w'), ensure_ascii=False, indent=1)
    print(len(samples), 'samples,', len(albums), 'albums')


if __name__ == '__main__':
    main()
