#!/bin/bash
# hsrec.sh: start (or resume) the Hemi-Sync recording queue, unattended, in tmux session "hemisync-rec".
#   hsrec.sh [catalog|all|clips|albums [Album ...]|site]     default: catalog
#   catalog = 20 s from the middle of the first track of every album (hscatalog.py, streaming, no downloads)
# Resumable: files that already passed the sound and length check are skipped.
# Needs: emulator-5556 running with Hemi-Sync Flow signed in (started online), Screen Copy (Mantra) v31 running.
# No internet once an album is downloaded, no AI, no credits. Log: ~/Music/HemiSync/record.log
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
MODE=${1:-catalog}; shift 2>/dev/null || true
if tmux has-session -t hemisync-rec 2>/dev/null; then
  echo "hemisync-rec is already running (tmux attach -t hemisync-rec)"; exit 0
fi
if ! screencopy status >/dev/null 2>&1; then echo "Screen Copy (Mantra) is not running"; exit 2; fi
if ! ~/Library/Android/sdk/platform-tools/adb -s emulator-5556 get-state >/dev/null 2>&1; then echo "emulator-5556 is not running"; exit 3; fi
mkdir -p ~/Music/HemiSync
if [ "$MODE" = catalog ]; then CMD="python3 -u hscatalog.py"; else
  ARGS="$MODE"; for a in "$@"; do ARGS="$ARGS '$a'"; done; CMD="python3 -u hsrun.py $ARGS"; fi
tmux new-session -d -s hemisync-rec "cd '$HERE' && caffeinate -i $CMD 2>&1 | tee -a ~/Music/HemiSync/run.out"
echo "started hemisync-rec: $MODE $*"
