#!/usr/bin/env python3
import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATE = ROOT / "checks" / "validate.py"


def load_validate():
    spec = importlib.util.spec_from_file_location("validate", VALIDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


GUIDELINE = """
# Topic

## Rule

Use the rule.

## Why

Because it matters.

## Do

- Do this.

## Avoid

- Avoid that.

## Example

```sql
SELECT 1;
```

## Exceptions

- None.
"""


WORKFLOW = """
# Workflow

## Guideline Routing

Load [topic](../guidelines/topic.md).

## Workflow

1. Do the work.

## Avoid

- Avoid shortcuts.
"""


SKILL = """
---
name: example
---

# Skill

## Routing

| Task | Load |
| --- | --- |
| Topic | [Topic](guidelines/topic.md) |
| Workflow | [Workflow](workflows/workflow.md) |

## Core Behavior

- Use the guide.
"""


class ValidateTests(unittest.TestCase):
    def test_valid_skill_tree_passes(self):
        validate = load_validate()

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write(root / "SKILL.md", SKILL)
            write(root / "guidelines.md", "[Topic](guidelines/topic.md)")
            write(root / "guidelines" / "topic.md", GUIDELINE)
            write(root / "workflows" / "workflow.md", WORKFLOW)

            result = validate.validate(root)

        self.assertEqual([], result.errors)

    def test_reports_broken_links_and_missing_index_entries(self):
        validate = load_validate()

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write(root / "SKILL.md", "[Missing](guidelines/missing.md)")
            write(root / "guidelines.md", "")
            write(root / "guidelines" / "topic.md", GUIDELINE)
            write(root / "workflows" / "workflow.md", WORKFLOW)

            result = validate.validate(root)

        self.assertTrue(any("broken link" in error for error in result.errors))
        self.assertTrue(any("guidelines.md does not list guidelines/topic.md" in error for error in result.errors))
        self.assertTrue(any("SKILL.md does not link workflows/workflow.md" in error for error in result.errors))

    def test_sql_blocks_are_extracted_and_empty_blocks_fail(self):
        validate = load_validate()

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write(root / "SKILL.md", SKILL)
            write(root / "guidelines.md", "[Topic](guidelines/topic.md)")
            write(root / "guidelines" / "topic.md", GUIDELINE.replace("SELECT 1;", ""))
            write(root / "workflows" / "workflow.md", WORKFLOW)

            result = validate.validate(root)

        self.assertEqual(1, result.sql_block_count)
        self.assertTrue(any("empty sql block" in error for error in result.errors))

    def test_conditional_page_requires_activation(self):
        validate = load_validate()

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write(root / "SKILL.md", SKILL)
            write(root / "guidelines.md", "[Advanced](guidelines/advanced-indexes.md)")
            write(root / "guidelines" / "advanced-indexes.md", GUIDELINE)
            write(root / "workflows" / "workflow.md", WORKFLOW)

            result = validate.validate(root)

        self.assertTrue(any("missing ## Activation" in error for error in result.errors))

    def test_rejects_duplicate_routing_and_workflows_in_index(self):
        validate = load_validate()

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write(
                root / "SKILL.md",
                SKILL.replace(
                    "| Workflow | [Workflow](workflows/workflow.md) |",
                    "| Workflow | [Workflow](workflows/workflow.md), [again](workflows/workflow.md) |",
                ),
            )
            write(
                root / "guidelines.md",
                "[Topic](guidelines/topic.md)\n[Again](guidelines/topic.md)\n"
                "[Workflow](workflows/workflow.md)",
            )
            write(root / "guidelines" / "topic.md", GUIDELINE)
            write(root / "workflows" / "workflow.md", WORKFLOW)

            result = validate.validate(root)

        self.assertTrue(any("guidelines.md lists guidelines/topic.md more than once" in error for error in result.errors))
        self.assertTrue(any("guidelines.md must not link workflow" in error for error in result.errors))
        self.assertTrue(any("SKILL.md links workflows/workflow.md more than once" in error for error in result.errors))

    def test_rejects_oversized_guideline_but_allows_long_workflow(self):
        validate = load_validate()
        oversized = GUIDELINE + "\n" + "\n".join(
            f"Additional guideline line {index}." for index in range(101)
        )
        long_workflow = WORKFLOW + "\n" + "\n".join(
            f"Additional workflow line {index}." for index in range(150)
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            write(root / "SKILL.md", SKILL)
            write(root / "guidelines.md", "[Topic](guidelines/topic.md)")
            write(root / "guidelines" / "topic.md", oversized)
            write(root / "workflows" / "workflow.md", long_workflow)

            result = validate.validate(root)

        size_errors = [error for error in result.errors if "line limit" in error]
        self.assertEqual(1, len(size_errors))
        self.assertIn("guidelines/topic.md", size_errors[0])


if __name__ == "__main__":
    unittest.main()
