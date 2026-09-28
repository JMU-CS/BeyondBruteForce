#!/usr/bin/env python3
"""Shared validation helpers for Beyond Brute Force Checkpoint 1."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_FIELDS = {
    "team_name",
    "team_members",
    "project_preferences",
    "assigned_problem",
}

REQUIRED_DIRECTORIES = {
    "src/course",
    "src/student",
    "tests/public",
    "tests/student",
    "benchmarks",
    "experiments",
    "reports",
    "presentation",
    "tools",
}


def load_valid_projects(path: Path) -> dict[str, str]:
    """Load {identifier: display_name} from the canonical project catalog."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Missing valid-project catalog: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path}: line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(data, dict) or not data:
        raise ValueError(f"{path} must contain a non-empty JSON object.")

    for project_id, display_name in data.items():
        if not isinstance(project_id, str) or not project_id.strip():
            raise ValueError(f"Every project identifier in {path} must be a non-empty string.")
        if not isinstance(display_name, str) or not display_name.strip():
            raise ValueError(f"Every project display name in {path} must be a non-empty string.")

    return data


def load_project(path: Path) -> tuple[dict | None, list[str]]:
    if not path.is_file():
        return None, [f"Missing required file: {path.name}"]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [
            f"{path.name} is not valid JSON: line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ]
    except OSError as exc:
        return None, [f"Could not read {path.name}: {exc}"]

    if not isinstance(data, dict):
        return None, [f"{path.name} must contain one JSON object at the top level."]

    return data, []


def validate_project_data(
    data: dict,
    valid_projects: set[str],
    *,
    require_unassigned: bool = False,
) -> dict[str, list[str]]:
    """Return validation messages grouped by Gradescope category."""
    result: dict[str, list[str]] = {
        "required_fields": [],
        "team": [],
        "preferences_shape": [],
        "preferences_values": [],
        "assigned_problem": [],
    }

    missing = sorted(REQUIRED_FIELDS - set(data.keys()))
    if missing:
        result["required_fields"].append(
            "Missing required field(s): " + ", ".join(missing)
        )

    team_name = data.get("team_name")
    if not isinstance(team_name, str) or not team_name.strip():
        result["team"].append("team_name must be a non-empty string.")

    members = data.get("team_members")
    if not isinstance(members, list):
        result["team"].append("team_members must be a JSON list.")
    else:
        if len(members) not in (2, 3):
            result["team"].append("team_members must contain exactly 2 or 3 students.")

        seen_github: set[str] = set()
        for i, member in enumerate(members, start=1):
            if not isinstance(member, dict):
                result["team"].append(f"Team member {i} must be a JSON object.")
                continue

            name = member.get("name")
            github = member.get("github")

            if not isinstance(name, str) or not name.strip():
                result["team"].append(f"Team member {i} needs a non-empty name.")

            if not isinstance(github, str) or not github.strip():
                result["team"].append(
                    f"Team member {i} needs a non-empty GitHub username."
                )
            else:
                normalized = github.strip().lower()
                if normalized in seen_github:
                    result["team"].append(
                        f"GitHub username '{github.strip()}' appears more than once."
                    )
                seen_github.add(normalized)

    preferences = data.get("project_preferences")
    if not isinstance(preferences, list):
        result["preferences_shape"].append(
            "project_preferences must be a JSON list."
        )
    else:
        if len(preferences) != 3:
            result["preferences_shape"].append(
                "project_preferences must contain exactly three project identifiers."
            )

        normalized: list[object] = []
        for pref in preferences:
            normalized.append(pref.strip() if isinstance(pref, str) else pref)

        string_prefs = [p for p in normalized if isinstance(p, str) and p]
        if len(string_prefs) != len(preferences):
            result["preferences_shape"].append(
                "Every project preference must be a non-empty string."
            )

        if len(set(string_prefs)) != len(string_prefs):
            result["preferences_shape"].append(
                "The three project preferences must be different."
            )

        bad = sorted({p for p in string_prefs if p not in valid_projects})
        if bad:
            result["preferences_values"].append(
                "Unknown project identifier(s): " + ", ".join(bad)
            )

    assigned = data.get("assigned_problem")
    if not isinstance(assigned, str):
        result["assigned_problem"].append("assigned_problem must be a string.")
    else:
        assigned = assigned.strip()
        if require_unassigned and assigned:
            result["assigned_problem"].append(
                "assigned_problem must be empty for Checkpoint 1."
            )
        elif assigned and assigned not in valid_projects:
            result["assigned_problem"].append(
                f"Unknown assigned_problem identifier: {assigned}"
            )

    return result


def validate_repository_structure(repo_root: Path) -> list[str]:
    errors = []
    for directory in sorted(REQUIRED_DIRECTORIES):
        if not (repo_root / directory).is_dir():
            errors.append(f"Missing required directory: {directory}/")
    return errors


def flatten_messages(grouped: dict[str, list[str]]) -> list[str]:
    messages: list[str] = []
    for values in grouped.values():
        messages.extend(values)
    return messages
