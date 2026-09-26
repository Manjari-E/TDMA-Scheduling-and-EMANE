#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 main.py --input input/nodes.json --range 500 --emane-xml emane/schedule.xml
python3 -m unittest discover -v
./emane/setup_emane.sh
echo 'Next: sudo ./emane/run_emane.sh'
echo 'Then:  ./emane/publish_schedule.sh'
