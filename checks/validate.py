#!/usr/bin/env python3
"""Validate the packaged PostgreSQL style guide skill.

Checks:
- local Markdown links resolve within the packaged skill files
- guidelines.md lists every guideline exactly once and no workflows
- SKILL.md lists every workflow exactly once
- guideline, conditional-page, workflow, and router sections are present
- guideline pages do not exceed the size budget
- SQL code fences are closed and non-empty
"""

import argparse
import pathlib
import re
import sys


GUIDELINE_SECTIONS = ("## Rule",)

CONDITIONAL_GUIDELINES = {
    "advanced-indexes.md",
    "functions-and-procedures.md",
    "roles-privileges-and-row-level-security.md",
    "triggers.md",
    "views-and-materialized-views.md",
}

WORKFLOW_SECTIONS = (
    "## Guideline Routing",
    "## Workflow",
)

MAX_GUIDELINE_LINES = 100

ROUTER_SECTIONS = {
    "SKILL.md": ("## Routing", "## Core Behavior"),
}

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^```([A-Za-z0-9_+.,-]*)\s*$")


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.checked_files = 0
        self.sql_block_count = 0


def validate(root):
    root = pathlib.Path(root)
    result = ValidationResult()

    skill_files = packaged_markdown_files(root)
    result.checked_files = len(skill_files)

    for path in skill_files:
        text = read(path)
        validate_links(root, path, text, result)
        validate_code_fences(path, text, result)

    validate_guidelines(root, result)
    validate_workflows(root, result)
    validate_routers(root, result)

    return result


def packaged_markdown_files(root):
    files = [
        root / "SKILL.md",
        root / "guidelines.md",
    ]
    files.extend(sorted((root / "guidelines").glob("*.md")))
    files.extend(sorted((root / "workflows").glob("*.md")))
    return [path for path in files if path.exists()]


def read(path):
    return path.read_text(encoding="utf-8-sig")


def validate_links(root, path, text, result):
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip().split()[0].strip("<>")
        if should_skip_link(target):
            continue

        target_path = target.split("#", 1)[0]
        if not target_path:
            continue

        resolved = (path.parent / target_path).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            result.errors.append(f"{relative(root, path)}: link escapes repo -> {target}")
            continue

        if not resolved.exists():
            result.errors.append(f"{relative(root, path)}: broken link -> {target}")


def should_skip_link(target):
    return (
        target.startswith("#")
        or target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
    )


def validate_code_fences(path, text, result):
    open_lang = None
    open_line = None
    body = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        fence = FENCE_RE.match(line.strip())
        if fence and open_lang is None:
            open_lang = fence.group(1)
            open_line = line_number
            body = []
            continue

        if line.strip() == "```" and open_lang is not None:
            if open_lang.startswith("sql"):
                result.sql_block_count += 1
                if not "\n".join(body).strip():
                    result.errors.append(f"{path}: empty sql block starting on line {open_line}")
            open_lang = None
            open_line = None
            body = []
            continue

        if open_lang is not None:
            body.append(line)

    if open_lang is not None:
        result.errors.append(f"{path}: unclosed code fence starting on line {open_line}")


def validate_guidelines(root, result):
    index = read(root / "guidelines.md") if (root / "guidelines.md").exists() else ""
    guideline_files = sorted((root / "guidelines").glob("*.md"))

    for path in guideline_files:
        rel = relative(root, path)
        text = read(path)
        validate_required_sections(root, path, text, GUIDELINE_SECTIONS, result)
        if path.name in CONDITIONAL_GUIDELINES:
            validate_required_sections(root, path, text, ("## Activation",), result)
        line_count = len(text.splitlines())
        if line_count > MAX_GUIDELINE_LINES:
            result.errors.append(
                f"{rel}: {line_count} lines exceeds {MAX_GUIDELINE_LINES}-line limit"
            )
        link_count = len(re.findall(rf"\]\({re.escape(rel)}(?:#[^)]+)?\)", index))
        if link_count == 0:
            result.errors.append(f"guidelines.md does not list {rel}")
        elif link_count > 1:
            result.errors.append(f"guidelines.md lists {rel} more than once")

    linked = set(re.findall(r"\]\((guidelines/[^)#]+\.md)(?:#[^)]+)?\)", index))
    existing = {relative(root, path) for path in guideline_files}
    for rel in sorted(linked - existing):
        result.errors.append(f"guidelines.md lists missing guideline {rel}")

    workflow_links = sorted(set(re.findall(r"\]\((workflows/[^)#]+\.md)(?:#[^)]+)?\)", index)))
    for rel in workflow_links:
        result.errors.append(f"guidelines.md must not link workflow {rel}")


def validate_workflows(root, result):
    workflow_files = sorted((root / "workflows").glob("*.md"))
    skill_text = read(root / "SKILL.md") if (root / "SKILL.md").exists() else ""

    for path in workflow_files:
        rel = relative(root, path)
        text = read(path)
        validate_required_sections(root, path, text, WORKFLOW_SECTIONS, result)
        link_count = len(re.findall(rf"\]\({re.escape(rel)}(?:#[^)]+)?\)", skill_text))
        if link_count == 0:
            result.errors.append(f"SKILL.md does not link {rel}")
        elif link_count > 1:
            result.errors.append(f"SKILL.md links {rel} more than once")


def validate_routers(root, result):
    for name, sections in ROUTER_SECTIONS.items():
        path = root / name
        if not path.exists():
            result.errors.append(f"{name} is missing")
            continue
        validate_required_sections(root, path, read(path), sections, result)


def validate_required_sections(root, path, text, sections, result):
    if not has_top_level_heading(text):
        result.errors.append(f"{relative(root, path)}: missing top-level heading")
    for section in sections:
        if section not in text:
            result.errors.append(f"{relative(root, path)}: missing {section}")


def has_top_level_heading(text):
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                lines = lines[index + 1 :]
                break

    return any(line.startswith("# ") for line in lines)


def relative(root, path):
    return path.resolve().relative_to(root.resolve()).as_posix()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default=pathlib.Path(__file__).resolve().parents[1],
        type=pathlib.Path,
        help="repository root to validate",
    )
    args = parser.parse_args(argv)

    result = validate(args.root)

    if result.errors:
        print(f"VALIDATION FAILED ({len(result.errors)} problem(s)):\n")
        for error in result.errors:
            print(f"  - {error}")
        return 1

    print(
        "OK: "
        f"{result.checked_files} markdown files valid; "
        f"{result.sql_block_count} sql code block(s) checked."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
