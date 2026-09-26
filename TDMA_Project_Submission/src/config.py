"""Project-wide constants.

RADIO_RANGE is a *default*. It is configurable (``--range`` on the CLI) so the
same code can be reused for other radios and so tests can use small numbers.
The assignment fixes it at 500 metres.
"""

RADIO_RANGE: float = 500.0          # metres (assignment value)
REQUIRED_NODE_COUNT: int = 16       # final assignment mode
RANDOM_RESTARTS: int = 300          # number of random orderings in the optimiser
RANDOM_SEED: int = 42               # fixed seed => reproducible results
