from __future__ import annotations

import sys
from pathlib import Path

# Allow running this file directly from inside the package directory by ensuring
# the package's parent directory is on sys.path.
if __package__ in (None, ''):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from visualization.tk_visualizer import main


if __name__ == '__main__':
    main()
