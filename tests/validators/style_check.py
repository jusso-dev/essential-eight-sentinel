"""Repository style and hygiene checker.

Enforces CONTRIBUTING.md rules:
- No em dashes (U+2014)
- No emojis
- No real Azure tenant or subscription GUIDs
- No claims of ASD, ACSC or Microsoft endorsement
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

EM_DASH = "\u2014"

# Comprehensive Unicode emoji detection (emoticons, symbols, pictographs, flags, dingbats).
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U0001F1E0-\U0001F1FF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "\uFE0F"
    "]"
)

# Detect explicit tenantId / subscriptionId literals that are not placeholder GUIDs.
TENANT_OR_SUB_RE = re.compile(
    r'(?:tenant[_-]?id|subscription[_-]?id)["\']?\s*[:=]\s*["\']?'
    r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
    re.IGNORECASE,
)

ALLOWED_PLACEHOLDER_GUIDS = frozenset(
    {
        "00000000-0000-0000-0000-000000000000",
        "11111111-1111-1111-1111-111111111111",
    }
)

# Catch affirmative endorsement claims while permitting explicit disclaimers ("not ... endorsed").
ENDORSEMENT_CLAIM_RE = re.compile(
    r"\b(?:officially\s+endorsed\s+by|endorsed\s+by\s+(?:the\s+)?(?:ASD|ACSC|Microsoft)"
    r"|official\s+(?:ASD|ACSC|Microsoft)\s+(?:solution|product|workbook))\b",
    re.IGNORECASE,
)
NEGATION_CONTEXT_RE = re.compile(
    r"\b(?:not|never|no|neither|without)\b",
    re.IGNORECASE,
)

SKIP_DIRS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"})
TEXT_EXTENSIONS = frozenset(
    {
        ".md",
        ".yml",
        ".yaml",
        ".json",
        ".kql",
        ".csv",
        ".py",
        ".ps1",
        ".sh",
        ".txt",
        ".jsonc",
    }
)


def check_text(text: str, label: str = "<string>") -> list[str]:
    """Return a list of style violation messages for the given text."""
    violations: list[str] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        if EM_DASH in line:
            violations.append(f"{label}:{lineno}: contains forbidden em dash (U+2014)")

        emoji_match = EMOJI_RE.search(line)
        if emoji_match:
            codepoint = f"U+{ord(emoji_match.group(0)):04X}"
            violations.append(f"{label}:{lineno}: contains forbidden emoji character ({codepoint})")

        for match in TENANT_OR_SUB_RE.finditer(line):
            guid = match.group(1).lower()
            if guid not in ALLOWED_PLACEHOLDER_GUIDS:
                violations.append(
                    f"{label}:{lineno}: non-placeholder tenant or subscription GUID {guid!r}"
                )

        endorsement_match = ENDORSEMENT_CLAIM_RE.search(line)
        if endorsement_match:
            prefix = line[max(0, endorsement_match.start() - 40) : endorsement_match.start()]
            if not NEGATION_CONTEXT_RE.search(prefix):
                violations.append(
                    f"{label}:{lineno}: potential endorsement claim ({endorsement_match.group(0)!r})"
                )

    return violations


def iter_repo_files(root: Path) -> list[Path]:
    """Return sorted repository text files subject to style checks."""
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name in ("LICENSE",):
            files.append(path)
    return sorted(files)


def check_repository(root: Path) -> list[str]:
    """Run style checks across all eligible files in the repository."""
    violations: list[str] = []
    for path in iter_repo_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        violations.extend(check_text(text, rel))
    return violations


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    violations = check_repository(root)
    if violations:
        for item in violations:
            print(item, file=sys.stderr)
        print(f"Style check failed with {len(violations)} violation(s).", file=sys.stderr)
        return 1
    print("Style check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
