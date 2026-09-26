"""Generate an EMANE TDMA full schedule from the computed slot assignment."""
from __future__ import annotations
from typing import Dict, Optional
from xml.sax.saxutils import quoteattr
from .scheduler import group_by_slot

def nem_ids(node_names) -> Dict[str, int]:
    return {name: i for i, name in enumerate(sorted(node_names), start=1)}

def build_emane_schedule_xml(
    node_to_slot: Dict[str, int],
    nem_map: Optional[Dict[str, int]] = None,
    slot_duration_us: int = 1500,
    slot_overhead_us: int = 50,
    frequency: str = "2.4G",
    datarate: str = "1M",
    bandwidth: str = "1M",
    power: str = "0",
    service_class: str = "0",
) -> str:
    nem_map = nem_map or nem_ids(node_to_slot)
    slots = group_by_slot(node_to_slot)
    total = (max(slots) + 1) if slots else 0
    out = [
        "<emane-tdma-schedule>",
        f'  <structure frames="1" slots="{total}" slotoverhead="{slot_overhead_us}" slotduration="{slot_duration_us}" bandwidth={quoteattr(bandwidth)}/>',
        f'  <multiframe frequency={quoteattr(frequency)} power={quoteattr(power)} class={quoteattr(service_class)} datarate={quoteattr(datarate)}>',
        '    <frame index="0">',
    ]
    for slot, members in slots.items():
        ids = ",".join(str(nem_map[m]) for m in sorted(members, key=lambda m: nem_map[m]))
        out += [f'      <slot index="{slot}" nodes="{ids}">', '        <tx/>', '      </slot>']
    out += ['    </frame>', '  </multiframe>', '</emane-tdma-schedule>']
    return "\n".join(out) + "\n"
