#!/bin/bash
# hsrec.sh: start (or resume) the Hemi-Sync recording queue, unattended, in tmux session "hemisync-rec".
#   hsrec.sh [all|clips|albums [Album ...]|site]     default: all
# Resumable: files that already passed the sound and length check are skipped.
# Needs: emulator-5556 running with Hemi-Sync Flow signed in (started online), Screen Copy (Mantra) v31 running.
# No internet once an album is downloaded, no AI, no credits. Log: ~/Music/HemiSync/record.log
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
MODE=${1:-all}; shift 2>/dev/null || true
if tmux has-session -t hemisync-rec 2>/dev/null; then
  echo "hemisync-rec is already running (tmux attach -t hemisync-rec)"; exit 0
fi
if ! screencopy status >/dev/null 2>&1; then echo "Screen Copy (Mantra) is not running"; exit 2; fi
if ! ~/Library/Android/sdk/platform-tools/adb -s emulator-5556 get-state >/dev/null 2>&1; then echo "emulator-5556 is not running"; exit 3; fi
mkdir -p ~/Music/HemiSync
ARGS="$MODE"; for a in "$@"; do ARGS="$ARGS '$a'"; done
tmux new-session -d -s hemisync-rec "cd '$HERE' && caffeinate -i python3 -u hsrun.py $ARGS 2>&1 | tee -a ~/Music/HemiSync/run.out"
echo "started hemisync-rec: $MODE $*"
