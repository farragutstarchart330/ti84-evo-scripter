#!/usr/bin/env python3
"""Repository-local structural validation for ti84-evo-scripter.

Checks the things a broken commit would break: required files, frontmatter
validity, the progressive-disclosure budget, cross-reference integrity, and
that the model registry and lint rule codes cited in SKILL.md actually exist.

Run the behavioural tooling checks separately -- `run_checks.py` does that.
This script is about repository shape.

Usage:
    python scripts/validate_skill.py .

Exit codes:
    0  valid
    1  at least one failure
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    ".gitignore",
    "evals/evals.json",
    "references/model-matrix.md",
    "references/ti-python-language.md",
    "references/transfer-options.md",
    "references/exam-legality.md",
    "assets/program_template.py",
    "assets/handout_template.html",
    "scripts/ti_models.py",
    "scripts/preflight.py",
    "scripts/run_checks.py",
    "scripts/lint_ti_python.py",
    "scripts/simulate_ti84.py",
    "scripts/_ti_sandbox.py",
    "scripts/verify_program.py",
    "scripts/make_handout.py",
    "scripts/ti_stubs/ti_system.py",
    "examples/TIPCALC/TIPCALC.py",
    "examples/TIPCALC/tests.json",
    "examples/TIPCALC/handout.json",
    "sandbox/README.md",
    "sandbox/REQUIREMENTS.md",
]

SKILL_REQUIRED_SECTIONS = [
    "# TI-84 Evo Scripter",
    "## Non-negotiables",
    "## Workflow",
    "## Worked example",
    "## Anti-patterns, and what enforces each",
    "## Troubleshooting",
    "## References",
]

SANDBOX_PROGRAMS = ["QUADRT", "TRISOLV", "STATS1", "COMPINT", "KINEMAT"]

MAX_SKILL_LINES = 500
MAX_SKILL_CHARS = 20000          # ~5k tokens at 4 chars/token
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
PROGRAM_NAME_RE = re.compile(r"^[A-Z][A-Z0-9]{0,7}$")

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def parse_frontmatter(content: str) -> tuple[dict[str, str], str | None]:
    if not content.startswith("---\n"):
        return {}, "SKILL.md must start with YAML frontmatter"
    try:
        _, frontmatter, _ = content.split("---\n", 2)
    except ValueError:
        return {}, "SKILL.md frontmatter must be closed with ---"

    values: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"')
    return values, None


def check_files(root: Path) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            fail("missing required file: %s" % rel)


def check_skill(root: Path) -> str:
    path = root / "SKILL.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")

    values, err = parse_frontmatter(text)
    if err:
        fail(err)
        return text

    name = values.get("name", "")
    if not NAME_RE.match(name):
        fail("frontmatter name %r must be lowercase alphanumeric-hyphens, "
             "1-64 chars" % name)

    desc = values.get("description", "")
    if not desc:
        fail("frontmatter description is missing")
    else:
        if not 1 <= len(desc) <= 1024:
            fail("description is %d chars; must be 1-1024" % len(desc))
        if not desc.startswith("Use when"):
            fail("description must start with 'Use when' for discovery")

    lines = len(text.splitlines())
    if lines > MAX_SKILL_LINES:
        fail("SKILL.md is %d lines; budget is %d" % (lines, MAX_SKILL_LINES))
    if len(text) > MAX_SKILL_CHARS:
        fail("SKILL.md is %d chars (~%d tokens); budget is %d chars"
             % (len(text), len(text) // 4, MAX_SKILL_CHARS))
    notes.append("SKILL.md %d/%d lines, ~%d/5000 tokens"
                 % (lines, MAX_SKILL_LINES, len(text) // 4))

    for section in SKILL_REQUIRED_SECTIONS:
        if section not in text:
            fail("SKILL.md is missing section: %s" % section)

    # The five non-negotiables must remain stated, not just headed.
    for phrase in ("accepts uploaded files", "Ship `.py` only",
                   "Numeric output only", "No f-strings",
                   "Never claim a check passed"):
        if phrase not in text:
            fail("SKILL.md no longer states non-negotiable: %r" % phrase)

    return text


def check_referenced_paths(root: Path, text: str) -> None:
    """Every scripts/ or references/ path named in SKILL.md must exist."""
    for rel in sorted(set(re.findall(
            r"(?:scripts|references|assets|examples)/[A-Za-z0-9_./-]+", text))):
        clean = rel.rstrip(".,);:`")
        if clean.endswith("/"):
            continue
        if not (root / clean).exists():
            fail("SKILL.md references a path that does not exist: %s" % clean)


def check_lint_codes(root: Path, text: str) -> None:
    """Rule codes cited in SKILL.md must be emitted by the linter."""
    lint = (root / "scripts" / "lint_ti_python.py")
    if not lint.is_file():
        return
    src = lint.read_text(encoding="utf-8")
    emitted = set(re.findall(r'"([EW]\d{3})"', src))
    cited = set(re.findall(r"\b([EW]\d{3})\b", text))
    for code in sorted(cited - emitted):
        fail("SKILL.md cites lint rule %s which the linter never emits" % code)
    if emitted:
        notes.append("linter emits %d rule codes" % len(emitted))


def check_models(root: Path) -> None:
    sys.path.insert(0, str(root / "scripts"))
    try:
        import ti_models
    except Exception as exc:                      # noqa: BLE001
        fail("cannot import scripts/ti_models.py: %s" % exc)
        return

    capable = ti_models.python_capable()
    if len(capable) < 6:
        fail("expected at least 6 Python-capable models, found %d" % len(capable))
    if not any(not m["python"] for m in ti_models.MODELS.values()):
        fail("registry has no non-Python models; the refusal path is untestable")
    if ti_models.DEFAULT_MODEL not in ti_models.MODELS:
        fail("DEFAULT_MODEL %r is not in the registry" % ti_models.DEFAULT_MODEL)

    for key, m in ti_models.MODELS.items():
        for field in ("label", "region", "python", "modules", "screen_cols",
                      "connect", "notes"):
            if field not in m:
                fail("model %r is missing field %r" % (key, field))
        if m["python"] and not m["modules"]:
            fail("model %r claims Python but has an empty module set" % key)
    for alias, target in ti_models.ALIASES.items():
        if target not in ti_models.MODELS:
            fail("alias %r points at unknown model %r" % (alias, target))

    notes.append("registry: %d models, %d Python-capable"
                 % (len(ti_models.MODELS), len(capable)))


def check_json(root: Path) -> None:
    for rel in sorted(str(p.relative_to(root)).replace("\\", "/")
                      for p in root.rglob("*.json")
                      if ".git" not in p.parts):
        try:
            json.loads((root / rel).read_text(encoding="utf-8"))
        except Exception as exc:                  # noqa: BLE001
            fail("invalid JSON in %s: %s" % (rel, exc))


def check_test_suites(root: Path) -> None:
    """Every tests.json must declare >=3 cases with real assertions."""
    for tests in sorted(root.rglob("tests.json")):
        rel = str(tests.relative_to(root)).replace("\\", "/")
        try:
            spec = json.loads(tests.read_text(encoding="utf-8"))
        except Exception:                         # noqa: BLE001
            continue                              # already reported by check_json
        cases = spec.get("cases", [])
        if len(cases) < 3:
            fail("%s has %d case(s); at least 3 required" % (rel, len(cases)))
        if not any("edge" in c.get("name", "").lower() for c in cases):
            fail("%s has no case named as an edge case" % rel)
        for c in cases:
            if not c.get("expect") and not c.get("reject"):
                fail("%s case %r asserts nothing"
                     % (rel, c.get("name", "?")))


def check_programs(root: Path) -> None:
    """Shipped .py programs must obey the rules the skill enforces."""
    targets = list((root / "examples").rglob("*.py"))
    targets += list((root / "sandbox").rglob("*.py"))
    if not targets:
        fail("no example or sandbox programs found")

    for path in sorted(targets):
        rel = str(path.relative_to(root)).replace("\\", "/")
        stem = path.stem
        if not PROGRAM_NAME_RE.match(stem):
            fail("%s: program name %r breaks the 1-8 uppercase AppVar rule"
                 % (rel, stem))
        src = path.read_text(encoding="utf-8")
        if re.search(r'\bf"', src) or re.search(r"\bf'", src):
            fail("%s contains an f-string" % rel)
        if '__main__' in src:
            fail("%s has a __main__ guard; the calculator imports to run" % rel)
        for i, line in enumerate(src.splitlines(), 1):
            if any(ord(ch) > 126 for ch in line):
                fail("%s line %d has a non-ASCII character" % (rel, i))
                break

    notes.append("validated %d shipped program(s)" % len(targets))


def check_sandbox(root: Path) -> None:
    sb = root / "sandbox"
    if not sb.is_dir():
        fail("sandbox/ is missing")
        return
    for name in SANDBOX_PROGRAMS:
        for rel in ("%s/%s.py" % (name, name), "%s/tests.json" % name,
                    "%s/handout.json" % name):
            if not (sb / rel).is_file():
                fail("sandbox is missing %s" % rel)
    readme = (sb / "README.md")
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        for name in SANDBOX_PROGRAMS:
            if name not in text:
                fail("sandbox/README.md does not mention %s" % name)


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    print("Validating AgentSkill repository: %s" % root)
    print("-" * 66)

    check_files(root)
    text = check_skill(root)
    if text:
        check_referenced_paths(root, text)
        check_lint_codes(root, text)
    check_models(root)
    check_json(root)
    check_test_suites(root)
    check_programs(root)
    check_sandbox(root)

    for note in notes:
        print("  info: %s" % note)
    if failures:
        print()
        for f in failures:
            print("  FAIL: %s" % f)
        print("-" * 66)
        print("%d failure(s)" % len(failures))
        return 1

    print("-" * 66)
    print("OK - repository structure is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
