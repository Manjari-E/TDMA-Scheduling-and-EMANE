import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

PYTHON = sys.executable

COMMANDS = [
    [
        PYTHON,
        "main.py",
        "--input",
        "input/nodes.json",
    ],
    [
        PYTHON,
        "visualization/network_topology.py",
    ],
    [
        PYTHON,
        "visualization/conflict_graph.py",
    ],
    [
        PYTHON,
        "visualization/tdma_schedule.py",
    ],
    [
        PYTHON,
        "visualization/spatial_reuse.py",
    ],
]


def run_command(command):
    print("\n" + "=" * 70)
    print("RUNNING:", " ".join(command))
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        print("\nERROR: Command failed.")
        print(" ".join(command))
        sys.exit(result.returncode)


def main():
    print("=" * 70)
    print("TDMA SCHEDULER - COMPLETE EXPERIMENT PIPELINE")
    print("=" * 70)

    for command in COMMANDS:
        run_command(command)

    print("\n" + "=" * 70)
    print("COMPLETE PIPELINE FINISHED SUCCESSFULLY")
    print("=" * 70)

    print("\nGenerated results:")

    results_dir = PROJECT_ROOT / "results"

    expected_files = [
        "schedule.json",
        "schedule.csv",
        "statistics.json",
        "conflict_graph.json",
        "final_report.txt",
        "network_topology.png",
        "conflict_graph.png",
        "tdma_schedule.png",
        "spatial_reuse.png",
    ]

    for filename in expected_files:
        file_path = results_dir / filename

        if file_path.exists():
            print(f"  [OK] {filename}")
        else:
            print(f"  [MISSING] {filename}")

    print("\nProject pipeline completed.")


if __name__ == "__main__":
    main()
    