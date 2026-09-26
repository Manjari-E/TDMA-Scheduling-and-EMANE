#!/usr/bin/env python3
"""TDMA Schedule Planner and Optimizer - command-line entry point."""
from __future__ import annotations

import argparse
import sys

from src.config import RADIO_RANGE, RANDOM_RESTARTS, RANDOM_SEED
from src.emane_bridge import build_emane_schedule_xml
from src.input_parser import InputError, load_nodes
from src.report import build_report
from src.result_export import export_results
from src.scheduler import build_schedule


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Centralised TDMA schedule optimiser using distance-2 graph colouring.")
    p.add_argument("--input", "-i", required=True, help="JSON file: {\"Node_01\": [x, y], ...}")
    p.add_argument("--range", "-r", type=float, default=RADIO_RANGE, dest="radio_range",
                   help=f"radio range in metres (default {RADIO_RANGE:g})")
    p.add_argument("--verbose", "-v", action="store_true", help="list every conflict and reuse pair")
    p.add_argument("--output", "-o", help="also write the report to this text file")
    p.add_argument("--results-dir", default="results",
                   help="directory for generated result files (default: results)")
    p.add_argument("--dev-mode", action="store_true",
                   help="allow any number of nodes (testing only; assignment mode needs exactly 16)")
    p.add_argument("--restarts", type=int, default=RANDOM_RESTARTS,
                   help=f"random-order restarts in the optimiser (default {RANDOM_RESTARTS})")
    p.add_argument("--seed", type=int, default=RANDOM_SEED, help=f"random seed (default {RANDOM_SEED})")
    p.add_argument("--emane-xml", help="(bonus, untested with EMANE) write an EMANE TDMA schedule XML")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.radio_range <= 0:
        print("error: --range must be a positive number of metres.", file=sys.stderr)
        return 2
    if args.restarts < 0:
        print("error: --restarts must be >= 0.", file=sys.stderr)
        return 2
    try:
        nodes = load_nodes(args.input, strict_count=not args.dev_mode)
    except InputError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    result = build_schedule(nodes, args.radio_range, restarts=args.restarts, seed=args.seed)
    report = build_report(result, verbose=args.verbose)
    print(report)

    try:
        results_dir = export_results(result, report, args.results_dir)
        print(f"Results written to {results_dir}")
    except OSError as exc:
        print(f"error: could not write results to '{args.results_dir}': {exc}", file=sys.stderr)
        return 2

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(report)
            print(f"Report written to {args.output}")
        except OSError as exc:
            print(f"error: could not write '{args.output}': {exc}", file=sys.stderr)
            return 2

    if not result.validation.is_valid:
        print("SCHEDULE INVALID - do not use.", file=sys.stderr)
        return 1

    if args.emane_xml:
        try:
            with open(args.emane_xml, "w", encoding="utf-8") as fh:
                fh.write(build_emane_schedule_xml(result.node_to_slot))
            print(f"EMANE schedule XML written to {args.emane_xml} (NOT tested with EMANE)")
        except OSError as exc:
            print(f"error: could not write '{args.emane_xml}': {exc}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
