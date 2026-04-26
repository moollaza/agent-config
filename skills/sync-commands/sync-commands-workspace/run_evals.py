#!/usr/bin/env python3
"""
Eval script for sync-commands skill.
Tests that transform.py correctly scrubs HumanLayer-specific content
and applies local conventions.
"""

import json
import re
import sys
import os

# Add the skill directory to path so we can import transform functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# Import transform functions from the skill's bundled script
SKILL_DIR = Path(__file__).parent.parent
TRANSFORM_SCRIPT = SKILL_DIR / 'transform.py'

# We need to exec the transform script to get its functions
transform_globals = {}
script_text = TRANSFORM_SCRIPT.read_text()
func_boundary = script_text.find('def fetch_remote_files')
exec(script_text[:func_boundary], transform_globals)
transform_content = transform_globals['transform_content']

GITHUB_API = 'https://api.github.com/repos/humanlayer/humanlayer/contents/.claude/commands?ref=main'
GITHUB_RAW = 'https://raw.githubusercontent.com/humanlayer/humanlayer/main/.claude/commands/'

# Also get the mapping and exclusion sets
exec_globals = {}
mapping_boundary = script_text.find('def remove_yaml_frontmatter')
exec(script_text[:mapping_boundary], exec_globals)
COMMAND_MAPPING = exec_globals['COMMAND_MAPPING']
EXCLUDED_COMMANDS = exec_globals['EXCLUDED_COMMANDS']


def fetch_file_list():
    req = Request(GITHUB_API)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    with urlopen(req) as resp:
        files = json.loads(resp.read())
    return [f['name'] for f in files if f['type'] == 'file' and f['name'].endswith('.md')]


def fetch_file(name):
    with urlopen(GITHUB_RAW + name) as resp:
        return resp.read().decode('utf-8')


def run_eval_1_forbidden_patterns(transformed_files):
    """Check that no HumanLayer-specific content remains."""
    results = []

    forbidden = [
        ("thoughts/", r'thoughts/'),
        ("standalone 'thoughts'", r'\bthoughts\b'),
        ("humanlayer thoughts sync", r'humanlayer thoughts sync'),
        ("hack/spec", r'hack/spec'),
        ("scripts/spec_metadata", r'scripts/spec_metadata'),
        ("thoughts/searchable/", r'thoughts/searchable/'),
        # Only match YAML frontmatter at the very start of the file (line 1)
        # Not --- used as markdown section separators or inside template examples
        ("YAML frontmatter at file start", r'\A---\s*\n'),
    ]

    for desc, pattern in forbidden:
        found_in = []
        for filename, content in transformed_files.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                found_in.append(f"{filename} ({len(matches)} matches)")

        passed = len(found_in) == 0
        evidence = "No matches found" if passed else f"Found in: {', '.join(found_in)}"
        results.append({
            "text": f"No '{desc}' references in transformed files",
            "passed": passed,
            "evidence": evidence
        })

    return results


def run_eval_2_conventions(transformed_files):
    """Check that local conventions are applied."""
    results = []

    # Check required patterns exist somewhere
    all_content = '\n'.join(transformed_files.values())

    if 'agent-docs/' in all_content:
        results.append({
            "text": "Uses 'agent-docs/' directory references",
            "passed": True,
            "evidence": "Found agent-docs/ references in transformed output"
        })
    else:
        results.append({
            "text": "Uses 'agent-docs/' directory references",
            "passed": False,
            "evidence": "No agent-docs/ references found"
        })

    # Check forbidden command name patterns
    forbidden_commands = [
        ("/resume_handoff", "/resume-handoff"),
        ("/validate_plan", "/validate-plan"),
        ("/create_plan", "/plan"),
        ("/implement_plan", "/implement"),
        ("/research_codebase", "/research"),
        ("/create_handoff", "/handoff"),
        ("/quick_fix", "/quick-fix"),
    ]

    for old, new in forbidden_commands:
        found_in = []
        for filename, content in transformed_files.items():
            if old in content:
                count = content.count(old)
                found_in.append(f"{filename} ({count}x)")

        passed = len(found_in) == 0
        evidence = (
            f"Correctly uses '{new}'"
            if passed
            else f"Still contains '{old}' in: {', '.join(found_in)}"
        )
        results.append({
            "text": f"Uses '{new}' not '{old}'",
            "passed": passed,
            "evidence": evidence
        })

    return results


