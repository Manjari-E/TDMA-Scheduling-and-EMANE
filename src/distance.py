"""Euclidean distance and the single, central "is it in range?" rule."""
from __future__ import annotations

import math
from typing import Tuple

Point = Tuple[float, float]


def calculate_distance(a: Point, b: Point) -> float:
    """distance = sqrt((x2-x1)^2 + (y2-y1)^2), in metres."""
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def is_within_range(distance: float, radio_range: float) -> bool:
    """Communication rule used EVERYWHERE: distance <= range means connected.

    Design decision (the assignment does not say what happens at exactly
    500.0 m): the boundary is inclusive. Keeping the rule in one function
    guarantees it is applied consistently.
    """
    return distance <= radio_range
