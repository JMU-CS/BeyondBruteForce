#!/usr/bin/env python3
"""Regression tests for the shared Beyond Brute Force project.json schema.

Run from the repository root::

    python tools/test_project_validation.py
"""
from __future__ import annotations

import copy
import unittest

from project_validation import flatten_messages, validate_project_data

VALID = {
    "minimum_vertex_cover", "minimum_graph_coloring",
    "traveling_salesperson", "maximum_clique", "longest_path",
}


def project(count=1, assigned="minimum_vertex_cover"):
    return {
        "team_name": "A Team",
        "team_members": [{"name": f"Student {i}"} for i in range(1, count + 1)],
        "project_preferences": ["minimum_vertex_cover", "maximum_clique", "longest_path"],
        "assigned_problem": assigned,
    }


def messages(data, **kwargs):
    return flatten_messages(validate_project_data(data, VALID, **kwargs))


class SchemaTests(unittest.TestCase):
    def test_one_two_three_person_teams(self):
        for size in (1, 2, 3):
            with self.subTest(size=size):
                self.assertEqual(messages(project(size), require_assigned=True), [])

    def test_out_of_range_team_sizes(self):
        for size in (0, 4):
            with self.subTest(size=size):
                self.assertTrue(any("1, 2, or 3" in m for m in messages(project(size))))

    def test_member_must_be_name_only(self):
        data = project()
        data["team_members"][0]["github"] = "aGithubAccount"
        self.assertTrue(any("unsupported" in m for m in messages(data)))
        del data["team_members"][0]["github"]
        self.assertEqual(messages(data), [])

    def test_duplicate_names_ignore_case_and_spacing(self):
        data = project(2)
        data["team_members"][0]["name"] = "Ada   Lovelace"
        data["team_members"][1]["name"] = " ada lovelace "
        self.assertTrue(any("appears more than once" in m for m in messages(data)))

    def test_empty_and_non_dict_members(self):
        data = project()
        data["team_members"] = [{"name": " "}, 3]
        errs = messages(data)
        self.assertTrue(any("non-empty name" in m for m in errs))
        self.assertTrue(any("JSON object" in m for m in errs))

    def test_preference_constraints(self):
        for prefs in (["minimum_vertex_cover"],
                      ["minimum_vertex_cover"] * 3,
                      ["minimum_vertex_cover", "longest_path", "fake_problem"],
                      ["minimum_vertex_cover", "longest_path", ""]):
            with self.subTest(prefs=prefs):
                data = project()
                data["project_preferences"] = prefs
                self.assertTrue(messages(data))

    def test_top_level_required_and_unexpected_fields(self):
        data = project()
        del data["team_name"]
        data["unplanned"] = 1
        errors = messages(data)
        self.assertTrue(any("Missing required" in m for m in errors))
        self.assertTrue(any("Unsupported top-level" in m for m in errors))

    def test_selection_assigned_and_either_phases(self):
        unassigned = project(assigned="")
        assigned = project(assigned="maximum_clique")
        self.assertEqual(messages(unassigned, require_unassigned=True), [])
        self.assertEqual(messages(assigned, require_assigned=True), [])
        self.assertEqual(messages(unassigned), [])
        self.assertEqual(messages(assigned), [])
        self.assertTrue(any("must be empty" in m for m in messages(assigned, require_unassigned=True)))
        self.assertTrue(any("must be a valid" in m for m in messages(unassigned, require_assigned=True)))

    def test_bad_assignment_and_not_among_preferences(self):
        self.assertTrue(messages(project(assigned="not_a_problem")))
        # The instructor is permitted to assign any canonical problem.
        self.assertEqual(messages(project(assigned="minimum_graph_coloring"), require_assigned=True), [])

    def test_conflicting_phase_flags(self):
        with self.assertRaises(ValueError):
            validate_project_data(project(), VALID, require_unassigned=True, require_assigned=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
