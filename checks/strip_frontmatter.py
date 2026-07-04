#!/usr/bin/env python3
"""mdBook preprocessor that strips YAML frontmatter from chapter content.

The packaged skill requires frontmatter on SKILL.md, but mdBook would render
it as literal text; this removes it from the book only.
"""

import json
import sys


def strip_frontmatter(text):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "".join(lines[index + 1 :]).lstrip("\n")
    return text


def process(item):
    chapter = item.get("Chapter")
    if not chapter:
        return
    chapter["content"] = strip_frontmatter(chapter["content"])
    for sub_item in chapter.get("sub_items", []):
        process(sub_item)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "supports":
        sys.exit(0)

    context, book = json.load(sys.stdin)
    for item in book["items"]:
        process(item)
    json.dump(book, sys.stdout)


if __name__ == "__main__":
    main()
