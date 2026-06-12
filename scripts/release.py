#!/usr/bin/env python3
"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>release.py</name>
    <type>release_automation</type>
    <purpose>Bump version atomically across every tracked location + changelog scaffold</purpose>
  </file_meta>
</ai_agent_documentation>
-->

Release bumper. Usage: python scripts/release.py 2.6.0

Updates, atomically and consistently:
  - pyproject.toml            [project] version
  - aruco_generator/__init__.py  __version__
  - docs/CHANGELOG.md         [Unreleased] -> [x.y.z] - YYYY-MM-DD, fresh Unreleased scaffold
  - AI_NAVIGATION.xml         version attributes + last_updated

Then prints the commit/tag commands. It does NOT run git for you.
"""

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

UNRELEASED_SCAFFOLD = """## [Unreleased]
### Added
- TBD

### Changed
- TBD

### Removed
- TBD

"""


def fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def bump_pyproject(version: str) -> None:
    path = ROOT / "pyproject.toml"
    text = path.read_text()
    new, n = re.subn(
        r'(?m)^version = "[^"]+"$', f'version = "{version}"', text, count=1
    )
    if n != 1:
        fail("could not find version field in pyproject.toml")
    path.write_text(new)


def bump_init(version: str) -> None:
    path = ROOT / "aruco_generator" / "__init__.py"
    text = path.read_text()
    new, n = re.subn(
        r'(?m)^__version__ = "[^"]+"$', f'__version__ = "{version}"', text, count=1
    )
    if n != 1:
        fail("could not find __version__ in aruco_generator/__init__.py")
    path.write_text(new)


def bump_changelog(version: str, today: str) -> None:
    path = ROOT / "docs" / "CHANGELOG.md"
    text = path.read_text()
    if "## [Unreleased]" not in text:
        fail("docs/CHANGELOG.md has no [Unreleased] section")
    if f"## [{version}]" in text:
        fail(f"version {version} already exists in CHANGELOG")
    new = text.replace(
        "## [Unreleased]",
        UNRELEASED_SCAFFOLD + f"## [{version}] - {today}",
        1,
    )
    path.write_text(new)


def bump_navigation(version: str, today: str) -> None:
    path = ROOT / "AI_NAVIGATION.xml"
    text = path.read_text()
    text = re.sub(r"<version>[\d.]+</version>", f"<version>{version}</version>", text)
    text = re.sub(
        r'<ai_navigation version="[\d.]+"', f'<ai_navigation version="{version}"', text
    )
    text = re.sub(
        r"<last_updated>[\d-]+</last_updated>",
        f"<last_updated>{today}</last_updated>",
        text,
    )
    path.write_text(text)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: python scripts/release.py <version>")
    version = sys.argv[1]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"version must be semver (x.y.z), got: {version}")

    today = datetime.date.today().isoformat()
    bump_pyproject(version)
    bump_init(version)
    bump_changelog(version, today)
    bump_navigation(version, today)

    print(f"Bumped all version locations to {version}.")
    print("Review docs/CHANGELOG.md (fill in the release notes), then:")
    print(f'  git commit -am "Release v{version}"')
    print(f'  git tag -a v{version} -m "Release v{version}"')
    print("  git push origin main --tags")


if __name__ == "__main__":
    main()
