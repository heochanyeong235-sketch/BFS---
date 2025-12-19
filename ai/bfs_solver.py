from __future__ import annotations

import pickle
from array import array
from collections import deque
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Optional

from core.cube_state import CubeState
from core.move_engine import CubeMoveEngine
from core.constants import (
    MOVE_TOKENS,
    FACE_U,
    FACE_D,
    FACE_F,
    FACE_B,
    FACE_L,
    FACE_R,
    EDGE_UF,
    EDGE_UR,
    EDGE_UB,
    EDGE_UL,
    EDGE_DF,
    EDGE_DR,
    EDGE_DB,
    EDGE_DL,
    EDGE_FR,
    EDGE_RB,
    EDGE_BL,
    EDGE_LF,
)
from ai.cube_ai_state import CubeAIState


@dataclass(frozen=True)
class _MoveEffect:
    forward_pos: tuple[int, ...]  # len=12, maps old_pos -> new_pos
    flip_by_new_pos: tuple[int, ...]  # len=12, 0/1 orientation xor applied at landing position


@dataclass(frozen=True)
class _CrossState:
    positions: tuple[int, int, int, int]  # current positions of the 4 target edges
    orientations: tuple[int, int, int, int]  # current orientations (0/1) of the 4 target edges


_CROSS_EDGE_IDS_U = (EDGE_UF, EDGE_UR, EDGE_UB, EDGE_UL)
_MOVE_EFFECTS: dict[str, _MoveEffect] | None = None
_DIST_BY_FACE: dict[int, array] = {}
_CACHE_LOADED = False
_CACHE_VERSION = 1
_CACHE_PATH = Path(__file__).resolve().with_name('_cross_dist_cache_v1.pkl')

_CROSS_EDGES_BY_FACE: dict[int, tuple[int, int, int, int]] = {
    FACE_U: (EDGE_UF, EDGE_UR, EDGE_UB, EDGE_UL),
    FACE_D: (EDGE_DF, EDGE_DR, EDGE_DB, EDGE_DL),
    FACE_F: (EDGE_UF, EDGE_FR, EDGE_DF, EDGE_LF),
    FACE_B: (EDGE_UB, EDGE_RB, EDGE_DB, EDGE_BL),
    FACE_L: (EDGE_UL, EDGE_BL, EDGE_DL, EDGE_LF),
    FACE_R: (EDGE_UR, EDGE_FR, EDGE_DR, EDGE_RB),
}

_POSITIONS_BY_RANK: list[tuple[int, int, int, int]] = []
_RANK_BY_POSITIONS: dict[tuple[int, int, int, int], int] = {}


def _init_rank_tables() -> None:
    if _POSITIONS_BY_RANK:
        return
    for rank, tup in enumerate(permutations(range(12), 4)):
        t = tuple(int(x) for x in tup)
        _RANK_BY_POSITIONS[t] = rank
        _POSITIONS_BY_RANK.append(t)  # type: ignore[arg-type]


def _try_load_cache() -> None:
    global _CACHE_LOADED
    if _CACHE_LOADED:
        return
    _CACHE_LOADED = True

    if not _CACHE_PATH.exists():
        return

    try:
        data = pickle.loads(_CACHE_PATH.read_bytes())
    except Exception:
        return

    if not isinstance(data, dict):
        return

    _init_rank_tables()
    n_states = len(_POSITIONS_BY_RANK) * 16
    if not _cache_header_ok(data, n_states):
        return

    faces_blob = data.get('faces')
    if not isinstance(faces_blob, dict):
        return

    _load_face_tables_from_cache(faces_blob, n_states)


def _cache_header_ok(data: dict, n_states: int) -> bool:
    if data.get('version') != _CACHE_VERSION:
        return False
    if data.get('move_tokens') != MOVE_TOKENS:
        return False
    if data.get('n_states') != n_states:
        return False
    return True


def _load_face_tables_from_cache(faces_blob: dict, n_states: int) -> None:
    for face, blob in faces_blob.items():
        try:
            face_id = int(face)
        except Exception:
            continue
        if not isinstance(blob, (bytes, bytearray)):
            continue
        arr = array('h')
        try:
            arr.frombytes(blob)
        except Exception:
            continue
        if len(arr) != n_states:
            continue
        _DIST_BY_FACE[face_id] = arr


def _save_cache() -> None:
    _init_rank_tables()
    n_states = len(_POSITIONS_BY_RANK) * 16
    payload = {
        'version': _CACHE_VERSION,
        'move_tokens': MOVE_TOKENS,
        'n_states': n_states,
        'faces': {int(face): dist.tobytes() for face, dist in _DIST_BY_FACE.items()},
    }
    tmp = _CACHE_PATH.with_suffix(_CACHE_PATH.suffix + '.tmp')
    tmp.write_bytes(pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL))
    tmp.replace(_CACHE_PATH)


def _encode_cross_state(state: _CrossState) -> int:
    _init_rank_tables()
    rank = _RANK_BY_POSITIONS[state.positions]
    ori_bits = (
        (state.orientations[0] & 1)
        | ((state.orientations[1] & 1) << 1)
        | ((state.orientations[2] & 1) << 2)
        | ((state.orientations[3] & 1) << 3)
    )
    return rank * 16 + ori_bits


