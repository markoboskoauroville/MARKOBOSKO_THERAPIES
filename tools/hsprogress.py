"""progress.json for Hemi-Sync Recording Monitor (Mantra): rewritten atomically every 5 s by a thread."""
import datetime, json, os, threading, time

P = os.path.expanduser('~/Music/HemiSync/progress.json')


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec='seconds')


class Progress:
    def __init__(self, clips_total=22, albums_total=10):
        old = {}
        try:
            old = json.load(open(P))
        except Exception:
            pass
        self.d = {'updated': now(), 'phase': 'clips', 'state': 'idle', 'message': '',
                  'clips': {'done': 0, 'total': clips_total, 'current': ''},
                  'albums': {'done': 0, 'total': albums_total, 'current_album': '', 'current_track': '', 'track_index': 0,
                             'track_count': 0, 'track_elapsed_s': 0, 'track_length_s': 0},
                  'remaining_s': 0, 'started': old.get('started') or now(), 'items': []}
        self.track_t0 = None
        self.lock = threading.Lock()
        threading.Thread(target=self._loop, daemon=True).start()

    def set(self, **kw):
        with self.lock:
            for k, v in kw.items():
                if k in ('clips', 'albums'):
                    self.d[k].update(v)
                else:
                    self.d[k] = v
        self.write()

    def items(self, items):
        with self.lock:
            self.d['items'] = items
        self.write()

    def item(self, kind, name, **kw):
        with self.lock:
            for it in self.d['items']:
                if it['kind'] == kind and it['name'] == name:
                    it.update(kw)
        self.write()

    def track_started(self, length_s):
        self.track_t0 = time.time()
        self.set(albums={'track_elapsed_s': 0, 'track_length_s': int(length_s or 0)})

    def write(self):
        with self.lock:
            if self.track_t0 and self.d['state'] == 'recording':
                self.d['albums']['track_elapsed_s'] = int(time.time() - self.track_t0)
            self.d['updated'] = now()
            tmp = P + '.tmp'
            os.makedirs(os.path.dirname(P), exist_ok=True)
            with open(tmp, 'w') as f:
                json.dump(self.d, f, ensure_ascii=False, indent=1)
            os.replace(tmp, P)

    def _loop(self):
        while True:
            time.sleep(5)
            try:
                self.write()
            except Exception:
                pass
