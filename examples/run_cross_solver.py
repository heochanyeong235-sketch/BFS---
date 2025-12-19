# examples/run_cross_solver.py 파일 상단 수정

import sys
import os

# --- 모듈 임포트 설정 (실행 환경에 맞게 경로 설정) ---
# 현재 파일의 부모 디렉토리 (프로젝트 루트 디렉토리)를 Python 경로에 추가
# 이 코드가 "refactored_cube - 복사본" 디렉토리를 찾게 합니다.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    # 이제 절대 경로 임포트 방식으로 모듈을 가져옵니다.
    # (프로젝트 구조에 따라 'refactored_cube' 같은 최상위 패키지 이름이 필요할 수 있습니다. 
    # 현재는 최상위 디렉토리를 바로 추가했으므로, 서브 디렉토리 이름을 사용합니다.)
    from core.cube_state import CubeState
    from core.move_engine import CubeMoveEngine
    from utils.scramble import generate_scramble
    from visualization.renderer import render_cube_flat
    from ai.bfs_solver import BFSSolver
    from ai.cube_ai_state import CubeAIState
    from core.constants import FACE_U, FACE_NAMES, DEFAULT_FACE_COLOR
except ImportError as e:
    # 디버깅을 돕기 위해 오류 메시지와 PATH를 출력
    print(f"Error during import: {e}")
    print(f"Current sys.path: {sys.path}")
    print("Please ensure your working directory is the project root or the path is set correctly.")
    sys.exit(1)

# ... main 함수는 그대로 유지 ...


def main():
    print("==============================================")
    print("🧭 BFS Cross Solver Demonstration (U-Face)")
    print("==============================================")

    # 1. 큐브 초기화 및 스크램블
    cube = CubeState.solved()
    engine = CubeMoveEngine(cube)
    
    # 20수 스크램블에서도 빠르게 크로스를 찾을 수 있어야 합니다.
    SCRAMBLE_LENGTH = 20
    MAX_BFS_DEPTH = None
    
    scramble = generate_scramble(length=SCRAMBLE_LENGTH) 
    print(f"\n[1] Generated Scramble (Length {len(scramble)}): {' '.join(scramble)}")
    engine.apply_sequence(scramble)
    
    print("\n[2] Initial State (After Scramble):")
    print(render_cube_flat(cube))

    color_name_by_code = {
        1: 'white',
        2: 'yellow',
        3: 'green',
        4: 'blue',
        5: 'orange',
        6: 'red',
    }

    def face_label(face: int) -> str:
        face_letter = FACE_NAMES[face]
        color_code = int(DEFAULT_FACE_COLOR[face])
        color_name = color_name_by_code.get(color_code, str(color_code))
        return f"{face_letter}({color_name})"

    # 3. 6가지 색상의 크로스를 모두 시도해서, 최단 해답을 선택 (동률이면 전부 출력)
    print(f"\n[3] Trying all 6 crosses (U/D/F/B/L/R) and picking the shortest (Max Depth: {MAX_BFS_DEPTH})...")
    
    # 탐색 시간을 측정하기 위해 현재 시간을 기록
    import time
    start_time = time.time()
    best_len, best = CubeAIState.find_best_cross_solutions(
        cube_state=cube,
        max_depth=MAX_BFS_DEPTH,
        include_white=True,
    )
    end_time = time.time()
    
    search_time = end_time - start_time
    print(f"\n[3] Search Complete (Time taken: {search_time:.4f} seconds)")

    if not best:
        print(f"\n[4] ❌ Failed to find any cross solution (max_depth={MAX_BFS_DEPTH}).")
        return

    # 최단수 동률이면 모두 출력
    print(f"\n[4] Best cross length: {best_len}")
    for face, solution in best:
        print(f"- Best Face: {face_label(face)} | Solution (len={len(solution)}): {' '.join(solution)}")

    # 5. 첫 번째(최단) 해답을 실제로 적용해서 눈으로 확인
    chosen_face, chosen_solution = best[0]
    solved_cube = cube.copy()
    CubeMoveEngine(solved_cube).apply_sequence(chosen_solution)

    print(f"\n[5] Final State After Applying First Best Solution (Face {face_label(chosen_face)}):")
    print(render_cube_flat(solved_cube))

    final_ai_state = CubeAIState.from_cube_state(solved_cube)
    ok = final_ai_state.is_cross_solved(chosen_face)
    print(f"\n[6] Cross Verification Result (Face {face_label(chosen_face)}): {ok}")
    print("✅ Success" if ok else "❌ Failure")


if __name__ == '__main__':
    # 큐브 상태, 무브 엔진, BFS 솔버, 크로스 검증 로직이 모두 준비되었으므로
    # 이 파일을 실행하여 최종 결과를 확인해 보십시오.
    main()