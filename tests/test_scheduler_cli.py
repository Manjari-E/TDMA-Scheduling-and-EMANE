import contextlib
import io
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET

import main as cli
from src.emane_bridge import build_emane_schedule_xml
from src.input_parser import load_nodes
from src.scheduler import build_schedule

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "input", "nodes.json")


class TestScheduleOutputs(unittest.TestCase):
    def setUp(self):
        self.result = build_schedule(load_nodes(SAMPLE), 500.0)

    def test_schedule_valid_and_complete(self):
        self.assertTrue(self.result.validation.is_valid)
        self.assertEqual(len(self.result.node_to_slot), 16)

    def test_matrix_each_node_in_exactly_one_slot(self):
        m = self.result.matrix
        for col in range(16):
            self.assertEqual(sum(row[col] for row in m), 1)

    def test_matrix_rows_match_slot_groups(self):
        for slot, members in self.result.slot_to_nodes.items():
            row = self.result.matrix[slot]
            self.assertEqual([n for n, v in zip(self.result.node_order, row) if v], sorted(members))


class TestCli(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_success(self):
        code, out, _ = self.run_cli("--input", SAMPLE)
        self.assertEqual(code, 0)
        self.assertIn("Status             : VALID", out)

    def test_missing_file_is_clean_error(self):
        code, _, err = self.run_cli("--input", "nope.json")
        self.assertEqual(code, 2)
        self.assertIn("Input error", err)
        self.assertNotIn("Traceback", err)

    def test_wrong_count_needs_dev_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "five.json")
            with open(path, "w") as fh:
                fh.write('{"A":[0,0],"B":[400,0],"C":[800,0]}')
            self.assertEqual(self.run_cli("--input", path)[0], 2)
            self.assertEqual(self.run_cli("--input", path, "--dev-mode")[0], 0)

    def test_bad_range(self):
        self.assertEqual(self.run_cli("--input", SAMPLE, "--range", "-5")[0], 2)

    def test_output_file_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.txt")
            self.assertEqual(self.run_cli("--input", SAMPLE, "--output", path)[0], 0)
            with open(path) as fh:
                self.assertIn("TDMA SCHEDULE VALIDATION", fh.read())


class TestEmaneBridge(unittest.TestCase):
    """Checks only that the generated XML is well-formed and self-consistent.
    It does NOT prove EMANE accepts it."""

    def test_xml_well_formed_and_matches_schedule(self):
        res = build_schedule(load_nodes(SAMPLE), 500.0)
        root = ET.fromstring(build_emane_schedule_xml(res.node_to_slot))
        self.assertEqual(root.tag, "emane-tdma-schedule")
        structure = root.find("structure")
        self.assertEqual(int(structure.get("slots")), res.optimization.slots)
        listed = []
        for slot in root.iter("slot"):
            listed += [int(x) for x in slot.get("nodes").split(",")]
        self.assertEqual(sorted(listed), list(range(1, 17)))     # every NEM transmits once


if __name__ == "__main__":
    unittest.main()
