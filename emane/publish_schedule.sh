#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test -f emane/schedule.xml || python3 main.py --input input/nodes.json --emane-xml emane/schedule.xml
command -v emaneevent-tdmaschedule >/dev/null || { echo 'ERROR: emaneevent-tdmaschedule not found'; exit 1; }
emaneevent-tdmaschedule emane/schedule.xml -i lo
