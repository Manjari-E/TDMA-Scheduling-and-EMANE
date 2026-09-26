import json
import os
import tempfile
import unittest

from src.input_parser import load_nodes
from src.report import build_report
from src.result_export import export_results
from src.scheduler import build_schedule

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "input", "nodes.json")


class TestResultExport(unittest.TestCase):
    def test_exports_complete_result_package(self):
        result = build_schedule(load_nodes(SAMPLE), 500.0)
        report = build_report(result)

        with tempfile.TemporaryDirectory() as tmp:
            output = export_results(result, report, tmp)
            expected = {
                "schedule.json",
                "schedule.csv",
                "statistics.json",
                "conflict_graph.json",
                "final_report.txt",
            }
            self.assertEqual({p.name for p in output.iterdir()}, expected)

            schedule = json.loads((output / "schedule.json").read_text())
            self.assertEqual(schedule["node_count"], 16)
            self.assertEqual(schedule["slot_count"], 5)
            self.assertEqual(len(schedule["node_to_slot"]), 16)
            self.assertEqual(schedule["validation_status"], "VALID")

            stats = json.loads((output / "statistics.json").read_text())
            self.assertEqual(stats["communication_graph"]["edges"], 23)
            self.assertEqual(stats["conflict_graph"]["total_conflict_edges"], 55)
            self.assertEqual(stats["optimization"]["slots_used"], 5)
            self.assertTrue(stats["optimization"]["proven_optimal_for_instance"])
            self.assertEqual(stats["validation"]["violations"], 0)

            conflicts = json.loads((output / "conflict_graph.json").read_text())
            self.assertEqual(len(conflicts["nodes"]), 16)
            self.assertEqual(len(conflicts["edges"]), 55)

            self.assertIn("TDMA SCHEDULE VALIDATION", (output / "final_report.txt").read_text())


if __name__ == "__main__":
    unittest.main()
