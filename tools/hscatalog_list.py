"""hscatalog_list: enumerate every album of Hemi-Sync Flow: Explore -> Applications -> <each category> -> Albums (A-Z).
Writes ~/Music/HemiSync/catalog_albums.json {album: [categories]} incrementally (resumable)."""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hsdrv as h

OUT = os.path.expanduser('~/Music/HemiSync/catalog_albums.json')
CATS = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []


def list_albums():
    names = []; same = 0
    for _ in range(80):
        ns = h.nodes(); new = 0
        for n in ns:
            t = n['text']
            if not t or '\n' in t or len(t) == 1 or t in ('Albums',) or not (250 < n['b'][1] and n['b'][3] < 2130):
                continue
            if n['b'][0] > 1000:
                continue
            if t not in names:
                names.append(t); new += 1
        same = same + 1 if not new else 0
        if same >= 2:
            break
        h.swipe(540, 1850, 540, 700, 600); time.sleep(1)
    return names


def main():
    data = json.load(open(OUT)) if os.path.exists(OUT) else {'albums': {}, 'done_cats': []}
    for cat in CATS:
        if cat in data['done_cats']:
            continue
        ok = h.to_album_list(cat)
        if not ok:
            print('no album list for', cat, flush=True)
            data['done_cats'].append(cat); json.dump(data, open(OUT, 'w'), ensure_ascii=False, indent=1); continue
        names = list_albums()
        for a in names:
            data['albums'].setdefault(a, [])
            if cat not in data['albums'][a]:
                data['albums'][a].append(cat)
        data['done_cats'].append(cat)
        json.dump(data, open(OUT, 'w'), ensure_ascii=False, indent=1)
        print(cat, len(names), 'total unique', len(data['albums']), flush=True)


if __name__ == '__main__':
    main()
