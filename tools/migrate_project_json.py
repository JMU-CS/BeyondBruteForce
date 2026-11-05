#!/usr/bin/env python3
"""Migrate legacy team-member records to the name-only project schema.

Default is a no-write preview. Use --apply to remove obsolete `github` fields
while preserving names, preferences, and assigned_problem. A .bak is created
before the original file is replaced.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_validation import load_project, load_valid_projects, validate_project_data, flatten_messages

ROOT = Path(__file__).resolve().parents[1]


def migrate(data: dict) -> tuple[dict, int]:
    """Return a copy with legacy member.github fields removed; never alter other fields."""
    updated = dict(data)
    members = data.get('team_members')
    if not isinstance(members, list):
        raise ValueError('team_members must be a JSON list; refusing automatic migration.')
    converted = []
    removed = 0
    for i, member in enumerate(members, start=1):
        if not isinstance(member, dict):
            raise ValueError(f'Team member {i} is not an object; refusing automatic migration.')
        clone = dict(member)
        if 'github' in clone:
            clone.pop('github')
            removed += 1
        converted.append(clone)
    updated['team_members'] = converted
    return updated, removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='write the migrated JSON after saving a backup')
    args = parser.parse_args()
    project_path = ROOT / 'project.json'
    project, errors = load_project(project_path)
    if errors or project is None:
        for error in errors:
            print('ERROR:', error)
        return 2
    try:
        updated, count = migrate(project)
    except ValueError as exc:
        print('ERROR:', exc)
        return 2

    if count == 0:
        print('No legacy github fields found; project.json was not changed.')
    elif not args.apply:
        print(f'Preview: would remove github from {count} member record(s).')
        print('Use --apply to create project.json.bak and update project.json.')
    else:
        backup = ROOT / 'project.json.bak'
        if backup.exists():
            print('ERROR: project.json.bak already exists; preserve/remove it before retrying.')
            return 2
        backup.write_bytes(project_path.read_bytes())
        project_path.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'Migrated {count} legacy member record(s). Backup: project.json.bak')

    try:
        catalog = load_valid_projects(ROOT / 'tools' / 'valid_projects.json')
        problems = flatten_messages(validate_project_data(updated, set(catalog)))
        if problems:
            print('Remaining project.json validation issues:')
            for issue in problems:
                print('  -', issue)
        else:
            print('Migrated project data conforms to the name-only schema.')
    except ValueError as exc:
        print('WARNING: Could not validate migrated data:', exc)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
