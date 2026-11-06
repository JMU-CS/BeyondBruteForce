#!/usr/bin/env python3
"""Offline tests for SNAP source edge counts and installed simple graph caching."""
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import install_external_benchmarks as installer


class SnapNormalizationTests(unittest.TestCase):
    def test_distinct_edges_count_self_loops_once(self):
        raw = [(0, 1), (1, 0), (0, 1), (2, 3), (0, 0), (0, 0), (1, 1)]
        n, edges = installer._normalize_undirected_edges(raw, expected_n=4)
        self.assertEqual((n, len(edges)), (4, 2))
        self.assertEqual(
            installer._source_undirected_edge_count(raw, normalized_m=len(edges)),
            (4, 2),
        )

    def test_as_20000102_published_and_normalized_counts(self):
        # SNAP publishes 13,895 source edges for this AS snapshot, but
        # the simple graph has only 12,572 distinct non-loop edges.
        raw = [(0, i) for i in range(1, 6474)]
        raw += [(1, i) for i in range(2, 6101)]
        raw += [(i, i) for i in range(1323)]
        _, normalized = installer._normalize_undirected_edges(raw, expected_n=6474)
        self.assertEqual(len(normalized), 12572)
        self.assertEqual(
            installer._source_undirected_edge_count(raw, normalized_m=len(normalized)),
            (13895, 1323),
        )

    def _fixture(self, base, source_m, expected_m=2):
        path = base / "benchmarks/longest_path/manifest.json"
        path.parent.mkdir(parents=True)
        row = {
            "id": "snap_tiny", "file": "external/snap/instances/tiny.txt",
            "n": 4, "m": expected_m, "source_m": source_m,
            "download": {"url": "https://example.invalid/test.gz", "compression": "gzip"},
        }
        path.write_text(json.dumps({"suites": {"challenge_open": [row]}}))
        return path.parent / row["file"]

    def test_installs_valid_high_loop_fraction_and_reuses_cache(self):
        # A legitimate 50% normalization reduction must be allowed when the
        # original source edges (including self-loops) match source_m exactly.
        payload = gzip.compress(b"0 1\n1 0\n2 3\n0 0\n1 1\n")
        with TemporaryDirectory() as d:
            root = Path(d)
            output = self._fixture(root, source_m=4)
            with patch.object(installer, "ROOT", root), patch.object(
                installer, "download", return_value=payload
            ) as download:
                self.assertEqual(installer.install_longest_path_snap(), 1)
                self.assertEqual(output.read_text().splitlines()[0], "4 2")
                self.assertEqual(installer.install_longest_path_snap(), 1)
                download.assert_called_once()
                self.assertTrue(installer._installed_course_graph_matches(output, n=4, m=2))
                self.assertFalse(installer._installed_course_graph_matches(output, n=4, m=3))
                output.write_text("4 2\n0 1\n")
                self.assertFalse(installer._installed_course_graph_matches(output, n=4, m=2))

    def test_rejects_incorrect_published_source_count(self):
        payload = gzip.compress(b"0 1\n2 3\n0 0\n1 1\n")
        with TemporaryDirectory() as d:
            root = Path(d)
            output = self._fixture(root, source_m=99)
            with patch.object(installer, "ROOT", root), patch.object(
                installer, "download", return_value=payload
            ):
                with self.assertRaisesRegex(RuntimeError, "source_m=99"):
                    installer.install_longest_path_snap()
                self.assertFalse(output.exists())

    def test_rejects_incorrect_normalized_count(self):
        payload = gzip.compress(b"0 1\n2 3\n0 0\n1 1\n")
        with TemporaryDirectory() as d:
            root = Path(d)
            output = self._fixture(root, source_m=4, expected_m=3)
            with patch.object(installer, "ROOT", root), patch.object(
                installer, "download", return_value=payload
            ):
                with self.assertRaisesRegex(RuntimeError, "manifest m=3"):
                    installer.install_longest_path_snap()
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
