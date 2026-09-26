#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test -f emane/platform.xml || ./emane/setup_emane.sh
test -f emane/schedule.xml || python3 main.py --input input/nodes.json --emane-xml emane/schedule.xml
[[ $EUID -eq 0 ]] || { echo 'Use: sudo ./emane/run_emane.sh'; exit 1; }
exec emane -r -l 4 emane/platform.xml
