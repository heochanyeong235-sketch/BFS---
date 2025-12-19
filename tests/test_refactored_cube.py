import unittest

import numpy as np

from ai.cube_ai_state import CubeAIState
from core.cube_state import CubeState
from core.move_engine import CubeMoveEngine


class TestRefactoredCube(unittest.TestCase):
    def test_solved_to_ai_is_identity(self):
        cube = CubeState.solved()
        ai = CubeAIState.from_cube_state(cube)
        self.assertTrue(np.array_equal(ai.corner_permutation, np.arange(8)))
        self.assertTrue(np.all(ai.corner_orientation == 0))
        self.assertTrue(np.array_equal(ai.edge_permutation, np.arange(12)))
        self.assertTrue(np.all(ai.edge_orientation == 0))

    def test_move_then_inverse_returns_solved(self):
        inverse = {
            'R': "R'",
            'L': "L'",
            'U': "U'",
            'D': "D'",
            'F': "F'",
            'B': "B'",
            "R'": 'R',
            "L'": 'L',
            "U'": 'U',
            "D'": 'D',
            "F'": 'F',
            "B'": 'B',
        }
        for mv in ['R', 'L', 'U', 'D', 'F', 'B']:
            cube = CubeState.solved()
            engine = CubeMoveEngine(cube)
            engine.apply(mv)
            engine.apply(inverse[mv])
            self.assertEqual(cube, CubeState.solved())


if __name__ == '__main__':
    unittest.main()
