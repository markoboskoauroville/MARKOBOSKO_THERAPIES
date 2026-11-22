# LESSONS: Marko Bosko Therapies

**Screenshots of the live page (22.11.2026).** `chrome --headless=new --screenshot=...` gave blank dark images for this page (also with a virtual time budget); a Playwright session driving the installed Chrome (`executable_path`, `--mute-audio`, viewport 1280x900 and 390x844, click the nav link, read `scrollY`, element top and horizontal overflow) gave real pictures. Use it, look at the images, never count a blank one as a check.

**Capture size (22.11.2026).** A Gemini picture taken by the Claude-in-Chrome extension screenshot is only the viewport (about 876 px wide) and the tab sits in a background tab of the "Work" window, here on the BenQ: not publishable at 1600 px. A real 16:9 picture needs Macro Recorder running (input lock, window fronted on the MacBook screen, 1:1 retina capture by window id). Never start Macro Recorder or Queen from a worker: Marko starts them.

**Deploy rule (22.11.2026).** MANTRA_MANIFEST modules/websites-deploy-to-cloudflare.md: GitHub holds code only, no Actions workflow; deploy from the Mac with deploy.sh (wrangler pages deploy). No workflow is added to this repo.

**Instruments list.** data/instruments.json is Stonewhistle only (one maker); a device from another maker gets its own section, not a second list.

**Score rounds.** Round 1: 6 of 10 (text section live; pictures missing, live screenshots blank, no teach step, no LESSONS, deploy rule not re-read). Round 2: after the corrections in this file; pictures still wait for Macro Recorder.

**Pictures on the VM (22.11.2026, Marko: "for therapist page, use virtual machine to generate images").** Gemini worker on chromium-vm made the three MIDIPan pictures (batch-markobosko-therapies-midipan.json, results Drive `Chromium Downloads/Gemini/markobosko-therapies-midipan/`). Per-item refs worked; native size 1024x572 (no 16:9 setting: it is in the prompt); restart the worker after replacing batch.json (it sleeps an hour). Review by scp'd JPEG previews only. Not published until the master's OK. Details in the chromium-vm skill (22.11.2026 section).
