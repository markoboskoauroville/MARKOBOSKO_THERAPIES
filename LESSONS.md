# LESSONS: Marko Bosko Therapies

**Screenshots of the live page (22.11.2026).** `chrome --headless=new --screenshot=...` gave blank dark images for this page (also with a virtual time budget); a Playwright session driving the installed Chrome (`executable_path`, `--mute-audio`, viewport 1280x900 and 390x844, click the nav link, read `scrollY`, element top and horizontal overflow) gave real pictures. Use it, look at the images, never count a blank one as a check.

**Capture size (22.11.2026).** A Gemini picture taken by the Claude-in-Chrome extension screenshot is only the viewport (about 876 px wide) and the tab sits in a background tab of the "Work" window, here on the BenQ: not publishable at 1600 px. A real 16:9 picture needs Macro Recorder running (input lock, window fronted on the MacBook screen, 1:1 retina capture by window id). Never start Macro Recorder or Queen from a worker: Marko starts them.

**Deploy rule (22.11.2026).** MANTRA_MANIFEST modules/websites-deploy-to-cloudflare.md: GitHub holds code only, no Actions workflow; deploy from the Mac with deploy.sh (wrangler pages deploy). No workflow is added to this repo.

**Instruments list.** data/instruments.json is Stonewhistle only (one maker); a device from another maker gets its own section, not a second list.

**Score rounds.** Round 1: 6 of 10 (text section live; pictures missing, live screenshots blank, no teach step, no LESSONS, deploy rule not re-read). Round 2: after the corrections in this file; pictures still wait for Macro Recorder.

**Pictures on the VM (22.11.2026, Marko: "for therapist page, use virtual machine to generate images").** Gemini worker on chromium-vm made the three MIDIPan pictures (batch-markobosko-therapies-midipan.json, results Drive `Chromium Downloads/Gemini/markobosko-therapies-midipan/`). Per-item refs worked; native size 1024x572 (no 16:9 setting: it is in the prompt); restart the worker after replacing batch.json (it sleeps an hour). Review by scp'd JPEG previews only. Not published until the master's OK. Details in the chromium-vm skill (22.11.2026 section).

**Scale in picture prompts (22.11.2026).** Round 1 B and C showed the MIDIPan about twice its size. Estimate from the Etsy photos (hand on the device in photo 11, USB-C plug and screws in photo 2): about 20 to 22 cm across, two palm widths. Round 2 prompts state "about 20 cm, a side plate, a hand is half as wide as the disc", attach the photo with a hand, and forbid objects on the walls: B came out right (disc about 2.4 hand widths), C right. Prompts: scratchpad therapies/vm/batch-midipan-round2.json. A is live (img/midipan-a.jpg, 1024 px); B and C wait for the master's OK (gallery .mp-gal in style.css is ready, not used yet).

**Round 3: pictures accepted (22.11.2026).** Round 1 (6 of 10): text section only, small Mac-captured draft, blank screenshots. Round 2: VM Gemini worker made A, B, C at native 1024x572; A accepted on the 2nd try (first had a garbled logo), B and C rejected for the device twice its size and invented wall objects. Round 3: prompts state the size against a hand with a hand photo as reference; B and C accepted by the master and published with A, plus an AI-illustration caption.

**Round 3: 9 of 10 (stray screenshot), round 4: 10.** Lesson: screenshots go to the scratchpad, never into the repo folder (my Playwright script wrote them to the current directory; give it absolute scratchpad paths).

**Order change (22.11.2026).** Moving a section = move the block, renumber the numeral and the kicker of every section that shifts, move the nav link; ids stay. Check no prose or script refers to the numbers (none did). The page is hand-edited, build_v4.py is stale.

**myNoise wording (22.11.2026).** Never state licence terms or prices from memory or from a brief: quote only the author's public page. A screenshot of someone's site is a copy: do not publish it. Stale builder scripts keep wrong lines alive: fix the source too.

**Shared VM worker (22.11.2026).** batch.json is one file for all jobs: another session replaced it while my redo waited, and my item never ran until I resubmitted after "round ends". Check `tail worker.log` for "round ends" before replacing batch.json and give each item a new name instead of moving files on Drive (Drive moves took minutes). The model cannot draw a 4 x 4 knob grid in a wide shot: ask for it only in a close top view (B).

**Facts about Marko's own gear (22.11.2026).** The manifest's measured notes (e.g. MANTRA_MANIFEST modules/oxi-e16.md: every encoder has a push with its own action) come BEFORE the maker's web page. I wrote "I do not know whether the E16 knobs can be pressed" on a page signed by the device's owner; read the manifest first (grep modules for the device name).

**Round: sound system (22.11.2026).** Read the maker's output counts before drawing a chain (CQ-20B: 8 independent XLR outputs, Alt Out only duplicates): the nine-feed problem showed up only because I checked. Genelec SAM monitors have no switches (GLM needed for setup) but the 7360A works stand-alone at a fixed 85 Hz. When the master and Marko choose, rewrite every place that carries the old chain (hero, setup, scheme SVG, table, totals, E16 clause, "before buying"), and re-sum the table by script.

**Way back (22.11.2026).** Chrome fires `popstate` on fragment jumps too (state null): a handler that hid the back button on every popstate killed it at once; react only to entries that carry our stored state. The button's "far scroll" check must wait for the smooth scroll to settle (debounced) or it hides during the travel. When closing a pushState panel with history.back() the previous entry's stored scroll would be restored: flag the pop and skip it. The first inventory showed 114 of 115 outside links opened in the same tab: count before changing.

**Picture grid (22.11.2026).** Read every maker's terms before taking a picture: four of the twelve confirmed makers (Koshi, Meinl, High Spirits, Meerklang) forbid reproduction without written permission, so the grid uses the ones whose terms are silent or only state ownership; the brief's catalogue list is not the list of usable makers. Shopify shops (Hokema, Hess) answer 429 to curl after a few requests: check their links in a real browser. A drum PNG in a wide banner needs a crop centred on its alpha box, not on the file. Put the "opens in a new tab" sign inside the name line, or it falls onto a line of its own in a flex tile. Remo's og:image is the only product picture in its HTML (the rest is a JS gallery).

## 23.11.2026
- The player module here is shared with markoboskocv (/showreel/, /aivideos/). Change it here first, copy it over, and version-tag it (`?v=N`), or browsers keep the old one.
