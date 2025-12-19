from __future__ import annotations

import sys
from pathlib import Path

# Allow running this file directly (e.g. VS Code "Run Python File") from inside
# the package directory by ensuring the package's parent directory is on sys.path.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from ai.cube_ai_state import CubeAIState
from core.cube_state import CubeState
from core.move_engine import CubeMoveEngine
from utils.scramble import generate_scramble
from visualization.renderer import render_cube_flat


def main() -> None:
    cube = CubeState.solved()
    engine = CubeMoveEngine(cube)

    scramble = generate_scramble(20)
    print('Scramble:', ' '.join(scramble))
    engine.apply_sequence(scramble)

    print(render_cube_flat(cube))

    ai_state = CubeAIState.from_cube_state(cube)
    print('corner_permutation:', ai_state.corner_permutation.tolist())
    print('corner_orientation:', ai_state.corner_orientation.tolist())
    print('edge_permutation:', ai_state.edge_permutation.tolist())
    print('edge_orientation:', ai_state.edge_orientation.tolist())


if __name__ == '__main__':
    main()
