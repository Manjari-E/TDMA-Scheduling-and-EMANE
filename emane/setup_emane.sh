#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EMANE_DIR="$PROJECT_DIR/emane"
MODEL_SRC="/usr/share/emane/xml/models/mac/tdmaeventscheduler/tdmaradiomodel.xml"
mkdir -p "$EMANE_DIR"
test -f "$MODEL_SRC" || { echo "ERROR: $MODEL_SRC not found"; exit 1; }
cp "$MODEL_SRC" "$EMANE_DIR/tdmaradiomodel.xml"

python3 - "$PROJECT_DIR" <<'PY'
import json, pathlib, sys
root=pathlib.Path(sys.argv[1]); emane=root/"emane"; nodes=json.loads((root/"input/nodes.json").read_text()); ordered=sorted(nodes)

nem_tpl='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nem SYSTEM "file:///usr/share/emane/dtd/nem.dtd">
<nem>
  <transport definition="transvirtual{n}.xml"/>
  <mac definition="tdmaradiomodel.xml"/>
  <phy>
    <param name="fixedantennagain" value="0.0"/>
    <param name="fixedantennagainenable" value="on"/>
    <param name="bandwidth" value="1M"/>
    <param name="noisemode" value="all"/>
    <param name="propagationmodel" value="precomputed"/>
    <param name="systemnoisefigure" value="4.0"/>
    <param name="subid" value="7"/>
  </phy>
</nem>
'''
trans_tpl='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE transport SYSTEM "file:///usr/share/emane/dtd/transport.dtd">
<transport name="Node {n} Virtual Transport" library="transvirtual">
  <param name="bitrate" value="0"/>
  <param name="devicepath" value="/dev/net/tun"/>
  <param name="device" value="emane{idx}"/>
  <param name="address" value="172.30.1.{n}"/>
  <param name="mask" value="255.255.0.0"/>
</transport>
'''
for n,_name in enumerate(ordered,1):
    (emane/f"nem{n}.xml").write_text(nem_tpl.format(n=n))
    (emane/f"transvirtual{n}.xml").write_text(trans_tpl.format(n=n,idx=n-1))
lines=['<?xml version="1.0" encoding="UTF-8"?>','<!DOCTYPE platform SYSTEM "file:///usr/share/emane/dtd/platform.dtd">','<platform name="TDMA 16 Node Platform">',
'  <param name="otamanagerchannelenable" value="on"/>','  <param name="otamanagerdevice" value="lo"/>','  <param name="otamanagergroup" value="224.1.2.8:45702"/>',
'  <param name="eventservicegroup" value="224.1.2.8:45703"/>','  <param name="eventservicedevice" value="lo"/>','  <param name="controlportendpoint" value="0.0.0.0:47000"/>']
for n in range(1,len(ordered)+1): lines.append(f'  <nem id="{n}" definition="nem{n}.xml"/>')
lines.append('</platform>'); (emane/"platform.xml").write_text("\n".join(lines)+"\n")
PY

echo "Generated 16 NEM definitions, 16 transports, platform.xml and TDMA model."
echo 'Generate schedule: python3 main.py --input input/nodes.json --emane-xml emane/schedule.xml'
