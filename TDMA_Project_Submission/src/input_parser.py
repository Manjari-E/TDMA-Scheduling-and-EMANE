"""Reading and validating the JSON node file.

Expected format (name -> [x, y] in metres):

    {"Node_01": [0.0, 0.0], "Node_02": [300.0, 0.0]}
"""
from __future__ import annotations

import json
import math
from typing import Dict, List, Tuple

from .config import REQUIRED_NODE_COUNT

Coordinates = Tuple[float, float]
Nodes = Dict[str, Coordinates]


class InputError(Exception):
    """Raised for any problem with the user's input (shown without a traceback)."""


def _reject_duplicate_keys(pairs: List[Tuple[str, object]]) -> dict:
    """json.loads silently keeps the LAST duplicate key. We want an error."""
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"Duplicate node name in JSON: '{key}'")
        result[key] = value
    return result


def _is_number(value: object) -> bool:
    # bool is a subclass of int in Python, so True/False must be excluded explicitly.
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def parse_nodes(text: str, strict_count: bool = True) -> Nodes:
    """Parse and validate JSON text.

    strict_count=True  -> exactly REQUIRED_NODE_COUNT (16) nodes (assignment mode).
    strict_count=False -> any count >= 1 (development / testing mode).
    """
    try:
        data = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise InputError(
            f"Invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})"
        ) from exc

    if not isinstance(data, dict):
        raise InputError(
            "Top level of the JSON must be an object mapping node names to [x, y]."
        )
    if not data:
        raise InputError("The JSON contains no nodes.")

    nodes: Nodes = {}
    for name, coords in data.items():
        if not name.strip():
            raise InputError("Node names must not be empty or blank.")
        if not isinstance(coords, list) or len(coords) != 2:
            raise InputError(
                f"Node '{name}': coordinates must be a list of exactly two numbers "
                f"[x, y], got {coords!r}."
            )
        if not all(_is_number(c) for c in coords):
            raise InputError(
                f"Node '{name}': coordinates must be numeric, got {coords!r}."
            )
        x, y = float(coords[0]), float(coords[1])
        if not (math.isfinite(x) and math.isfinite(y)):
            raise InputError(f"Node '{name}': coordinates must be finite numbers.")
        nodes[name] = (x, y)

    if strict_count and len(nodes) != REQUIRED_NODE_COUNT:
        raise InputError(
            f"Assignment mode requires exactly {REQUIRED_NODE_COUNT} nodes, "
            f"found {len(nodes)}. Use --dev-mode to allow other sizes for testing."
        )
    return nodes


def load_nodes(path: str, strict_count: bool = True) -> Nodes:
    """Read a JSON file from disk and validate it."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except FileNotFoundError as exc:
        raise InputError(f"Input file not found: {path}") from exc
    except OSError as exc:
        raise InputError(f"Cannot read input file '{path}': {exc}") from exc
    return parse_nodes(text, strict_count=strict_count)
