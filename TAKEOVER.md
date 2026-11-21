# TAKEOVER: Marko Bosko Therapies

**What it is.** The first project of Marko Bosko's new site https://markoboskotherapies.pages.dev: an immersive therapy room. A person in a
wheelchair sits in a room whose four walls are projected with an underwater Caribbean reef, with speakers around the room, all driven by a
Mac Mini. One calm static page, in this order: hero picture, "The setup" picture with two plain sentences, the equipment table with
prices, "About me" with two links (https://markobosko.pages.dev and https://djmantra.pages.dev; DJ Mantra was chosen as his sound and
rhythm site). Nothing else. Marko's request, word for word: momentaryupdates.md (21.11.2026).

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
