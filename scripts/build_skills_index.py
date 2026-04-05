#!/usr/bin/env python3
"""Scan skill directories and generate skills.json index."""

import json
from pathlib import Path


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter (name, description) from markdown."""
    meta: dict = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip()
            body = parts[2]
    return meta, body


def first_heading(text: str) -> str:
    """Return the first # heading from markdown, or empty string."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return ""


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    skills = []

    for skill_dir in sorted(repo.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        meta, _ = parse_frontmatter(skill_md.read_text())
        name = meta.get("name", skill_dir.name)
        description = meta.get("description", "")

        refs = []
        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            for ref_file in sorted(refs_dir.glob("*.md")):
                ref_text = ref_file.read_text()
                title = first_heading(ref_text)
                if not title:
                    # Prettify filename as fallback
                    title = ref_file.stem.replace("-", " ").replace("_", " ").title()
                refs.append({
                    "title": title,
                    "file": f"references/{ref_file.name}",
                })

        skills.append({
            "name": name,
            "folder": skill_dir.name,
            "description": description,
            "references": refs,
        })

    out = repo / "skills.json"
    out.write_text(json.dumps(skills, indent=2) + "\n")
    print(f"Wrote {out} with {len(skills)} skill(s)")


if __name__ == "__main__":
    main()