def _decode_cross_state(index: int) -> _CrossState:
    _init_rank_tables()
    rank = index // 16
    ori_bits = index % 16
    positions = _POSITIONS_BY_RANK[rank]
    orientations = (
        (ori_bits >> 0) & 1,
        (ori_bits >> 1) & 1,
        (ori_bits >> 2) & 1,
        (ori_bits >> 3) & 1,
    )
    return _CrossState(positions, orientations)


def _build_move_effects() -> dict[str, _MoveEffect]:
    effects: dict[str, _MoveEffect] = {}
    for mv in MOVE_TOKENS:
        cube = CubeState.solved()
        CubeMoveEngine(cube).apply(mv)
        ai_state = CubeAIState.from_cube_state(cube)

        # For solved cube: new_ep[new_pos] = old_pos (since old_perm is identity)
        ep_after = [int(x) for x in ai_state.edge_permutation.tolist()]
        eo_after = [int(x) for x in ai_state.edge_orientation.tolist()]

        forward_pos = [0] * 12
        for new_pos, old_pos in enumerate(ep_after):
            forward_pos[old_pos] = new_pos
        effects[mv] = _MoveEffect(tuple(forward_pos), tuple(eo_after))
    return effects


def _apply_move_to_cross_state(state: _CrossState, effect: _MoveEffect) -> _CrossState:
    new_positions = [0, 0, 0, 0]
    new_orientations = [0, 0, 0, 0]

    for i in range(4):
        old_pos = state.positions[i]
        new_pos = effect.forward_pos[old_pos]
        new_positions[i] = new_pos
        new_orientations[i] = state.orientations[i] ^ (effect.flip_by_new_pos[new_pos] & 1)

    return _CrossState(tuple(new_positions), tuple(new_orientations))


def _ensure_cross_distance_table(face: int) -> tuple[dict[str, _MoveEffect], array]:
    global _MOVE_EFFECTS

    _init_rank_tables()
    _try_load_cache()
    if _MOVE_EFFECTS is None:
        _MOVE_EFFECTS = _build_move_effects()

    cached = _DIST_BY_FACE.get(face)
    if cached is not None:
        return _MOVE_EFFECTS, cached

    edges = _CROSS_EDGES_BY_FACE.get(face)
    if edges is None:
        raise ValueError(f'unknown face id: {face!r}')

    n_states = len(_POSITIONS_BY_RANK) * 16
    dist = array('h', [-1]) * n_states

    goal = _CrossState(positions=edges, orientations=(0, 0, 0, 0))
    goal_idx = _encode_cross_state(goal)
    dist[goal_idx] = 0

    q: deque[int] = deque([goal_idx])
    while q:
        cur_idx = q.popleft()
        cur_d = dist[cur_idx]
        cur_state = _decode_cross_state(cur_idx)

        for mv in MOVE_TOKENS:
            nxt_state = _apply_move_to_cross_state(cur_state, _MOVE_EFFECTS[mv])
            nxt_idx = _encode_cross_state(nxt_state)
            if dist[nxt_idx] != -1:
                continue
            dist[nxt_idx] = cur_d + 1
            q.append(nxt_idx)

    _DIST_BY_FACE[face] = dist
    try:
        _save_cache()
    except Exception:
        pass
    return _MOVE_EFFECTS, dist


class BFSSolver:
    """Fast cross-only solver.

    Despite the name, this uses a precomputed BFS distance table over the reduced
    state space (only the 4 cross edges). This makes it fast enough for 20-move scrambles.
    """

    def __init__(self, target_center_face: int = FACE_U):
        self.target_center_face = target_center_face

    def solve_cross(self, start_cube: CubeState, max_depth: Optional[int] = None) -> Optional[list[str]]:
        move_effects, dist = _ensure_cross_distance_table(self.target_center_face)
        edges = _CROSS_EDGES_BY_FACE[self.target_center_face]

        start_ai_state = CubeAIState.from_cube_state(start_cube)
        if start_ai_state.is_cross_solved(self.target_center_face):
            return []

        positions: list[int] = []
        orientations: list[int] = []
        edge_perm = [int(x) for x in start_ai_state.edge_permutation.tolist()]
        edge_ori = [int(x) for x in start_ai_state.edge_orientation.tolist()]

        for edge_id in edges:
            pos = edge_perm.index(edge_id)
            positions.append(pos)
            orientations.append(edge_ori[pos] & 1)

        state = _CrossState(tuple(positions), tuple(orientations))
        idx = _encode_cross_state(state)
        d0 = dist[idx]
        if d0 < 0:
            return None
        if max_depth is not None and d0 > max_depth:
            return None

        solution: list[str] = []
        cur_state = state
        cur_d = d0
        while cur_d > 0:
            found = False
            for mv in MOVE_TOKENS:
                nxt_state = _apply_move_to_cross_state(cur_state, move_effects[mv])
                nxt_idx = _encode_cross_state(nxt_state)
                nxt_d = dist[nxt_idx]
                if nxt_d == cur_d - 1:
                    solution.append(mv)
                    cur_state = nxt_state
                    cur_d = nxt_d
                    found = True
                    break
            if not found:
                return None

        return solution