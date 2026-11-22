# TAKEOVER: Marko Bosko Therapies

**What it is.** The first project of Marko Bosko's new site https://markoboskotherapies.pages.dev: an immersive therapy room. A person in a
wheelchair sits in a room whose four walls are projected with an underwater Caribbean reef, with speakers around the room, all driven by a
Mac Mini. One calm static page, in this order: hero picture, "The setup" picture with two plain sentences, the equipment table with
prices, "About me" with two links (https://markobosko.pages.dev and https://djmantra.pages.dev; DJ Mantra was chosen as his sound and
rhythm site). Project 2 (same day, momentaryupdates.md): "Soba za terapiju bojom i zvukom" with a Hemi-Sync (BrainSync) explanation, a sample player, a full-screen demo therapy mode, recommended albums, "For Brigita" (Hemi-Sync Flow store links), instruments (Stonewhistle, data/instruments.json), Marko Borić's card and two downloads. The whole site is in Croatian (Marko, 21.11.2026). Marko's request, word for word: momentaryupdates.md (21.11.2026).

**Decisions.**
- No donation bowl, Marko's decision of 21.11.2026 (an exception to MANTRA_MANIFEST modules/donation-bowl.md).
- Thomann sells no short-throw projectors and no Mac Mini: the projectors link to beamer-discount.de, the Mac mini to apple.com/de.
  Every price was read on 21.11.2026 (Thomann JSON-LD `price`, beamer-discount JSON-LD offer, Apple's page data) and is marked as such.
- Thomann rate-limits (HTTP 429 after about 15 quick requests, search behind a Cloudflare check): one request every 10 to 20 seconds.

**Pictures.** `site/img/room.jpg` (hero) and `site/img/setup.jpg` must be photoreal Nano Banana (Gemini) renders, 16:9, never drawn art, never
stock. Until they exist the page shows a neutral placeholder. The prompts are in Drive: `Chromium Downloads/Gemini/_batch/batch-markobosko-therapies.json`
(copy it over batch.json, the Gemini worker on chromium-vm makes `hero-room.png` and `setup-room.png` in `Gemini/markobosko-therapies`; the
Chrome profiles there must be signed in to Gemini first). Publish them as JPEG 1600 px wide into site/img/ and run deploy.sh.
The worker script on the VM was patched on 21.11.2026 (skips `paste_files` when a batch has no reference images); the original is /tmp/gemini-worker.bak there.

**Deploy.** `bash deploy.sh` (since 21.11.2026 the project is cloud + VM only: cloud sessions have CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID in their environment; the Mac fallback still reads ~/Downloads/API; `wrangler pages deploy` only, never `wrangler deploy`, no wrangler.jsonc, no Worker).
It stops if the Pages project does not exist. The token is read from ~/Downloads/API/Cloudflare.api.txt and never printed.
The repo is public and unpromoted: no README, no description.

**Project 2 parts and what is still missing (21.11.2026).**
- `site/player.js` is the one player module (sample list + demo therapy mode share one audio element); it reads `site/audio/samples.json` (22 clips) and `site/audio/albums.json` + `site/audio/albums/` (covers, why_hr = Croatian sentence). The audio worker delivers them; until then the page shows "stiže uskoro". Deploy copies `site/` without `*.md`.
- Demo therapy mode: butterchurn (vendor/, from MANTRA_ROOM android assets) with four slow presets, no audio input (so no beat flashes), plus slow colour fades; controls fade after 4 s; Esc or the Izlaz button exits.
- Alan Tower (Marko, 21.11.2026: he created and organizes the Hemi-Sync Flow app) has a short card with Marko description only: no public source confirms his role in the app, so no title, link or biography is published.
- "BrainSync" text is from hemi-sync.com facts only; replace with BRAINSYNC.md facts when delivered.
- DJ Mantra's players are inline code in its single index.html, not a module file, so this site has its own player.js.
**Hemi-Sync samples (21.11.2026), code in tools/ (no audio in git except the site MP3s).**
- Source: the Hemi-Sync Flow app on the Pixel_7_API_35 emulator (emulator-5556, headless, signed in). Never emulator-5554.
  The recorder is Screen Copy (Mantra) v31+: `screencopy record start|next|stop --serial emulator-5556` captures the
  device's own playback to WAV (always pass --serial: without it the CLI acts on tab 1). No Mac audio routing.
- Player: 12 numbered one-minute samples (site/audio/NN-slug.mp3, samples.json with n, title, album, artist; rows
  "NN. Title · Artist"). Made by hsrun.py clips + hssite.py (numbering, clean titles/artists) + hsretag.py.
- Catalogue sampler (Marko's redefinition, 21.11.2026): `tools/hsrec.sh catalog` (Macro Recorder action
  "Hemi-Sync catalogue sampler") = hscatalog.py: for every album in the 35 Applications category lists, the FIRST track
  is streamed (no downloads, "no caching, real time"), seeked to its middle (seek bar tap), 20 s recorded, 0.5 s fades,
  -1 dBFS. Master: ~/Music/Hemi Sync samples/<Album>/<NNN> <Track>.mp3; site copy site/audio/catalog/ + catalog.json
  (n, album, title, artist, voice, file, duration_s), deployed every 20. Resumable; tmux "hemisync-rec"; log
  ~/Music/HemiSync/record.log; progress ~/Music/HemiSync/progress.json (for Hemi-Sync Recording Monitor (Mantra)).
- Voice flag: local Whisper (MANTRA_VOICE :8837/hear, offline), words beyond the usual music hallucinations.
- Lessons: (1) emulator storage under ~500 MB = Android "storage low": the app's download worker silently does nothing
  and streaming used to play silence; Google app + YouTube updates were uninstalled on 5556 to free space.
  (2) The overloaded emulator drops 21-43 ms blocks of exact zeros into the capture while its UI is busy: press HOME
  while recording; hsaudio.clean() cuts zero runs >= 256 samples with a 4 ms crossfade. (3) uiautomator dumps fail
  while the mini player exists (marquee never idles): close it with its X (60,2035) or force-stop the app.
  (4) Screen Copy v31 leaked pipe fds (~18/min) until record start failed after ~1 h: the sampler restarts it above
  1200 fds (v32 fixes it). (5) A second playback capture (scrcpy CLI) silences Screen Copy's capture: never run one.
  (6) The app cold-starts only online; once started, downloaded tracks play in airplane mode.
- /admin (21.11.2026): "Alan Tower – javni radovi" is in `admin_pending/admin/index.html`, NOT in `site/`, because Cloudflare Zero Trust Access is not enabled on the account (API: access.api.error.not_enabled). `deploy.sh` copies it only with `ACCESS_ON=1`, after an Access app for `markoboskotherapies.pages.dev/admin*` (allow marko.bosko@auroville.community and marko.bosko@gmail.com, One-time PIN) exists. robots.txt disallows /admin; sitemap lists only `/`.

**Project 1, new setup (21.11.2026, momentaryupdates.md).** Nothing on the floor: 4 Optoma UST lasers upside down on OWM3000 ceiling
mounts, 8 Adam Audio D3V (4 pairs, 3/8" thread) upside down on iriz CM550 ceiling mounts, each pair over Lindy USB-over-Cat6 to the
Mac mini, macOS Aggregate Device (8 ch, drift correction), Ableton Live 12 Suite + Envelop for Live. A phone beside each speaker
(Godox MTH02 holder) shows that speaker's sound and is a camera for Skeleton (repo SKELETON, pose match + reward). New pictures: Drive
batch `Gemini/_batch/batch-markobosko-therapies-ceiling.json` → `Gemini/markobosko-therapies-ceiling/{room,setup,movement}.png`.
Open checks: ZH430UST inverted mode + OWM3000 fit (Optoma), D3V inverted use (Adam), ceiling power at each pair.

**MIDIPan section (22.11.2026, momentaryupdates.md).** New `#midipan` section before About me (nav link "MIDIPan"): Marko's device (MIDIPan by Shiela Dixon, Etsy shop shieladixon, listing 1735074092; 12 oval pads in a ring + 1 centre pad counted on the listing photos; MIDI over USB/TRS; price/size not on the page text: size unknown) and a PROPOSAL (not built): finger-coordination games, voice says pad + finger, pads light, reward character on the projected wall. Picture is the neutral `.ph` placeholder. Not added to data/instruments.json (that file is Stonewhistle only, one maker). Maker photos are references only, never published: /private/tmp/claude-501/-Users-markobosko-Developer-claude-code/7dd31525-1b01-4fd4-ad5e-8388698a855a/scratchpad/therapies/refs/. Lifestyle pictures: prompt A sent once in Gemini (prompts in /private/tmp/claude-501/-Users-markobosko-Developer-claude-code/7dd31525-1b01-4fd4-ad5e-8388698a855a/scratchpad/therapies/prompts.txt), B and C not made; waiting for the master's picture review. Lesson: the Claude-in-Chrome tab lived in a background tab of the "Work" window on the BenQ, so only a 876 px viewport screenshot was possible (too small for 1600 px); needs Macro Recorder running to front the window on the MacBook screen and capture 1:1.

**MIDIPan picture brief (22.11.2026, round 1 corrections).** Prompts A, B, C for the next Gemini run (attach midipan-1, midipan-2, room-ref; 16:9): see scratchpad .../therapies/prompts-next-run.txt, repeated here in short. A wide (person in wheelchair, device seen a little from above so 12 oval pads + centre pad countable, fingers spread on different pads, one pad lit, larger turtle on the wall); B close (two hands from above, five fingers each, one pad lit); C together (therapist or family member beside, both looking at the wall, exactly two people). Section is now numbered 08 in the page. Nothing published until the master has looked.

**MIDIPan pictures made on the VM (22.11.2026).** Drive `Chromium Downloads/Gemini/markobosko-therapies-midipan/` (midipan-a-wide.png [2nd try; first in _wrong/], midipan-b-hands.png, midipan-c-together.png; refs/ = midipan-top, midipan-angle, room). 1024x572 each. NOT published; waiting for the master's OK. Publishing = JPEG from the VM into site/img, replace the `.ph` placeholder in #midipan (A main, B and C beside/below), deploy.sh, screenshot desktop+phone.
