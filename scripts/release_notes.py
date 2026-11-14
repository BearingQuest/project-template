"""Write the CHANGELOG.md section for one release version to a file.

Used by the build job in .github/workflows/release.yml. A version with no
section (or an empty one) is an error; there is no fallback to another section.

Usage: release_notes.py VERSION CHANGELOG OUTPUT
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def release_notes(changelog: str, version: str) -> str:
    """Return the text under the `## <version>` heading, or raise ValueError."""
    heading = re.compile(rf"^## \[?{re.escape(version)}\]?(?: .*)?$")
    lines = changelog.splitlines()
    start = next((i for i, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        raise ValueError(f"CHANGELOG.md has no section for {version}")
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    notes = "\n".join(body).strip()
    if not notes:
        raise ValueError(f"CHANGELOG.md section for {version} is empty")
    return notes + "\n"


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        sys.stderr.write(__doc__ or "")
        return 2
    version, changelog, output = argv[1], Path(argv[2]), Path(argv[3])
    try:
        notes = release_notes(changelog.read_text(encoding="utf-8"), version)
    except ValueError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    output.write_text(notes, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
