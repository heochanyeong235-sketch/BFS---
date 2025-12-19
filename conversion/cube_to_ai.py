from __future__ import annotations

import numpy as np

from core.cube_state import CubeState
from core.constants import (
    CORNER_COLOR_SETS,
    CORNER_STICKER_POSITIONS,
    EDGE_COLOR_SETS,
    EDGE_STICKER_POSITIONS,
    COLOR_WHITE,
    COLOR_YELLOW,
)


def _read_stickers(cube: np.ndarray, coords: list[tuple[int, int, int]]) -> list[int]:
    return [int(cube[f, r, c]) for f, r, c in coords]


def identify_corner_piece_id(colors: list[int]) -> int:
    s = set(colors)
    for piece_id, color_set in CORNER_COLOR_SETS.items():
        if s == color_set:
            return piece_id
    raise ValueError(f'invalid corner colors: {colors!r}')


def identify_corner_orientation(colors: list[int]) -> int:
    for idx, c in enumerate(colors):
        if c in (COLOR_WHITE, COLOR_YELLOW):
            return idx
    raise ValueError(f'corner missing U/D color: {colors!r}')


def identify_edge_piece_id(colors: list[int]) -> int:
    s = set(colors)
    for piece_id, color_set in EDGE_COLOR_SETS.items():
        if s == color_set:
            return piece_id
    raise ValueError(f'invalid edge colors: {colors!r}')


def _expected_edge_color_order(piece_id: int) -> tuple[int, int]:
    solved = CubeState.solved().stickers
    coords = EDGE_STICKER_POSITIONS[piece_id]
    return tuple(_read_stickers(solved, coords))  # type: ignore[return-value]


_EXPECTED_EDGE_ORDER = {pid: _expected_edge_color_order(pid) for pid in EDGE_STICKER_POSITIONS.keys()}


def identify_edge_orientation(colors: list[int]) -> int:
    piece_id = identify_edge_piece_id(colors)
    expected = _EXPECTED_EDGE_ORDER[piece_id]
    return 0 if (colors[0], colors[1]) == expected else 1


def cube_to_ai_arrays(cube_state: CubeState) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    cube = cube_state.stickers
    corner_perm = np.empty(8, dtype=np.int8)
    corner_ori = np.empty(8, dtype=np.int8)
    edge_perm = np.empty(12, dtype=np.int8)
    edge_ori = np.empty(12, dtype=np.int8)

    for pos_id, coords in CORNER_STICKER_POSITIONS.items():
        colors = _read_stickers(cube, coords)
        piece_id = identify_corner_piece_id(colors)
        corner_perm[pos_id] = piece_id
        corner_ori[pos_id] = identify_corner_orientation(colors)

    for pos_id, coords in EDGE_STICKER_POSITIONS.items():
        colors = _read_stickers(cube, coords)
        piece_id = identify_edge_piece_id(colors)
        edge_perm[pos_id] = piece_id
        edge_ori[pos_id] = identify_edge_orientation(colors)

    return corner_perm, corner_ori, edge_perm, edge_ori
