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

**Deploy.** `bash deploy.sh` (wrangler from the Mac, `wrangler pages deploy` only, never `wrangler deploy`, no wrangler.jsonc, no Worker).
It stops if the Pages project does not exist. The token is read from ~/Downloads/API/Cloudflare.api.txt and never printed.
The repo is public and unpromoted: no README, no description.

**Project 2 parts and what is still missing (21.11.2026).**
- `site/player.js` is the one player module (sample list + demo therapy mode share one audio element); it reads `site/audio/samples.json` (22 clips) and `site/audio/albums.json` + `site/audio/albums/` (covers, why_hr = Croatian sentence). The audio worker delivers them; until then the page shows "stiže uskoro". Deploy copies `site/` without `*.md`.
- Demo therapy mode: butterchurn (vendor/, from MANTRA_ROOM android assets) with four slow presets, no audio input (so no beat flashes), plus slow colour fades; controls fade after 4 s; Esc or the Izlaz button exits.
- The therapist section is a TODO: no name is published for him. The kognitive app for Emina has no public release (repo kognius_app is private), so its button reads "Uskoro".
- "BrainSync" text is from hemi-sync.com facts only; replace with BRAINSYNC.md facts when delivered.
- DJ Mantra's players are inline code in its single index.html, not a module file, so this site has its own player.js.
