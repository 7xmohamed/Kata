#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

# ANSI colors
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"


def fail(message: str) -> None:
    if sys.stderr.isatty():
        print(f"{COLOR_RED}{message}{COLOR_RESET}", file=sys.stderr)
    else:
        print(message, file=sys.stderr)
    sys.exit(1)


def parse_frontmatter(path: Path) -> dict:
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        fail(f"READ ERROR: Could not read {path}: {e}")

    lines = content.splitlines()
    if not lines or lines[0] != "---":
        fail(f"INVALID FRONTMATTER: {path} must start with ---")

    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"INVALID FRONTMATTER: {path} missing closing ---")

    frontmatter = lines[1:end]
    fields = {}
    in_metadata = False

    for line in frontmatter:
        if line.startswith("name:"):
            fields["name"] = line.split(":", 1)[1].strip()
            in_metadata = False
        elif line.startswith("description:"):
            raw_value = line.split(":", 1)[1].strip()
            if not raw_value.startswith('"') and ": " in raw_value:
                fail(
                    f"UNQUOTED DESCRIPTION WITH COLON: {path}\n"
                    f"  Description contains ': ' and must be wrapped in double quotes, "
                    f"otherwise YAML plain-scalar parsing truncates the field."
                )
            fields["description"] = raw_value.strip('"')
            in_metadata = False
        elif line.startswith("when_to_use:"):
            raw_value = line.split(":", 1)[1].strip()
            fields["when_to_use"] = raw_value.strip('"')
            in_metadata = False
        elif line == "metadata:":
            in_metadata = True
        elif in_metadata and line.startswith("  version:"):
            fields["version"] = line.split(":", 1)[1].strip().strip('"')
        elif line and not line.startswith(" "):
            in_metadata = False

    for field in ("name", "description", "version"):
        if not fields.get(field):
            fail(f"MISSING {field}: in {path}")

    return fields


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Kata skills structural integrity.")
    parser.add_argument("--fix", action="store_true", help="Auto-fix fixable issues (placeholder for compatibility).")
    parser.add_argument("--verbose", action="store_true", help="Print detailed validation logs.")
    args = parser.parse_args()

    # Locate the repository root
    script_dir = Path(__file__).resolve().parent
    root = (script_dir / "..").resolve()

    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if not skill_files:
        fail("NO SKILLS FOUND: expected skills/*/SKILL.md")

    skill_versions = {}
    skill_descriptions = {}

    for path in skill_files:
        skill_dir = path.parent.name
        fields = parse_frontmatter(path)
        if fields["name"] != skill_dir:
            fail(f"NAME MISMATCH: {path} frontmatter name={fields['name']} dir={skill_dir}")

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            fail(f"READ ERROR: Could not read {path}: {e}")

        if "⚔️" not in content:
            fail(
                f"MISSING KATA PREFIX INSTRUCTION: {path}\n"
                f"  Every SKILL.md must carry the ⚔️ first-line prefix directive "
                f"so the shared voice convention stays enforced."
            )
        skill_versions[skill_dir] = fields["version"]
        skill_descriptions[skill_dir] = fields["description"]

        if args.verbose or sys.stdout.isatty():
            print(f"{COLOR_GREEN}ok:{COLOR_RESET} {path.relative_to(root).as_posix()}")
        else:
            print(f"ok: {path.relative_to(root).as_posix()}")

    for market_dir in (".gemini-plugin", ".claude-plugin", ".codex-plugin"):
        market_path = root / market_dir / "marketplace.json"
        if not market_path.exists():
            fail(f"MISSING MARKETPLACE: expected {market_path}")

        try:
            with open(market_path, "r", encoding="utf-8") as f:
                marketplace = json.load(f)
        except Exception as e:
            fail(f"INVALID JSON: {market_path} is not valid JSON: {e}")

        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list):
            fail(f"INVALID MARKETPLACE: {market_path} plugins must be a list")

        market_versions = {}
        market_descriptions = {}
        for entry in plugins:
            if not isinstance(entry, dict):
                fail(f"INVALID MARKETPLACE: {market_path} plugin entry must be an object")
            name = entry.get("name")
            version = entry.get("version")
            source = entry.get("source")
            description = entry.get("description", "").strip().strip('"')
            if not name or not version:
                fail(f"INVALID MARKETPLACE: {market_path} every plugin needs name and version")
            if not description:
                fail(f"MISSING DESCRIPTION: {market_path} plugin {name}")
            if name in market_versions:
                fail(f"DUPLICATE MARKETPLACE ENTRY: {name} in {market_path}")
            expected_source = f"./skills/{name}"
            if source != expected_source:
                fail(f"WRONG SOURCE: {name} in {market_path} source={source!r} expected={expected_source!r}")
            market_versions[name] = version
            market_descriptions[name] = description

        missing_from_market = sorted(set(skill_versions) - set(market_versions))
        if missing_from_market:
            fail(f"NOT IN MARKETPLACE: {', '.join(missing_from_market)} in {market_path}")

        extra_in_market = sorted(set(market_versions) - set(skill_versions))
        if extra_in_market:
            fail(f"MISSING SKILL DIRECTORY: {', '.join(extra_in_market)} for {market_path}")

        for skill, skill_version in sorted(skill_versions.items()):
            market_version = market_versions[skill]
            if skill_version != market_version:
                fail(f"VERSION MISMATCH: {skill} in {market_path} SKILL={skill_version} MARKET={market_version}")
            if not market_descriptions[skill].startswith(skill_descriptions[skill]):
                fail(
                    f"DESCRIPTION MISMATCH: {skill} in {market_path}\n"
                    f"  SKILL.md:    {skill_descriptions[skill]}\n"
                    f"  marketplace: {market_descriptions[skill]}\n"
                    f"  marketplace description must start with the SKILL.md description"
                )

        if args.verbose or sys.stdout.isatty():
            print(f"{COLOR_GREEN}ok:{COLOR_RESET} {market_dir} marketplace")
        else:
            print(f"ok: {market_dir} marketplace")

    # Direct local references
    ref_pattern = re.compile(r'(?<![/.])\b(?:references|agents|scripts)/[\w/.-]+\b')
    script_pattern = re.compile(r'\}/scripts/([\w/.-]+)')
    for path in skill_files:
        skill_dir = path.parent.name
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            fail(f"READ ERROR: Could not read {path}: {e}")

        refs = set(ref_pattern.findall(text))
        refs |= {"scripts/" + s for s in script_pattern.findall(text)}
        for ref in sorted(refs):
            expected = root / "skills" / skill_dir / ref
            if not expected.exists():
                fail(f"BROKEN REFERENCE: {path} references {ref} but file does not exist")
            if args.verbose:
                if sys.stdout.isatty():
                    print(f"{COLOR_GREEN}ok:{COLOR_RESET} reference {skill_dir}/{ref}")
                else:
                    print(f"ok: reference {skill_dir}/{ref}")

    # Description conformance
    for skill, description in sorted(skill_descriptions.items()):
        clean = description.strip().strip('"')
        length = len(clean)
        if length < 40:
            fail(f"DESCRIPTION TOO SHORT: {skill} ({length} chars); need ≥40 for reliable resolver matching")
        if length > 500:
            fail(f"DESCRIPTION TOO LONG: {skill} ({length} chars); trim to ≤500 to keep the resolver index light")

        first_word = clean.split()[0].lower() if clean.split() else ""
        passive_starters = ("the", "a", "an", "this", "it")
        if first_word in passive_starters:
            fail(
                f"DESCRIPTION STARTS WITH ARTICLE: {skill}\n"
                f"  Start with a verb or action phrase (third-person). Got: {clean[:60]!r}"
            )
        if "not for" not in clean.lower():
            fail(
                f"DESCRIPTION MISSING EXCLUSION CLAUSE: {skill}\n"
                f"  Must contain a 'Not for ...' clause so the resolver learns when NOT to fire. Got: {clean[:120]!r}"
            )
        if args.verbose or sys.stdout.isatty():
            print(f"{COLOR_GREEN}ok:{COLOR_RESET} description {skill} ({length} chars)")
        else:
            print(f"ok: description {skill} ({length} chars)")

    # RESOLVER.md coverage
    resolver_path = root / "skills" / "RESOLVER.md"
    if not resolver_path.exists():
        fail(f"MISSING RESOLVER: expected {resolver_path}")

    try:
        resolver_text = resolver_path.read_text(encoding="utf-8")
    except Exception as e:
        fail(f"READ ERROR: Could not read {resolver_path}: {e}")

    for skill in sorted(skill_versions):
        token = f"skills/{skill}/SKILL.md"
        if token not in resolver_text:
            fail(
                f"RESOLVER GAP: {skill} has no entry in {resolver_path}\n"
                f"  Add a row to a triggers table that references {token!r}."
            )
        if args.verbose or sys.stdout.isatty():
            print(f"{COLOR_GREEN}ok:{COLOR_RESET} resolver entry for {skill}")
        else:
            print(f"ok: resolver entry for {skill}")

    # Check for specific files that exist for skills that use them
    reference_files = [
        "skills/design/references/design-reference.md",
        "skills/read/references/read-methods.md",
        "skills/write/references/write-en.md",
        "skills/health/agents/inspector-context.md",
        "skills/health/agents/inspector-control.md",
        "skills/check/agents/reviewer-security.md",
        "skills/check/agents/reviewer-architecture.md",
        "skills/check/references/persona-catalog.md",
        "rules/english.md"
    ]
    for rel_path in reference_files:
        file_path = root / rel_path
        if not file_path.is_file():
            fail(f"MISSING REQUIRED FILE: {rel_path} does not exist")

    print("references: ok")


if __name__ == "__main__":
    main()
