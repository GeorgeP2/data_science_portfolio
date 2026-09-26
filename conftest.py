"""Make every ``projects/*/src`` importable during tests.

Each project's package has a unique name (derived from its slug), so they can
all share one ``sys.path`` without collisions.
"""

import sys
from pathlib import Path

for src in sorted(Path(__file__).parent.glob("projects/*/src")):
    if src.parent.name != "_template":
        sys.path.insert(0, str(src))
