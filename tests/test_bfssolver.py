# tests/test_bfs_solver.py

import unittest
import numpy as np
import os
import sys

# 테스트 실행 환경을 위한 경로 설정 (기존 test_refactored_cube.py의 방식을 따름)
# 프로젝트 루트 디렉토리를 PYTHONPATH에 추가한다고 가정
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.cube_state import CubeState
from core.move_engine import CubeMoveEngine
from ai.cube_ai_state import CubeAIState
from ai.bfs_solver import BFSSolver
from core.constants import FACE_U, FACE_F
import core.constants as constants

class TestBFSSolver(unittest.TestCase):
    """BFS 크로스 솔버 및 크로스 검증 로직 테스트"""

    def setUp(self):
        """매 테스트 실행 전, 솔버 인스턴스 준비"""
        self.solver = BFSSolver(target_center_face=FACE_U)

    def test_bfs_solves_green_cross(self):
        """BFSSolver가 F(초록) 크로스도 해결할 수 있어야 한다."""
        cube = CubeState.solved()
        self.apply_moves(cube, ['R', 'U', 'F'])

        solver = BFSSolver(target_center_face=FACE_F)
        solution = solver.solve_cross(cube, max_depth=None)
        self.assertIsNotNone(solution)

        solved_cube = cube.copy()
        self.apply_moves(solved_cube, solution)
        ai_state = CubeAIState.from_cube_state(solved_cube)
        self.assertTrue(ai_state.is_cross_solved(FACE_F))
    
    def apply_moves(self, cube: CubeState, moves: list[str]) -> CubeState:
        """주어진 큐브에 무브 시퀀스를 적용하는 헬퍼 함수"""
        engine = CubeMoveEngine(cube)
        engine.apply_sequence(moves)
        return cube

    # ----------------------------------------------------
    # 1. is_cross_solved() 검증 테스트
    # ----------------------------------------------------
    def test_solved_cube_is_cross_solved(self):
        """해결된 큐브는 U-크로스가 해결된 상태여야 한다."""
        solved_cube = CubeState.solved()
        ai_state = CubeAIState.from_cube_state(solved_cube)
        
        self.assertTrue(ai_state.is_cross_solved(FACE_U), "해결된 큐브는 U-크로스가 해결되어야 합니다.")

    def test_single_move_R_is_not_cross_solved(self):
        """'R' 무브가 적용된 큐브는 U-크로스가 해결되지 않아야 한다."""
        cube = CubeState.solved()
        self.apply_moves(cube, ['R']) # U-크로스 엣지 (UF, UR)에 영향을 줌
        
        ai_state = CubeAIState.from_cube_state(cube)
        self.assertFalse(ai_state.is_cross_solved(FACE_U), "R 무브 후 U-크로스는 해결되지 않아야 합니다.")
        
    def test_single_move_U2_is_not_cross_solved(self):
        """'U2' 무브는 U-크로스 엣지의 위치(Permutation)를 바꾼다."""
        cube = CubeState.solved()
        self.apply_moves(cube, ['U2']) 
        
        ai_state = CubeAIState.from_cube_state(cube)
        self.assertFalse(ai_state.is_cross_solved(FACE_U), "U2 무브 후 U-크로스는 해결되지 않아야 합니다 (위치 변경).")

    # ----------------------------------------------------
    # 2. BFSSolver 탐색 기능 테스트
    # ----------------------------------------------------
    
    # 2.1 깊이 1 테스트
    def test_bfs_solves_depth_1(self):
        """BFS 솔버가 깊이 1의 해답(역무브)을 찾아야 한다."""
        
        # 해답: F'
        cube = CubeState.solved()
        self.apply_moves(cube, ['F']) # 현재 상태: F
        
        # F'은 U-Cross 엣지 UF를 다시 제자리로 돌려놓으면서 EO=0을 만족시켜야 함.
        solution = self.solver.solve_cross(cube, max_depth=1) 
        
        self.assertIsNotNone(solution, "깊이 1의 해답을 찾지 못했습니다.")
        self.assertEqual(len(solution), 1, "해답 길이가 1이어야 합니다.")
        self.assertEqual(solution[0], "F'", "최단 해답은 F'이어야 합니다.")


    # 2.2 깊이 2 테스트
    def test_bfs_solves_depth_2_example(self):
        """BFS 솔버가 깊이 2의 해답을 찾아야 한다. (R D')"""
        
        # R D'는 U면 엣지인 UR과 DF(코너)를 움직여 U-크로스를 깨뜨림.
        # R' D는 U면 엣지 UR과 DF를 움직여 U-크로스를 깨뜨림.
        # Scramble: R U
        cube = CubeState.solved()
        self.apply_moves(cube, ['R', "U"]) 
        
        # Solution: U' R' (깊이 2)
        solution = self.solver.solve_cross(cube, max_depth=2)
        
        self.assertIsNotNone(solution, "깊이 2의 해답(U' R')을 찾지 못했습니다.")
        self.assertEqual(len(solution), 2, "해답 길이가 2이어야 합니다.")
        self.assertEqual(solution[0], "U'", "첫 번째 해답 무브는 U'이어야 합니다.")
        self.assertEqual(solution[1], "R'", "두 번째 해답 무브는 R'이어야 합니다.")


    # 2.3 깊이 제한 테스트
    def test_bfs_depth_limit(self):
        """BFS는 최대 깊이를 초과하는 솔루션을 찾지 않아야 한다."""
        
        # 해답: U' R' L D F' B2 (6수)가 필요하다고 가정하고, max_depth를 3으로 설정하면 실패해야 함.
        # 실제 6수 스크램블을 찾아 테스트해야 하지만, 일단 R U U' R'으로 테스트합니다.
        
        # 'R U' 상태는 보통 2수 해답(U' R')로 크로스를 복구할 수 있으므로,
        # 깊이 1에서는 실패, 깊이 2에서는 성공을 기대합니다.
        cube = CubeState.solved()
        self.apply_moves(cube, ['R', 'U'])  # R U 상태

        solution_fail = self.solver.solve_cross(cube, max_depth=1)
        self.assertIsNone(solution_fail, "최대 깊이 1으로는 2수 해답을 찾지 못해야 합니다.")

        cube_2 = CubeState.solved()
        self.apply_moves(cube_2, ['R', 'U'])
        solution_success = self.solver.solve_cross(cube_2, max_depth=2)
        self.assertIsNotNone(solution_success, "최대 깊이 2에서는 해답을 찾아야 합니다.")
        self.assertEqual(len(solution_success), 2)


if __name__ == '__main__':
    unittest.main()