def run_eval_3_coverage(remote_files):
    """Check that all upstream files are accounted for."""
    results = []

    mapped = set(COMMAND_MAPPING.keys())
    excluded = EXCLUDED_COMMANDS
    accounted = mapped | excluded

    unaccounted = [f for f in remote_files if f not in accounted]

    passed = len(unaccounted) == 0
    if passed:
        evidence = (
            f"All {len(remote_files)} upstream files are in "
            f"COMMAND_MAPPING ({len(mapped)}) or "
            f"EXCLUDED_COMMANDS ({len(excluded)})"
        )
    else:
        evidence = (
            f"Unaccounted files: {', '.join(unaccounted)}. "
            f"Add to COMMAND_MAPPING or EXCLUDED_COMMANDS in transform.py"
        )

    results.append({
        "text": "All upstream files accounted for",
        "passed": passed,
        "evidence": evidence
    })

    return results


def main():
    print("=" * 60)
    print("SYNC-COMMANDS SKILL EVAL")
    print("=" * 60)

    # Fetch all upstream files we sync
    print("\nFetching upstream files...")
    remote_files = fetch_file_list()
    print(f"Found {len(remote_files)} upstream files")

    # Transform each mapped file
    transformed = {}
    for remote_name, local_name in COMMAND_MAPPING.items():
        if remote_name in remote_files:
            print(f"  Fetching & transforming {remote_name} -> {local_name}")
            raw = fetch_file(remote_name)
            transformed[local_name] = transform_content(raw, remote_name)

    print(f"\nTransformed {len(transformed)} files")

    # Run evals
    all_results = {}

    print("\n" + "-" * 60)
    print("EVAL 1: Forbidden HumanLayer-specific patterns")
    print("-" * 60)
    eval1 = run_eval_1_forbidden_patterns(transformed)
    all_results['eval_1_forbidden_patterns'] = eval1
    for r in eval1:
        status = "PASS" if r['passed'] else "FAIL"
        print(f"  [{status}] {r['text']}")
        if not r['passed']:
            print(f"         {r['evidence']}")

    print("\n" + "-" * 60)
    print("EVAL 2: Local convention application")
    print("-" * 60)
    eval2 = run_eval_2_conventions(transformed)
    all_results['eval_2_conventions'] = eval2
    for r in eval2:
        status = "PASS" if r['passed'] else "FAIL"
        print(f"  [{status}] {r['text']}")
        if not r['passed']:
            print(f"         {r['evidence']}")

    print("\n" + "-" * 60)
    print("EVAL 3: Upstream file coverage")
    print("-" * 60)
    eval3 = run_eval_3_coverage(remote_files)
    all_results['eval_3_coverage'] = eval3
    for r in eval3:
        status = "PASS" if r['passed'] else "FAIL"
        print(f"  [{status}] {r['text']}")
        if not r['passed']:
            print(f"         {r['evidence']}")

    # Summary
    all_assertions = eval1 + eval2 + eval3
    passed = sum(1 for r in all_assertions if r['passed'])
    total = len(all_assertions)
    failed = total - passed

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    # Save results
    output_dir = Path(__file__).parent / 'iteration-1'
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / 'grading.json'
    results_path.write_text(json.dumps({
        "eval_results": all_results,
        "summary": {"passed": passed, "total": total, "failed": failed}
    }, indent=2))
    print(f"\nResults saved to {results_path}")

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
