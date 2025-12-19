from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from conversion.cube_to_ai import cube_to_ai_arrays
from core.cube_state import CubeState
from core import constants


@dataclass(frozen=True)
class CubeAIState:
    corner_permutation: np.ndarray
    corner_orientation: np.ndarray
    edge_permutation: np.ndarray
    edge_orientation: np.ndarray

    @classmethod
    def from_cube_state(cls, cube_state: CubeState) -> CubeAIState:
        cp, co, ep, eo = cube_to_ai_arrays(cube_state)
        return cls(cp, co, ep, eo)

    def is_solved(self) -> bool:
        return (
            np.array_equal(self.corner_permutation, np.arange(8))
            and np.all(self.corner_orientation == 0)
            and np.array_equal(self.edge_permutation, np.arange(12))
            and np.all(self.edge_orientation == 0)
        )

    def is_cross_solved(self, cross_center_face: int) -> bool:
        cross_edges_by_face = {
            constants.FACE_U: [constants.EDGE_UF, constants.EDGE_UR, constants.EDGE_UB, constants.EDGE_UL],
            constants.FACE_D: [constants.EDGE_DF, constants.EDGE_DR, constants.EDGE_DB, constants.EDGE_DL],
            constants.FACE_F: [constants.EDGE_UF, constants.EDGE_FR, constants.EDGE_DF, constants.EDGE_LF],
            constants.FACE_B: [constants.EDGE_UB, constants.EDGE_RB, constants.EDGE_DB, constants.EDGE_BL],
            constants.FACE_L: [constants.EDGE_UL, constants.EDGE_BL, constants.EDGE_DL, constants.EDGE_LF],
            constants.FACE_R: [constants.EDGE_UR, constants.EDGE_FR, constants.EDGE_DR, constants.EDGE_RB],
        }
        edge_positions = cross_edges_by_face.get(cross_center_face)
        if edge_positions is None:
            raise ValueError(f'unknown face id: {cross_center_face!r}')

        for pos in edge_positions:
            if int(self.edge_permutation[pos]) != pos:
                return False
            if int(self.edge_orientation[pos]) != 0:
                return False
        return True

    @staticmethod
    def find_best_cross_solutions(
        cube_state: CubeState,
        max_depth: int | None = None,
        include_white: bool = True,
    ) -> tuple[int, list[tuple[int, list[str]]]]:
        """Try multiple face crosses and return all shortest solutions.

        Returns:
        - best_len
        - list of (face_id, solution_moves) for all faces tied at best_len
        """
        # Local import to avoid circular import at module import time.
        from ai.bfs_solver import BFSSolver

        faces = [
            constants.FACE_U,
            constants.FACE_D,
            constants.FACE_F,
            constants.FACE_B,
            constants.FACE_L,
            constants.FACE_R,
        ]
        if not include_white:
            faces = [f for f in faces if f != constants.FACE_U]

        best_len: int | None = None
        best: list[tuple[int, list[str]]] = []

        for face in faces:
            solver = BFSSolver(target_center_face=face)
            sol = solver.solve_cross(cube_state, max_depth=max_depth)
            if sol is None:
                continue
            l = len(sol)
            if best_len is None or l < best_len:
                best_len = l
                best = [(face, sol)]
            elif l == best_len:
                best.append((face, sol))

        if best_len is None:
            return (10**9, [])
        return best_len, best

    @staticmethod
    def find_multiple_cross_solutions(
        cube_state: CubeState,
        max_depth: int | None = None,
        max_solutions: int = 10,
        include_white: bool = True,
    ) -> list[tuple[int, int, list[str]]]:  # (face_id, length, solution_moves)
        """Try multiple face crosses and return multiple solutions sorted by length.

        Returns:
        - List of (face_id, solution_length, solution_moves) sorted by length
        """
        # Local import to avoid circular import at module import time.
        from ai.bfs_solver import BFSSolver

        faces = [
            constants.FACE_U,
            constants.FACE_D,
            constants.FACE_F,
            constants.FACE_B,
            constants.FACE_L,
            constants.FACE_R,
        ]
        if not include_white:
            faces = [f for f in faces if f != constants.FACE_U]

        all_solutions: list[tuple[int, int, list[str]]] = []

        for face in faces:
            solver = BFSSolver(target_center_face=face)
            
            # Try different depths to get multiple solutions
            for depth in range(1, (max_depth or 8) + 1):
                sol = solver.solve_cross(cube_state, max_depth=depth)
                if sol is not None:
                    all_solutions.append((face, len(sol), sol))
                    break  # Found solution for this face at this depth

        # Sort by solution length, then by face id for consistency
        all_solutions.sort(key=lambda x: (x[1], x[0]))
        
        # Return top max_solutions
        return all_solutions[:max_solutions]