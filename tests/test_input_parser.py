import json
import os
import tempfile
import unittest

from src.input_parser import InputError, load_nodes, parse_nodes


def sixteen():
    return json.dumps({f"Node_{i:02d}": [i * 10.0, 0.0] for i in range(1, 17)})


class TestInput(unittest.TestCase):
    def test5_invalid_json(self):
        with self.assertRaises(InputError) as ctx:
            parse_nodes('{"A": [0, 0],', strict_count=False)
        self.assertIn("Invalid JSON", str(ctx.exception))

    def test6_invalid_coordinates(self):
        bad = ['{"A": ["x", 1]}', '{"A": [1]}', '{"A": [1, 2, 3]}', '{"A": null}',
               '{"A": "0,0"}', '{"A": [true, 1]}', '{"A": [1, null]}']
        for text in bad:
            with self.subTest(text=text):
                with self.assertRaises(InputError) as ctx:
                    parse_nodes(text, strict_count=False)
                self.assertIn("Node 'A'", str(ctx.exception))

    def test_non_finite_coordinates_rejected(self):
        with self.assertRaises(InputError):
            parse_nodes('{"A": [NaN, 1]}', strict_count=False)

    def test_duplicate_names_rejected(self):
        with self.assertRaises(InputError) as ctx:
            parse_nodes('{"A": [0, 0], "A": [1, 1]}', strict_count=False)
        self.assertIn("Duplicate", str(ctx.exception))

    def test_blank_name_and_wrong_top_level(self):
        for text in ('{"  ": [0, 0]}', '[1, 2]', '{}'):
            with self.assertRaises(InputError):
                parse_nodes(text, strict_count=False)

    def test_exactly_sixteen_required_in_assignment_mode(self):
        self.assertEqual(len(parse_nodes(sixteen())), 16)
        with self.assertRaises(InputError) as ctx:
            parse_nodes('{"A": [0, 0], "B": [1, 1]}')
        self.assertIn("16", str(ctx.exception))

    def test_dev_mode_allows_other_counts(self):
        self.assertEqual(len(parse_nodes('{"A": [0, 0], "B": [1, 1]}', strict_count=False)), 2)

    def test_integers_accepted_and_converted(self):
        self.assertEqual(parse_nodes('{"A": [1, 2]}', strict_count=False)["A"], (1.0, 2.0))

    def test_missing_file(self):
        with self.assertRaises(InputError):
            load_nodes("/no/such/file.json")

    def test_shipped_input_files_load(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for name in ("nodes.json", "nodes_dense.json"):
            self.assertEqual(len(load_nodes(os.path.join(root, "input", name))), 16)


if __name__ == "__main__":
    unittest.main()
